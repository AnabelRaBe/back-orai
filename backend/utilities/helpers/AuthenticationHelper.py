import json
from typing import Any, Optional

import requests
import aiohttp
from jose import jwt
from msal import ConfidentialClientApplication
from msal.token_cache import TokenCache
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

    def __str__(self) -> str:
        return self.error or ""


class AuthenticationHelper:
    scope: str = "https://graph.microsoft.com/.default"

    def __init__(
        self,
        use_authentication: bool,
        server_app_id: Optional[str] = None,
        server_app_secret: Optional[str] = None,
        client_app_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        require_access_control: bool = False,
    ):
        self.use_authentication = use_authentication
        self.server_app_id = server_app_id
        self.server_app_secret = server_app_secret
        self.client_app_id = client_app_id
        self.tenant_id = tenant_id
        self.authority = f"https://login.microsoftonline.com/{tenant_id}"
        self.valid_issuers = [
            f"https://sts.windows.net/{tenant_id}/",
            f"https://login.microsoftonline.com/{tenant_id}/v2.0",
        ]
        self.valid_audiences = [f"api://{server_app_id}", str(server_app_id)]
        self.key_url = f"{self.authority}/discovery/v2.0/keys"

        if self.use_authentication:
            self.require_access_control = require_access_control
            self.confidential_client = ConfidentialClientApplication(
                server_app_id, authority=self.authority, client_credential=server_app_secret, token_cache=TokenCache()
            )
        else:
            self.require_access_control = False

    def get_auth_setup_for_client(self) -> dict[str, Any]:
        return {
            "useLogin": self.use_authentication,  # Whether or not login elements are enabled on the UI
            "requireAccessControl": self.require_access_control,  # Whether or not access control is required to use the application
            "msalConfig": {
                "auth": {
                    "clientId": self.client_app_id,  # Client app id used for login
                    "authority": self.authority,  # Directory to use for login https://learn.microsoft.com/azure/active-directory/develop/msal-client-application-configuration#authority
                    "redirectUri": "/redirect",  # Points to window.location.origin. You must register this URI on Azure Portal/App Registration.
                    "postLogoutRedirectUri": "/",  # Indicates the page to navigate after logout.
                    "navigateToLoginRequestUrl": False,  # If "true", will navigate back to the original request location before processing the auth code response.
                },
                "cache": {
                    # Configures cache location. "sessionStorage" is more secure, but "localStorage" gives you SSO between tabs.
                    "cacheLocation": "localStorage",
                    # Set this to "true" if you are having issues on IE11 or Edge
                    "storeAuthStateInCookie": False,
                },
            },
            "loginRequest": {
                # Scopes you add here will be prompted for user consent during sign-in.
                # By default, MSAL.js will add OIDC scopes (openid, profile, email) to any login request.
                # For more information about OIDC scopes, visit:
                # https://docs.microsoft.com/azure/active-directory/develop/v2-permissions-and-consent#openid-connect-scopes
                "scopes": [".default"],
                # Uncomment the following line to cause a consent dialog to appear on every login
                # For more information, please visit https://learn.microsoft.com/azure/active-directory/develop/v2-oauth2-auth-code-flow#request-an-authorization-code
                # "prompt": "consent"
            },
            "tokenRequest": {
                "scopes": [f"api://{self.server_app_id}/access_as_user"],
            },
        }

    @staticmethod
    def get_token_auth_header(headers: dict) -> str:
        auth = headers.get("Authorization")
        if auth:
            parts = auth.split()

            if parts[0].lower() != "bearer":
                raise AuthError(error="Authorization header must start with Bearer", status_code=401)
            elif len(parts) == 1:
                raise AuthError(error="Token not found", status_code=401)
            elif len(parts) > 2:
                raise AuthError(error="Authorization header must be Bearer token", status_code=401)

            token = parts[1]
            return token
        
        token = headers.get("x-ms-token-aad-access-token")
        if token:
            return token

        raise AuthError(error="Authorization header is expected", status_code=401)

    @staticmethod
    async def list_groups(graph_resource_access_token: str) -> list[str]:
        headers = {"Authorization": "Bearer " + graph_resource_access_token}
        groups = []
        async with aiohttp.ClientSession(headers=headers) as session:
            resp_json = None
            resp_status = None
            async with session.get(url="https://graph.microsoft.com/v1.0/me/transitiveMemberOf?$select=id") as resp:
                resp_json = await resp.json()
                resp_status = resp.status
                if resp_status != 200:
                    raise AuthError(error=json.dumps(resp_json), status_code=resp_status)

            while resp_status == 200:
                value = resp_json["value"]
                for group in value:
                    groups.append(group["id"])
                next_link = resp_json.get("@odata.nextLink")
                if next_link:
                    async with session.get(url=next_link) as resp:
                        resp_json = await resp.json()
                        resp_status = resp.status
                else:
                    break
            if resp_status != 200:
                raise AuthError(error=json.dumps(resp_json), status_code=resp_status)
        return groups

    async def get_user_groups(self, token: str, user_id: str) -> list:
        graph_url = f"https://graph.microsoft.com/v1.0/users/{user_id}/getMemberGroups"

        headers = { 'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json', }
    
        data = { 'securityEnabledOnly': True }

        response = requests.post(graph_url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            groups = response.json()
            return groups['value']
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return []

    async def get_auth_claims_if_enabled(self, headers: dict) -> dict[str, Any]:
        if not self.use_authentication:
            return {}
        try:
            auth_token = AuthenticationHelper.get_token_auth_header(headers)
            await self.validate_access_token(auth_token)

            graph_resource_access_token = self.confidential_client.acquire_token_on_behalf_of(
                user_assertion=auth_token, scopes=["https://graph.microsoft.com/.default"]
            )
            if "error" in graph_resource_access_token:
                raise AuthError(error=str(graph_resource_access_token), status_code=401)

            id_token_claims = graph_resource_access_token["id_token_claims"]
            auth_claims = {"oid": id_token_claims["oid"], "groups": id_token_claims.get("groups", [])}

            missing_groups_claim = "groups" not in id_token_claims
            has_group_overage_claim = (
                missing_groups_claim
                and "_claim_names" in id_token_claims
                and "groups" in id_token_claims["_claim_names"]
            )
            if missing_groups_claim or has_group_overage_claim:
                auth_claims["groups"] = await AuthenticationHelper.list_groups(graph_resource_access_token)
            return auth_claims
        except AuthError as e:
            print("Exception getting authorization information - " + json.dumps(e.error))
            if self.require_access_control:
                raise
            return {}
        except Exception:
            print("Exception getting authorization information")
            if self.require_access_control:
                raise
            return {}

    async def validate_access_token(self, token: str):
        """
        Validate an access token is issued by Entra
        """
        jwks = None
        async for attempt in AsyncRetrying(
            retry=retry_if_exception_type(AuthError),
            wait=wait_random_exponential(min=15, max=60),
            stop=stop_after_attempt(5),
        ):
            with attempt:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url=self.key_url) as resp:
                        resp_status = resp.status
                        if resp_status in [500, 502, 503, 504]:
                            raise AuthError(
                                error=f"Failed to get keys info: {await resp.text()}", status_code=resp_status
                            )
                        jwks = await resp.json()

        if not jwks or "keys" not in jwks:
            raise AuthError({"code": "invalid_keys", "description": "Unable to get keys to validate auth token."}, 401)

        rsa_key = None
        issuer = None
        audience = None
        try:
            unverified_header = jwt.get_unverified_header(token)
            unverified_claims = jwt.get_unverified_claims(token)
            issuer = unverified_claims.get("iss")
            audience = unverified_claims.get("aud")
            for key in jwks["keys"]:
                if key["kid"] == unverified_header["kid"]:
                    rsa_key = {"kty": key["kty"], "kid": key["kid"], "use": key["use"], "n": key["n"], "e": key["e"]}
                    break
        except Exception as exc:
            raise AuthError(
                {"code": "invalid_header", "description": "Unable to parse authorization token."}, 401
            ) from exc
        if not rsa_key:
            raise AuthError({"code": "invalid_header", "description": "Unable to find appropriate key"}, 401)

        if issuer not in self.valid_issuers:
            raise AuthError(
                {"code": "invalid_header", "description": f"Issuer {issuer} not in {','.join(self.valid_issuers)}"}, 401
            )

        # if audience not in self.valid_audiences:
        #     raise AuthError(
        #         {
        #             "code": "invalid_header",
        #             "description": f"Audience {audience} not in {','.join(self.valid_audiences)}",
        #         },
        #         401,
        #     )

        try:
            jwt.decode(token, rsa_key, algorithms=["RS256"], audience=audience, issuer=issuer)
        except jwt.ExpiredSignatureError as jwt_expired_exc:
            raise AuthError({"code": "token_expired", "description": "token is expired"}, 401) from jwt_expired_exc
        except jwt.JWTClaimsError as jwt_claims_exc:
            raise AuthError(
                {"code": "invalid_claims", "description": "incorrect claims," "please check the audience and issuer"},
                401,
            ) from jwt_claims_exc
        except Exception as exc:
            raise AuthError(
                {"code": "invalid_header", "description": "Unable to parse authorization token."}, 401
            ) from exc

"""
This module checks that the user has access to use the rest of the endpoints.
"""
import os
from utilities.helpers.AuthenticationHelper import AuthError, AuthenticationHelper
import logging
from dotenv import load_dotenv
import azure.functions as func
import json
 
async def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Function to handle requests for user authentication.
    This function checks whether the user has access to use the endpoints by validating their access token and group membership. It ensures that the user belongs to the required groups defined in the environment variables.
    Args:
        req (func.HttpRequest): The HTTP request object containing the token ID, access token, and groups access.
    Returns:
        func.HttpResponse: An HTTP response indicating success or failure of the authentication process.
    """
    logging.info('Requested to start processing the Autentication.')

    load_dotenv(override=True)

    data = req.get_json()
    token_id = data['token_id']
    access_token = data['access_token']
    groups_access = data['groups_access']

    auth_helper = AuthenticationHelper(use_authentication = True,
                                        server_app_id = os.getenv(""),
                                        server_app_secret = os.getenv("AZURE_CLIENT_SECRET"),
                                        client_app_id = os.getenv("CLIENT_ID"),
                                        tenant_id = os.getenv("AZURE_TENANT_ID"))

    orai_groups = { "groups" :
                        {
                            os.getenv("ORAI_USER_GROUP_ID"): os.getenv("ORAI_USER_GROUP_NAME"),
                            os.getenv("ORAI_ADMIN_USER_GROUP_ID"): os.getenv("ORAI_ADMIN_USER_GROUP_NAME"),
                            os.getenv("ORAI_ADVANCE_USER_GROUP_ID"): os.getenv("ORAI_ADVANCE_USER_GROUP_NAME"),
                            os.getenv("ORAI_METRICS_GROUP_ID"): os.getenv("ORAI_METRICS_GROUP_NAME")            
                        }
                    }

    try:
        await auth_helper.validate_access_token(token_id)
        logging.info("Token validated.")
        try:
            user_groups = await auth_helper.list_groups(access_token)
            groups = []
            for group_id in user_groups:
                for k, v in orai_groups["groups"].items():
                    if k == group_id:
                        groups.append(v)
     
            groups_access_in_groups = False

            for group_access in groups_access:
                logging.info(f'Buscando grupo: {group_access}')
                if (group_access in groups) or (os.getenv("GROUP_NAME") in groups_access and len(groups) > 0):
                    groups_access_in_groups = True

            if groups_access_in_groups:
                logging.info(f"Orai group validated. \nBelong to: {groups}")
                return func.HttpResponse(f"Orai group validated. Belong to: {groups}", status_code=200)
            else:
                logging.info("Error: You don't belong to the right group")
                return func.HttpResponse("Error: You don't belong to the right group", status_code=403)

        except Exception as ex:
            logging.info(f"Error extracting user groups: {ex}")
            return func.HttpResponse(json.dumps({"Error extracting user groups:": str(ex)}), status_code=500, mimetype="application/json")

    except AuthError as e:
        logging.info(f"Error validating token: {e.status_code}; {e.error}")
        return func.HttpResponse(json.dumps({"Error validating token:": str(e.error)}), status_code=e.status_code, mimetype="application/json")
    
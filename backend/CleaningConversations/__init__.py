import logging
import datetime
import json, os, requests
import azure.functions as func
from ..utilities.common.PostgreSQL import PostgreSQL
from ..utilities.common.ValidationRequest import RequestCleaning
from dotenv import load_dotenv
import urllib.parse


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Requested to delete unsaved conversations from the previous day')

    load_dotenv()

    try:
        request_body = req.get_json()

        validated_body = RequestCleaning(**request_body)

        user_id = str(validated_body.user_id)
        access_token = validated_body.access_token
        token_id = validated_body.token_id
        groups_access = [os.getenv("GROUP_NAME")]

        params = {"token_id": token_id,
                "access_token": access_token,
                "groups_access": groups_access}

        backend_url = urllib.parse.urljoin(os.getenv('BACKEND_URL'), "/api/Authentication")
        response = requests.post(backend_url, json=params)

        if response.status_code == 200:
            try:
                now = datetime.datetime.now()
                yesterday = (now - datetime.timedelta(days=1))
                formatted_yesterday = yesterday.strftime("%Y-%m-%d %H:%M:%S.%f%z")
                postgresql = PostgreSQL()
                user_id = str(validated_body.user_id)
                postgresql.delete_data("conversations", f"user_id = '{user_id}' AND modified_at <= '{formatted_yesterday}' AND save_chat = 'False'")

                postgresql.close_connection()

                return func.HttpResponse(status_code=204)
            except Exception as e:
                logging.exception("Exception in SaveConversation")
                return func.HttpResponse(json.dumps({"Error": str(e)}), status_code=500, mimetype="application/json") 
        else:
            logging.info(f'Authentication error: {response.json()}. status_code: {response.status_code}')
            return func.HttpResponse(json.dumps(response.json()), status_code = response.status_code)
    
    except Exception as e:
        logging.exception("Exception in CleaningConversations")
        return func.HttpResponse(json.dumps({"Error": str(e)}), status_code=500, mimetype="application/json") 
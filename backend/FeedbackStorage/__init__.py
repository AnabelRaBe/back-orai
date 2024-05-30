"""
The feedback provided by the user about an answer given by the AI in relation to the question asked by the user is stored.
"""

import logging
import urllib.parse
import azure.functions as func
import requests
from dotenv import load_dotenv
import os
import json
from ..utilities.helpers.FeedbackHelper import Feedback


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    The feedback provided by the user about an answer given by the AI in relation to the question asked by the user is stored.
    Params:
        func.HttpResponse
    Returns:
        func.HttpResponse
    """
    logging.info('Requested to start processing FeedbackStorage')

    load_dotenv()

    data = req.get_json()
    access_token = data['access_token']
    token_id = data['token_id']
    user_id = data['user_id']
    name = data['name']
    feedback = data['feedback']
    question = data['question']
    answer = data['answer']
    citations = data['citations']
    conversation_id = data['conversation_id']
    config_llm = data['config_LLM']
    prompt = data['answering_prompt']

    groups_access = [os.getenv("GROUP_NAME")]

    params = {"token_id": token_id,
            "access_token": access_token,
            "groups_access": groups_access}

    backend_url = urllib.parse.urljoin(os.getenv('BACKEND_URL'), "/api/Authentication")

    try:
        response = requests.post(backend_url, json=params)

        if response.status_code == 200:

            try:
                feedback_object = Feedback(user_id=user_id,
                                            name=name,
                                            feedback=feedback,
                                            question=question,
                                            answer=answer,
                                            citations=citations,
                                            conversation_id=conversation_id,
                                            config_llm=config_llm,
                                            prompt=prompt
                                            )
                feedback_object.generate_json_feedback()
                return func.HttpResponse(status_code=204)

            except Exception as e:
                logging.exception("Exception in FeedbackStorage")
                return func.HttpResponse(json.dumps({"Error": str(e)}), status_code=500, mimetype="application/json")

        else:
            logging.info(f'Authentication error: {response.json()}. status_code: {response.status_code}')
            return func.HttpResponse(json.dumps(response.json()), status_code = response.status_code)

    except Exception as e:
        logging.exception(f"Response failed: {e}")
        return func.HttpResponse(json.dumps({"Error": str(e)}), status_code=500, mimetype="application/json")

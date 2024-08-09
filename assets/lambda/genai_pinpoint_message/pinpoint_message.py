"""
Lambda that prompts Pinpoint to send a message based on channel
"""

#########################
#   LIBRARIES & LOGGER
#########################

import json
# import logging
import os
import sys
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

from requests_toolbelt.multipart.encoder import MultipartEncoder
import requests

# Define credentials
myusername = 'stellario'
mypassword = 'Babushka1!'

"""
LOGGER = logging.Logger("Content-generation", level=logging.DEBUG)
HANDLER = logging.StreamHandler(sys.stdout)
HANDLER.setFormatter(logging.Formatter("%(levelname)s | %(name)s | %(message)s"))
LOGGER.addHandler(HANDLER)
"""

#########################
#        HELPER
#########################

PINPOINT_PROJECT_ID = os.environ["PINPOINT_PROJECT_ID"]
CHARSET = "UTF-8"
EMAIL_IDENTITY = os.environ["EMAIL_IDENTITY"]
SMS_IDENTITY = os.environ["SMS_IDENTITY"]

#########################
#        HANDLER
#########################

def lambda_handler(event, context):
    print("Entering pinpoint_message() Lambda")
    print(f"EMAIL_IDENTITY: {EMAIL_IDENTITY}")
    print(f"event: {event}")

    # Get the HTTP method from the event object
    http_method = event["requestContext"]["http"]["method"]

    # Check if the request is a POST request
    if http_method == "POST":
        # Get the Pinpoint project ID from the environment variable
        pinpoint_project_id = os.environ["PINPOINT_PROJECT_ID"]
        # parse event
        event = json.loads(event["body"])
        print(f"pinpoint_message() event: {event}")
        address = event["address"]
        channel = event["channel"]

        # FAS
        # Need to preface the SMS address with +1 or pinpoint SMS
        # will not work.
        if channel == "SMS":
            address = '+1' + address
        print(f"address: {address}")  

        message_subject = event["message-subject"]
        message_body_html = event["message-body-html"]
        message_body_text = event["message-body-text"]

        # Create a Pinpoint client
        client = boto3.client("pinpoint")
        
        message_request = {"Addresses":{address: {"ChannelType": channel}}}

        ## FAS
        ## Ensure that this Lambda has permission to access and use the SES Identity
        ## associated with EMAIL_IDENTITY.

        if channel == "EMAIL":
            message_request["MessageConfiguration"] = {
                "EmailMessage": {
                    "FromAddress": EMAIL_IDENTITY,
                    "SimpleEmail": {
                        "Subject": {"Charset": CHARSET, "Data": message_subject},
                        "HtmlPart": {"Charset": CHARSET, "Data": message_body_html},
                        "TextPart": {"Charset": CHARSET, "Data": message_body_text},
                    },
                }
            }
            print(f"email message_request: {message_request}")

        elif channel == "SMS":
            sms_config = {"Body": message_body_text, "MessageType": "PROMOTIONAL"}

            # Check if SMS_IDENTITY is provided, if it isn't use shared number pool
            if SMS_IDENTITY:
                sms_config["OriginationNumber"] = SMS_IDENTITY

            message_request["MessageConfiguration"] = {"SMSMessage": sms_config}
            print(f"sms message_request: {message_request}")

        else:
            return {
                "statusCode": 400,
                "body": "Unsupported channel type",
                "headers": {"Content-Type": "application/json"},
            }

        try:
            response = client.send_messages(ApplicationId=pinpoint_project_id, MessageRequest=message_request)
            print(f"response: {response}")

            # Return the response
            return {"statusCode": 200, "body": json.dumps(response), "headers": {"Content-Type": "application/json"}}

        except ClientError as e:
            # Handle any errors that occur
            print(e)
            return {
                "statusCode": 500,
                "body": f"An error occurred while sending the {channel} message",
                "headers": {"Content-Type": "application/json"},
            }
        
    else:
        # Return an error response for unsupported HTTP methods
        return {"statusCode": 400, "body": "Unsupported HTTP method", "headers": {"Content-Type": "application/json"}}
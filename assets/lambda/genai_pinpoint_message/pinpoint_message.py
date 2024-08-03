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

import c2m_add_credit
import c2m_check_job_status
import c2m_check_tracking
import c2m_create_job
import c2m_submit_job
import c2m_upload_address_list
import c2m_upload_document

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

def parse_custom_address(address: str):
    address_1, city, state, postal_code = address.split('%')
    address_object = {"address_1": address_1,
                      "city": city,
                      "state": state,
                      "postal_code": postal_code}
    print(address_object)
    return address_object

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

        elif channel == "CUSTOM":
            print("Channel is CUSTOM")
            print("In the pinpoint_message() Lambda")

            address_object = parse_custom_address(address)
            
            print('address_object')
            print(address_object)

            add_credit_return = c2m_add_credit.c2m_add_credit(billing_name = 'Awesome User',
                                               billing_address1 = '221B Baker St',
                                               billing_city = 'Springfield',
                                               billing_state = 'MO',
                                               billing_zip = '34567',
                                               billing_amount = '10',
                                               billing_number = '4111111111111111',
                                               billing_month = '12',
                                               billing_year = '2030',
                                               billing_cvv = '123',
                                               billing_cc_type = 'VI')

            print(add_credit_return)

            document_id = c2m_upload_document.c2m_upload_document(document_name = 'Test Document',
                                              document_class = 'Letter 8.5 x 11',
                                              document_type = 'application/odt',
                                              document_format = 'ODT')

            print(document_id)
            
                        
            print('address_object')
            print(address_object)

            address_list_id = c2m_upload_address_list.c2m_upload_address_list(address_list_name = 'My First List',
                                                      address_list_mapping_id = '1',
                                                      #first_name = 'Awesome',
                                                      #last_name = 'User',
                                                      organization = 'Justice League',
                                                      address_1 = address_object['address_1'],
                                                      city = address_object['city'],
                                                      state = address_object['state'],
                                                      postal_code = address_object['postal_code'],
                                                      country = 'USA')
            
            print(address_list_id)                        


            job_id = c2m_create_job.c2m_create_job(document_id = document_id,
                                    address_list_id = address_list_id)

            print(job_id)

            submit_job_return = c2m_submit_job.c2m_submit_job(billing_type = 'User Credit', job_id = job_id)
            print(submit_job_return)

            check_job_status_return = c2m_check_job_status.c2m_check_job_status(job_id = job_id)
            print(check_job_status_return)

            """
            check_tracking_return = c2m_check_tracking.c2m_check_tracking(tracking_type = 'IMB', job_id = job_id)
            print(check_tracking_return)
            """
            
            # Return the response
            return {"statusCode": 200, "body": json.dumps(check_job_status_return), "headers": {"Content-Type": "application/json"}}

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
"""
Lambda that prompts Pinpoint to send a message based on channel
"""

#########################
#   LIBRARIES & LOGGER
#########################

import json
#import logging
import os
import sys
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

import requests

# Define credentials
myusername = 'stellario'
mypassword = 'Babushka1!'

check_job_status_url    = "https://stage-rest.click2mail.com/molpro/jobs/"

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

def c2m_check_job_status(job_id: str = None):

  # Define the endpoint to use, including the jobId
  url = check_job_status_url + job_id 

  headers = {'user-agent': 'my-app/0.0.1'}

  # Make the GET call
  r = requests.get(url, headers=headers, auth=(myusername, mypassword))

  # Display the result - a success should return an HTTP status_code 201
  print(r.status_code)

  # Display the full XML returned.
  print(r.text)

  return r.text
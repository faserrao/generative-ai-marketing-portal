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

import requests
from io import BytesIO
import xml.etree.ElementTree as ET

# Define credentials
myusername = 'stellario'
mypassword = 'Babushka1!'

create_job_url          = "https://stage-rest.click2mail.com/molpro/jobs"

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


def c2m_create_job(document_class:    str = 'Letter 8.5 x 11',
                   layout:            str = 'Address on Separate Page',
                   production_time:   str = 'Next Day',
                   envelope:          str = '#10 Double Window',
                   color:             str = 'Black and White',
                   paper_type:        str = 'White 24#',
                   print_option:      str = 'Printing One side',
                   document_id:       str = None,
                   address_list_id:   str = None):

  # Define the endpoint to use
  url = create_job_url

  headers = {'user-agent': 'my-app/0.0.1'}

  # Build the dictionary of parameters to describe the job
  values = {'documentClass' : document_class,
            'layout'        : layout,
            'productionTime': production_time,
            'envelope'      : envelope,
            'color'         : color,
            'paperType'     : paper_type,
            'printOption'   : print_option,
            'documentId'    : document_id,
            'addressId'     : address_list_id}

  """
  values = {'documentClass' : 'Letter 8.5 x 11',
          'layout'        : 'Address on Separate Page',
          'productionTime': 'Next Day',
          'envelope'      : '#10 Double Window',
          'color'         : 'Black and White',
          'paperType'     : 'White 24#',
          'printOption'   : 'Printing One side',
          'documentId'    : document_id,
          'addressId'     : address_list_id}
  """

  print('values = ', values)

  # Make the POST call
  r = requests.post(url, data=values, headers=headers, auth=(myusername, mypassword))

  # Display the result - a success should return status_code 201
  print(r.status_code)

  # Display the full XML returned.
  print(r.text)

  xml_data = r.text

  # Parse the XML string
  root = ET.fromstring(xml_data)

  # Find the <id> element
  job_id = root.find('id').text

  # Print the document ID
  print(f"Job ID: {job_id}")

  return job_id
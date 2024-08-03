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
from io import BytesIO
import xml.etree.ElementTree as ET

import boto3
from botocore.exceptions import ClientError

from requests_toolbelt.multipart.encoder import MultipartEncoder
import requests
from odf.opendocument import OpenDocumentText
from odf.text import P

# Define credentials
myusername = 'stellario'
mypassword = 'Babushka1!'

upload_address_list_url = "https://stage-rest.click2mail.com/molpro/addressLists"

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

def string_to_odt_in_memory(content: str):
    # Create an OpenDocumentText document
    doc = OpenDocumentText()
    
    # Add a paragraph with the content
    paragraph = P(text=content)
    doc.text.addElement(paragraph)
    
    # Save the document to a BytesIO object
    odt_stream = BytesIO()
    doc.save(odt_stream)
    odt_stream.seek(0)  # Reset stream position to the beginning
    
    return odt_stream


###############################################
def c2m_upload_address_list(address_list_name :       str = '',
                            address_list_mapping_id:  str = '',
                            first_name:               str = 'first_name',
                            last_name:                str = 'last_name',
                            organization:             str = '',
                            address_1:                str = '',
                            address_2:                str = '',
                            address_3:                str = '',
                            city:                     str = '',
                            state:                    str = '',
                            postal_code:              str = '',
                            country:                  str = ''):

  # Define the endpoint to use
  url = upload_address_list_url

  headers = {
      "Accept": "application/xml",
      "Content-Type": "application/xml"
  }

  # Build the XML block containing the mappingId and the 
  # address information
  body = (
  '<addressList>'
    '<addressListName>' + address_list_name + '</addressListName>'
    '<addressMappingId>' + address_list_mapping_id + '</addressMappingId>'
    '<addresses>'
      '<address>'
          '<Firstname>' + first_name + '</Firstname>'
          '<Lastname>' + last_name + '</Lastname>'
          '<Organization>' + organization + '</Organization>'
          '<Address1>' + address_1 + '</Address1>'
          '<Address2>' + address_2 + '</Address2>'
          '<Address3>' + address_3 + '</Address3>'
          '<City>' + city + '</City>'
          '<State>' + state + '</State>'
          '<Postalcode>' + postal_code + '</Postalcode>'
          '<Country>' + country + '</Country>'
      '</address>'
    '</addresses>'
  '</addressList>'
  )

  print('body = ' + body)

  # Make the POST call
  r = requests.post(url, data=body, headers=headers, auth=(myusername, mypassword))

  # Display the result - a success should return status_code 201
  print(r.status_code)

  # Display the full XML returned.
  print(r.text)

  xml_data = r.text

  # Parse the XML string
  root = ET.fromstring(xml_data)

  # Find the <id> element
  address_list_id = root.find('id').text

  # Print the document ID
  print(f"Address List ID: {address_list_id}")

  return address_list_id
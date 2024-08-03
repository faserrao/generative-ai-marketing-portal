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

upload_doc_url          = "https://stage-rest.click2mail.com/molpro/documents"

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

def c2m_upload_document(document_format:  str = 'ODT',
                        document_name:    str = 'Test Letter ODT',
                        document_class:   str = 'Letter 8.5 x 11',
                        document_content: str = None,
                        document_type:    str = 'application/odt'):

  # Convert string to ODT in memory
  odt_stream = string_to_odt_in_memory(document_content)

  # Set up parameters for calling the endpoint
  # The API enforces strict HTTPS, so the payload
  # needs to be encoded
  # The 'file.pdf' value in the 'file' value tuple 
  # is a placeholder whose file extension must 
  # match the document type, but whose name does not matter
  mp_encoder = MultipartEncoder(
    fields={
      'documentFormat': document_format,
      'documentName': document_name,
      'documentClass': document_class,
      'file': ('file.odt', odt_stream, document_type)
    }
  )
  headers = {'user-agent': 'my-app/0.0.1','Content-Type': mp_encoder.content_type}

  # Make the POST call
  r = requests.post(upload_doc_url, auth=(myusername, mypassword), headers=headers, data=mp_encoder)

  # Display the result - a success should return status_code 201
  print(r.status_code)

  # Display the full XML returned. The new document_id will be in 
  # <document>
  #   <id>document_id</id>
  # <document>
  print(r.text)

  # The XML string
  #xml_data = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
  #<document>
  #    <id>750373</id>
  #    <status>0</status>
  #    <description>Success</description>
  #    <pages>6</pages>
  #</document>'''

  xml_data = r.text

  # Parse the XML string
  root = ET.fromstring(xml_data)

  # Find the <id> element
  document_id = root.find('id').text

  # Print the document ID
  print(f"Document ID: {document_id}")

  return document_id
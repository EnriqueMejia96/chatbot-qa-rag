from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv
load_dotenv()
language_key = os.getenv('LANGUAGE_KEY')
language_endpoint = os.getenv('LANGUAGE_ENDPOINT')

# Authenticate the client
def authenticate_client():
    ta_credential = AzureKeyCredential(language_key)
    text_analytics_client = TextAnalyticsClient(
        endpoint=language_endpoint, 
        credential=ta_credential)
    return text_analytics_client

# Function to check if PII data exists in the text
def security_pii_management(text):
    client = authenticate_client()
    try:
        response = client.recognize_pii_entities([text], language="es")
        result = response[0]  # Access the first (and only) document in the response
        if result.is_error:
            print(f"Error: {result.error.code}, Message: {result.error.message}")
            return False
        # Check if any entities are detected
        # print(result.entities)
        return len(result.entities) > 0
    except Exception as e:
        print(f"An exception occurred: {e}")
        return False
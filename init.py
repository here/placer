import os
from dotenv import load_dotenv

import requests
import pandas as pd

load_dotenv()

api_key = os.getenv('API_KEY')

def get_place_info(address, api_key):
# Base URL
  base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
# Parameters in a dictionary
  params = {
   "query": address,
   # "inputtype": "textquery",
   # "fields": "formatted_address,name,business_status,place_id",
   # "fields": "*",
   "key": api_key,
  }
# Send request and capture response
  response = requests.get(base_url, params=params)
# Check if the request was successful
  if response.status_code == 200:
    return response.json()
  else:
    return None

print("end of line")
print(api_key)

print(get_place_info("Cafe Tropical, 2900 Sunset Blvd, Los Angeles, CA 90026", api_key))
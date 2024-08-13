import os
from dotenv import load_dotenv

import requests
import json
import pandas as pd

load_dotenv()

api_key = os.getenv('API_KEY')
inputfile = 'input.xslx'
outputfile = 'output.json'

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

print("API Key")
print(api_key)

df = pd.read_excel('input.xlsx')
df['maps'] = 'empty'

searchdf = df[['Name','Address','City','St','Zip','maps']]

# name = "Cafe Tropical"
# address = "2900 Sunset Blvd, Los Angeles, CA 90026"

# name = searchtext[0]['Name']

for row in searchdf.itertuples():
  # print(row)
  searchrow = f"{row.Name}, {row.Address}, {row.City}, {row.St}, {row.Zip}"
  print(searchrow)

  if row.maps != 'empty':
      continue

  response = get_place_info(searchrow, api_key)

  df.at[row.Index,'maps'] = json.dumps(response)

  if row.Index > 10:
    break

print(df.head)

df.to_excel('./out.xlsx',engine="openpyxl")
#df.to_excel('./out.xlsx')

# print(places)
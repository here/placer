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

df = pd.read_excel('out.xlsx')
# df['maps'] = 'empty'

searchdf = df[['Name','Address','City','St','Zip','mapobj']]

# name = "Cafe Tropical"
# address = "2900 Sunset Blvd, Los Angeles, CA 90026"

# name = searchtext[0]['Name']

start = 42 # Start row number in excel
loops = 10
reqcount = 0
for i, row in enumerate(searchdf.itertuples()):
  if i+2 < start: # Add two for index to match excel sheet row number.  Adds header row and first result zero row.
    print(f"{i} continuing not yet {start}")
    continue
  # print(row)
  searchrow = f"{row.Name}, {row.Address}, {row.City}, {row.St}, {row.Zip}"
  print(searchrow)

  # Limit to specific state
  if row.St.casefold() != 'Or'.casefold():
    print(f"Oregon {row.St.casefold()} != {'Or'.casefold()} for {searchrow}")
    continue

  # If response data already exists in row.mapobj, skip row
  if not pd.isna(row.mapobj):
    print(f"mapobj pd.isna() as {row.mapobj} for {searchrow}")
    continue

  print(f"searching {searchrow}")
  response = get_place_info(searchrow, api_key)
  print(response)
  reqcount += 1

  df.at[row.Index,'mapresults'] = len(response['results'])
  
  if len(response['results']) == 1:
    df.at[row.Index,'mapstatus'] = response['results'][0]['business_status']
    df.at[row.Index,'mapname'] = response['results'][0]['name']
    df.at[row.Index,'mapaddress'] = response['results'][0]['formatted_address']
    df.at[row.Index,'maprating'] = response['results'][0]['rating']
    df.at[row.Index,'mapratecount'] = response['results'][0]['user_ratings_total']
    df.at[row.Index,'maptypes'] = json.dumps(response['results'][0]['types'])
  
  df.at[row.Index,'mapobj'] = response
  df.at[row.Index,'mapjson'] = json.dumps(response)

  if reqcount >= loops:
    break

  # if i >= loops-1:
  #   break

print(df.head)

df.to_excel('./new.xlsx',engine="openpyxl")
#df.to_excel('./out.xlsx')

# print(places)
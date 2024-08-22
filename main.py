import os
from dotenv import load_dotenv

import requests
import json
import pandas as pd

load_dotenv()

api_key = os.getenv('API_KEY')
api_loops = os.getenv('API_LOOPS')
states_allow = os.getenv('STATES_ALLOW')
inputfile = 'out.xlsx'

def get_place_info(address, api_key):
  base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
  # Parameters in a dictionary
  params = {
   "query": address,
   "key": api_key,
  }
  # Send request and capture response
  response = requests.get(base_url, params=params)
  # Check if the request was successful
  if response.status_code == 200:
    return response.json()
  else:
    return None

print(f"API Key {api_key}")

# Read in dataframe as df from excel using pandas as pd
df = pd.read_excel(inputfile)

searchdf = df[['Name','Address','City','St','Zip','mapobj']]

# Placeholder name and address
# name = "Cafe Tropical"
# address = "2900 Sunset Blvd, Los Angeles, CA 90026"

start = 0 # Start row number in excel
loops = int(api_loops)
reqcount = 0
for i, row in enumerate(searchdf.itertuples()):
  if i+2 < start: # Add two for index to match excel sheet row number.  Adds header row and first result zero row.
    print(f"{i} continuing not yet {start}")
    continue

  searchrow = f"{row.Name}, {row.Address}, {row.City}, {row.St}, {row.Zip}"
  # print(searchrow)

  # if state not in allowlist restart loop with continue
  if row.St.casefold() not in ['or','id','wa']:
    # print(f"State not allowed {row.St.casefold()}")
    continue

  # If data exists in row.mapobj restart loop with continue
  if not pd.isna(row.mapobj):
    print(f"existing data, mapobj is not pd.isna(), {row.St}, {row.Name}")
    continue

  print(f"searching {searchrow}")
  response = get_place_info(searchrow, api_key)
  print(response)
  reqcount += 1

  df.at[row.Index,'mapresults'] = len(response['results'])
  
  # Responses with exactly one result are more reliable for breaking out data
  if len(response['results']) == 1:
    df.at[row.Index,'mapstatus'] = response['results'][0].get('business_status')
    df.at[row.Index,'mapname'] = response['results'][0].get('name')
    response_address = response['results'][0].get('formatted_address')
    address_parts = response_address.split(',')
    if len(address_parts) == 4:
      df.at[row.Index,'mapstreet'] = address_parts[0]
      df.at[row.Index,'mapcity'] = address_parts[1].strip()
      df.at[row.Index,'mapstate'] = address_parts[2].split()[0].strip()
      df.at[row.Index,'mapzip'] = address_parts[2].split()[1].strip()
    else:
      print('Address split unexpected {address_parts}')
    df.at[row.Index,'mapaddress'] = response_address
    df.at[row.Index,'maprating'] = response['results'][0].get('rating')
    df.at[row.Index,'mapratecount'] = response['results'][0].get('user_ratings_total')
    df.at[row.Index,'maptypes'] = json.dumps(response['results'][0].get('types'))
  
  # Store full response python object and json for future use
  df.at[row.Index,'mapobj'] = response
  df.at[row.Index,'mapjson'] = json.dumps(response)

  if reqcount >= loops:
    break

  # if i >= loops-1:
  #   break

print(df.head)

# df.to_excel('./new.xlsx',engine="openpyxl")
# df.to_excel('./out.xlsx') # Permissions error to overwrite existing file
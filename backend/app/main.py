from fastapi import FastAPI, HTTPException, Query
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime
import pandas as pd
from haversine import haversine

from .mymodules.csv_cleaning import cleancsv1

import json
import requests
import os
import subprocess

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Your Backend is running :)"}

@app.on_event("startup")
async def startup_event():
    print("Your Backend is running: 🌈")

# Google API key
GOOGLE_API_KEY = "AIzaSyATC1fSYrOd7mQufuvHCOZX2CdXptZNvas"  # Replace with your actual API key

def get_coordinates(address):
    """
    Convert an address to geographic coordinates using Google's Geocoding API.
    """
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": GOOGLE_API_KEY}
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # This will raise an error for non-200 responses
        data = response.json()
        if data['status'] != 'OK':
            print(f"Error in Geocoding API response: {data['status']}")
            return None, None
        location = data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Geocoding API: {e}")
        return None, None

# def is_location_in_piemonte(lat, lng):
#         """
#         Check if given latitude and longitude are in the Piemonte region using Google's Reverse Geocoding API.
#         """
#         reverse_geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
#         params = {
#             "latlng": f"{lat},{lng}",
#             "key": GOOGLE_API_KEY
#         }
#         try:
#             response = requests.get(reverse_geocode_url, params=params)
#             response.raise_for_status()
#             data = response.json()
            
#             if data['status'] != 'OK':
#                 print(f"Error in Reverse Geocoding API response: {data['status']}")
#                 return False

#             # Check if any of the returned results are in the Piemonte region
#             for result in data['results']:
#                 if any('Piemonte' in component['long_name'] for component in result['address_components']):
#                     return True

#             return False
#         except requests.exceptions.RequestException as e:
#             print(f"Error connecting to Reverse Geocoding API: {e}")
#             return False

@app.get('/cleaned_csv_show')
async def read_and_return_cleaned_csv(
    bagni: str = Query(None), 
    camere: str = Query(None), 
    letti: str = Query(None), 
    provincia: str = Query(None), 
    comune: str = Query(None), 
    location: str = Query(None), 
    range_km: float = Query(None)
):
    # CSV file paths
    regpie_csv_path = 'app/regpie-RifugiOpenDa_2296-all.csv'
    shelters_csv_path = 'app/mountain_shelters.csv'
    scrape_script_path = 'app/mymodules/scrape.py'

    # Check if mountain_shelters.csv exists, otherwise run scrape.py
    if not os.path.exists(shelters_csv_path):
        print("Mountain shelters file not found. Running scrape.py to generate it.")
        subprocess.run(['python', scrape_script_path], check=True)

    # Define the path for merged_data.csv
    merged_data_csv_path = os.path.join(os.path.dirname(shelters_csv_path), 'merged_data.csv')

    # Check if merged_data.csv exists, otherwise run cleancsv1
    if not os.path.exists(merged_data_csv_path):
        print("Merged data file not found. Running cleancsv1 to generate it.")
        cleancsv1(regpie_csv_path, shelters_csv_path)

    # After ensuring merged_data.csv exists, load and return its contents
    try:
        cleaned_df = pd.read_csv(merged_data_csv_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading merged data: {str(e)}")
        
    # Get user coordinates
    user_lat, user_lng = None, None
    if location:
        user_lat, user_lng = get_coordinates(location)
        if user_lat is None or user_lng is None:
            print("Invalid location or unable to get coordinates.")
            raise HTTPException(status_code=400, detail="Invalid location")
        
        # if not is_location_in_piemonte(user_lat, user_lng):
        #     print("Location is not in Piemonte.")
        #     raise HTTPException(status_code=400, detail="Location is not in Piemonte")
        
        print(f"User coordinates: Latitude = {user_lat}, Longitude = {user_lng}")
    else: 
        user_lat, user_lng = None, None
    # Convert the DataFrame to a dictionary for processing
    cleaned_data = cleaned_df.to_dict(orient='records')

    # Check if any filter is set
    is_any_filter_set = any([
        bagni, camere, letti, provincia, comune, location, range_km is not None
    ])

    if not is_any_filter_set:
        # If no filters are set, return all data
        return JSONResponse(content=cleaned_data)

    # Apply filters
    filtered_data = []
    for item in cleaned_data:
        if bagni and str(item.get('BAGNI', '')) != bagni:
            continue
        if camere and str(item.get('CAMERE', '')) != camere:
            continue
        if letti and str(item.get('LETTI', '')) != letti:
            continue
        if provincia and item.get('PROVINCIA', '').lower() != provincia.lower():
            continue
        if comune and item.get('COMUNE', '').lower() != comune.lower():
            continue

         # Location-based filtering
        if user_lat is not None and user_lng is not None and range_km is not None:
            if 'Latitude' in item and 'Longitude' in item:
                item_lat, item_lng = item['Latitude'], item['Longitude']
                distance = haversine((user_lat, user_lng), (item_lat, item_lng))
                print(f"Distance from {item['DENOMINAZIONE']} to user location: {distance} km")

                if distance <= range_km:
                    item['Distance'] = f"{distance:.2f} km"
                    filtered_data.append(item)
            continue

        filtered_data.append(item)
        
    return JSONResponse(content=filtered_data)
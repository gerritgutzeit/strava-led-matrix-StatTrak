#!/usr/bin/python
# -*- coding:utf-8 -*-

import requests
import urllib3
import credentials as auth
import traceback

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_strava_token():
    """Get a fresh Strava access token using refresh token."""
    auth_url = "https://www.strava.com/oauth/token"
    payload = {
        'client_id': auth.STRAVA_CLIENT_ID,
        'client_secret': auth.STRAVA_CLIENT_SECRET,
        'refresh_token': auth.STRAVA_REFRESH_TOKEN,
        'grant_type': 'refresh_token'
    }
    
    try:
        res = requests.post(auth_url, data=payload, verify=False)
        return res.json()['access_token']
    except Exception as e:
        print(f'Error getting access token: {e}')
        return None

def get_athlete_gear():
    """Get all gear associated with the authenticated athlete."""
    access_token = get_strava_token()
    if not access_token:
        return None
        
    # Use the detailed athlete endpoint
    athlete_url = "https://www.strava.com/api/v3/athlete"
    activities_url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    try:
        print("Fetching athlete data...")
        response = requests.get(athlete_url, headers=headers)
        if response.status_code != 200:
            print(f"Error: API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
        athlete_data = response.json()
        
        # Fetch recent activities to get gear IDs
        print("Fetching recent activities...")
        response = requests.get(activities_url, headers=headers, params={'per_page': 200})
        if response.status_code != 200:
            print(f"Error: API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
        activities = response.json()
        
        # Extract unique gear IDs from activities
        gear_ids = set()
        for activity in activities:
            if 'gear_id' in activity and activity['gear_id']:
                gear_ids.add(activity['gear_id'])
                
        if not gear_ids:
            print("No gear IDs found in recent activities")
            return None
            
        print(f"Found gear IDs: {gear_ids}")
            
        # Get detailed information for each piece of gear
        gear_list = []
        for gear_id in gear_ids:
            gear_data = get_gear_info(gear_id)
            if gear_data:
                gear_list.append(gear_data)
                
        return gear_list
    except Exception as e:
        print(f'Error getting athlete gear: {e}')
        print(f'Full error: {traceback.format_exc()}')
        return None

def get_gear_info(gear_id):
    """Get information about specific Strava gear."""
    access_token = get_strava_token()
    if not access_token:
        return None
        
    gear_url = f"https://www.strava.com/api/v3/gear/{gear_id}"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    try:
        response = requests.get(gear_url, headers=headers)
        gear_data = response.json()
        return gear_data
    except Exception as e:
        print(f'Error getting gear info: {e}')
        return None

def display_gear_info(gear_data):
    """Display gear information in a formatted way."""
    if not gear_data:
        print("No gear data available.")
        return
        
    print("\n=== Strava Gear Information ===")
    print(f"ID: {gear_data.get('id', 'N/A')}")
    print(f"Name: {gear_data.get('name', 'N/A')}")
    print(f"Brand: {gear_data.get('brand_name', 'N/A')}")
    print(f"Model: {gear_data.get('model_name', 'N/A')}")
    print(f"Distance: {gear_data.get('distance')/1000:.1f} km")
    if gear_data.get('retired'):
        print("Status: Retired")
    else:
        print("Status: Active")
    print("============================\n")

def main():
    # Get all athlete gear
    gear_list = get_athlete_gear()
    
    if gear_list:
        print("Found", len(gear_list), "pieces of gear:")
        for gear in gear_list:
            display_gear_info(gear)
    else:
        print("No gear found or error occurred.")

if __name__ == "__main__":
    main() 
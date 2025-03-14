#!/usr/bin/python
# -*- coding:utf-8 -*-

import requests
import urllib3
import credentials as auth

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_gear_distance(gear_id="b14697016"):
    """Get the distance for a specific piece of Strava gear."""
    # Strava API URLs
    auth_url = "https://www.strava.com/oauth/token"
    gear_url = f"https://www.strava.com/api/v3/gear/{gear_id}"

    # Get access token
    payload = {
        'client_id': auth.StravaCredentials['client_id'],
        'client_secret': auth.StravaCredentials['client_secret'],
        'refresh_token': auth.StravaCredentials['refresh_token'],
        'grant_type': 'refresh_token'
    }

    try:
        print('Requesting Token...')
        res = requests.post(auth_url, data=payload, verify=False)
        access_token = res.json()['access_token']
        
        # Get gear data
        header = {'Authorization': f'Bearer {access_token}'}
        gear_data = requests.get(gear_url, headers=header).json()
        
        print("\n=== Gear Information ===")
        print(f"Gear ID: {gear_id}")
        print(f"Name: {gear_data.get('name', 'N/A')}")
        
        # Get distance in kilometers
        distance_km = gear_data.get('distance', 0) / 1000
        print(f"Total Distance: {distance_km:.1f} km")
        
        return distance_km
        
    except Exception as e:
        print(f'Error: {e}')
        return None

if __name__ == "__main__":
    get_gear_distance() 
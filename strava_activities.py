#!/usr/bin/python
# -*- coding:utf-8 -*-

import requests
import urllib3
import credentials as auth
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_strava_token() -> Optional[str]:
    """Get a fresh Strava access token using refresh token."""
    auth_url = "https://www.strava.com/oauth/token"
    payload = {
        'client_id': auth.StravaCredentials['client_id'],
        'client_secret': auth.StravaCredentials['client_secret'],
        'refresh_token': auth.StravaCredentials['refresh_token'],
        'grant_type': 'refresh_token'
    }
    
    try:
        print('Requesting Token...\n')
        res = requests.post(auth_url, data=payload, verify=False)
        res.raise_for_status()
        token_data = res.json()
        return token_data['access_token']
    except Exception as e:
        print(f'Error getting access token: {e}')
        return None

def get_activity_details(activity_id: int, access_token: str) -> Optional[Dict[str, Any]]:
    """Get detailed activity data including streams."""
    headers = {'Authorization': f'Bearer {access_token}'}
    
    try:
        # Get detailed activity data
        detailed_url = f"https://www.strava.com/api/v3/activities/{activity_id}"
        params = {
            'include_all_efforts': True
        }
        
        detailed_response = requests.get(detailed_url, headers=headers, params=params)
        detailed_response.raise_for_status()
        detailed_activity = detailed_response.json()
        
        print(f"\nDebug: Raw activity response for {activity_id}:")
        print(f"athlete_count: {detailed_activity.get('athlete_count')}")
        print(f"total_athlete_count: {detailed_activity.get('total_athlete_count')}")
        print(f"athlete_pairs: {detailed_activity.get('athlete_pairs')}")
        print(f"other_athlete_count: {detailed_activity.get('other_athlete_count')}")
        
        # Get activity streams
        streams_url = f"https://www.strava.com/api/v3/activities/{activity_id}/streams"
        streams_params = {
            'keys': 'time,heartrate,watts,velocity_smooth,cadence,temp',
            'key_by_type': True
        }
        
        streams_response = requests.get(streams_url, headers=headers, params=streams_params)
        streams_response.raise_for_status()
        streams = streams_response.json()
        
        # Format the activity data
        formatted_activity = {
            'id': detailed_activity['id'],
            'name': detailed_activity['name'],
            'date': datetime.strptime(detailed_activity['start_date_local'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S'),
            'type': detailed_activity['type'],
            'distance': round(detailed_activity['distance'] / 1000, 2),  # km
            'moving_time': detailed_activity['moving_time'],  # seconds
            'elapsed_time': detailed_activity['elapsed_time'],  # seconds
            'average_speed': round(detailed_activity['average_speed'] * 3.6, 2),  # convert m/s to km/h
            'max_speed': round(detailed_activity['max_speed'] * 3.6, 2),  # convert m/s to km/h
            'elevation_gain': detailed_activity['total_elevation_gain'],  # meters
            'average_watts': detailed_activity.get('average_watts'),
            'max_watts': detailed_activity.get('max_watts'),
            'weighted_average_watts': detailed_activity.get('weighted_average_watts'),
            'kilojoules': detailed_activity.get('kilojoules'),
            'average_heartrate': detailed_activity.get('average_heartrate'),
            'max_heartrate': detailed_activity.get('max_heartrate'),
            'average_cadence': detailed_activity.get('average_cadence'),
            'average_temp': detailed_activity.get('average_temp'),
            'gear': detailed_activity.get('gear', {}).get('name'),
            'gear_id': detailed_activity.get('gear', {}).get('id'),
            'device_name': detailed_activity.get('device_name'),
            'achievement_count': detailed_activity.get('achievement_count'),
            'kudos_count': detailed_activity.get('kudos_count'),
            'athlete_count': detailed_activity.get('athlete_count', 0),
            'total_athlete_count': detailed_activity.get('total_athlete_count', 0),
            'other_athlete_count': detailed_activity.get('other_athlete_count', 0),
            'athlete_pairs': detailed_activity.get('athlete_pairs', []),
            'other_athletes': detailed_activity.get('other_athletes', []),
            'athlete': {
                'id': detailed_activity.get('athlete', {}).get('id'),
                'firstname': detailed_activity.get('athlete', {}).get('firstname', ''),
                'lastname': detailed_activity.get('athlete', {}).get('lastname', ''),
                'username': detailed_activity.get('athlete', {}).get('username', 'unknown')
            },
            'streams': streams
        }
        
        return formatted_activity
        
    except Exception as e:
        print(f'Error fetching activity details: {e}')
        return None

def get_companion_activities(activity_id: int, access_token: str) -> List[Dict[str, Any]]:
    """Get activities from companions that match the given activity."""
    headers = {'Authorization': f'Bearer {access_token}'}
    companion_activities = []
    
    try:
        # First get the original activity to find companions
        detailed_url = f"https://www.strava.com/api/v3/activities/{activity_id}"
        response = requests.get(detailed_url, headers=headers)
        response.raise_for_status()
        activity = response.json()
        
        print(f"\nDebug: Activity response data:")
        print(f"athlete_count: {activity.get('athlete_count')}")
        print(f"total_athlete_count: {activity.get('total_athlete_count')}")
        print(f"athlete_pairs: {activity.get('athlete_pairs')}")
        print(f"other_athlete_count: {activity.get('other_athlete_count')}")
        
        # If there are companion athletes
        athlete_count = activity.get('athlete_count', 0)
        if athlete_count > 1:
            print(f"\nFound {athlete_count - 1} companion(s). Fetching their activities...")
            
            # Get the start time window to search for companion activities
            activity_start = datetime.fromisoformat(activity['start_date'])
            time_window = timedelta(minutes=5)  # Look for activities starting within 5 minutes
            
            # Try different fields that might contain companion data
            companion_athletes = (
                activity.get('athlete_pairs', []) or 
                activity.get('other_athletes', []) or 
                activity.get('athletes', [])
            )
            
            if not companion_athletes:
                print("No companion athlete data found in the activity")
                return []
                
            print(f"Found {len(companion_athletes)} companion athletes in the data")
            
            # For each companion athlete
            for athlete in companion_athletes:
                athlete_id = athlete.get('id')
                if athlete_id:
                    print(f"Fetching activities for athlete {athlete_id}...")
                    # Search for activities from this athlete around the same time
                    athlete_activities_url = f"https://www.strava.com/api/v3/athletes/{athlete_id}/activities"
                    params = {
                        'after': int((activity_start - time_window).timestamp()),
                        'before': int((activity_start + time_window).timestamp()),
                        'per_page': 5
                    }
                    
                    response = requests.get(athlete_activities_url, headers=headers)
                    if response.status_code == 200:
                        athlete_activities = response.json()
                        print(f"Found {len(athlete_activities)} activities for athlete {athlete_id}")
                        
                        # Find matching activity (similar start time)
                        for athlete_activity in athlete_activities:
                            athlete_start = datetime.fromisoformat(athlete_activity['start_date'])
                            if abs((athlete_start - activity_start).total_seconds()) <= 300:  # Within 5 minutes
                                # Get detailed activity data
                                detailed_activity = get_activity_details(athlete_activity['id'], access_token)
                                if detailed_activity:
                                    companion_activities.append(detailed_activity)
                                    print(f"Found matching activity for {athlete.get('firstname', 'Unknown')} {athlete.get('lastname', '')}")
                                break
                    else:
                        print(f"Could not fetch activities for athlete {athlete_id} (Status: {response.status_code})")
                        if response.status_code == 404:
                            print("This might be due to privacy settings or the athlete not being a connection")
    
    except Exception as e:
        print(f'Error fetching companion activities: {e}')
        print(f'Response content: {response.text if 'response' in locals() else "No response"}')
    
    return companion_activities

def get_most_recent_activity(token: str) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
    """Get the most recent activity over 20km and any companion activities."""
    # Get recent activities
    activities_url = "https://www.strava.com/api/v3/activities"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"per_page": 10}  # Fetch last 10 activities to find one over 20km
    
    try:
        response = requests.get(activities_url, headers=headers, params=params)
        response.raise_for_status()
        activities = response.json()
        print(f"\nFound {len(activities)} recent activities")
    except Exception as e:
        print(f"Error fetching activities: {e}")
        return None, []
    
    # Find most recent activity over 20km
    activity = None
    for act in activities:
        if act['distance'] >= 20000:  # 20km in meters
            activity = act
            print(f"\nFound activity over 20km: {act['name']}")
            print(f"Initial activity data:")
            print(f"- ID: {act['id']}")
            print(f"- Distance: {act['distance'] / 1000:.2f} km")
            print(f"- Athlete count: {act.get('athlete_count', 0)}")
            print(f"- Total athlete count: {act.get('total_athlete_count', 0)}")
            print(f"- Other athlete count: {act.get('other_athlete_count', 0)}")
            break
    
    if not activity:
        print("No activities found over 20km")
        return None, []
    
    # Get detailed activity data
    activity_id = activity['id']
    print(f"\nFetching detailed data for activity {activity_id}...")
    
    try:
        # Get detailed activity data using get_activity_details
        formatted_activity = get_activity_details(activity_id, token)
        if not formatted_activity:
            print("Failed to get detailed activity data")
            return None, []
            
        # Debug info about companions
        print(f"\nDetailed activity data received:")
        print(f"- Athlete count: {formatted_activity.get('athlete_count', 0)}")
        print(f"- Total athlete count: {formatted_activity.get('total_athlete_count', 0)}")
        print(f"- Other athlete count: {formatted_activity.get('other_athlete_count', 0)}")
        print(f"- Athlete pairs: {formatted_activity.get('athlete_pairs', [])}")
        print(f"- Other athletes: {formatted_activity.get('other_athletes', [])}")
        
        # Get companion activities using the dedicated function
        companion_activities = get_companion_activities(activity_id, token)
        print(f"\nFound {len(companion_activities)} companion activities")
        
        return formatted_activity, companion_activities
        
    except Exception as e:
        print(f"Error in get_most_recent_activity: {e}")
        return None, []

def format_time(seconds: int) -> str:
    """Format seconds into HH:MM:SS."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def print_activity(activity: Dict[str, Any]):
    """Print formatted activity information."""
    print("\n=== Activity Information ===")
    print(f"Name: {activity.get('name', 'N/A')}")
    print(f"Date: {activity.get('date', 'N/A')}")
    print(f"Type: {activity.get('type', 'N/A')}")
    print(f"Distance: {activity.get('distance', 'N/A')} km")
    print(f"Moving Time: {format_time(activity.get('moving_time', 0))}")
    print(f"Elapsed Time: {format_time(activity.get('elapsed_time', 0))}")
    print(f"Average Speed: {activity.get('average_speed', 'N/A')} km/h")
    print(f"Max Speed: {activity.get('max_speed', 'N/A')} km/h")
    print(f"Elevation Gain: {activity.get('total_elevation_gain', 'N/A')} m")
    
    if activity.get('average_watts'):
        print(f"\n=== Power Data ===")
        print(f"Average Power: {activity['average_watts']} W")
        if activity.get('weighted_average_watts'):
            print(f"Weighted Average Power: {activity['weighted_average_watts']} W")
        if activity.get('max_watts'):
            print(f"Max Power: {activity['max_watts']} W")
        if activity.get('kilojoules'):
            print(f"Work: {activity['kilojoules']} kJ")
            
    if activity.get('average_heartrate'):
        print(f"\n=== Heart Rate Data ===")
        print(f"Average Heart Rate: {activity['average_heartrate']} bpm")
        if activity.get('max_heartrate'):
            print(f"Max Heart Rate: {activity['max_heartrate']} bpm")
            
    if activity.get('average_cadence'):
        print(f"\n=== Additional Data ===")
        print(f"Average Cadence: {activity['average_cadence']} rpm")
    if activity.get('average_temp'):
        print(f"Average Temperature: {activity['average_temp']}°C")
        
    if activity.get('gear', {}).get('name'):
        print(f"\nGear: {activity['gear']['name']} (ID: {activity['gear']['id']})")
    if activity.get('device_name'):
        print(f"Device: {activity['device_name']}")
        
    print(f"\nAchievements: {activity.get('achievement_count', 0)}")
    print(f"Kudos: {activity.get('kudos_count', 0)}")
    
    # Print time series data if available
    streams = activity.get('streams', {})
    if streams:
        print("\n=== Time Series Data ===")
        print("Time(s) | HR(bpm) | Power(W) | Speed(km/h) | Cadence(rpm) | Temp(°C)")
        print("-" * 65)
        
        time_data = streams.get('time', {}).get('data', [])
        hr_data = streams.get('heartrate', {}).get('data', [None] * len(time_data))
        power_data = streams.get('watts', {}).get('data', [None] * len(time_data))
        speed_data = streams.get('velocity_smooth', {}).get('data', [None] * len(time_data))
        cadence_data = streams.get('cadence', {}).get('data', [None] * len(time_data))
        temp_data = streams.get('temp', {}).get('data', [None] * len(time_data))
        
        # Print first 5 and last 5 data points
        for i in range(min(5, len(time_data))):
            speed = round(speed_data[i] * 3.6, 1) if speed_data[i] is not None else None
            print(f"{time_data[i]:6d} | {hr_data[i] or '-':7} | {power_data[i] or '-':7} | {speed or '-':10} | {cadence_data[i] or '-':11} | {temp_data[i] or '-':7}")
            
        if len(time_data) > 10:
            print("..." + " " * 62)
            
        for i in range(max(5, len(time_data)-5), len(time_data)):
            speed = round(speed_data[i] * 3.6, 1) if speed_data[i] is not None else None
            print(f"{time_data[i]:6d} | {hr_data[i] or '-':7} | {power_data[i] or '-':7} | {speed or '-':10} | {cadence_data[i] or '-':11} | {temp_data[i] or '-':7}")
            
    print("============================")

def print_activity_comparison(main_activity: Dict[str, Any], companion_activities: List[Dict[str, Any]]):
    """Print activity data with companion comparisons."""
    print("\n=== Your Activity ===")
    print_activity(main_activity)
    
    if not companion_activities:
        print("\nNo companion activities found for this ride.")
        return
        
    for companion in companion_activities:
        print(f"\n=== {companion.get('athlete', {}).get('firstname', 'Unknown')} {companion.get('athlete', {}).get('lastname', '')}\'s Activity ===")
        print_activity(companion)
        
        # Print comparison
        print("\n=== Performance Comparison ===")
        print(f"Distance: You: {main_activity.get('distance', 'N/A'):.1f} km vs {companion.get('athlete', {}).get('firstname', 'Unknown')}: {companion.get('distance', 'N/A'):.1f} km")
        print(f"Moving Time: You: {format_time(main_activity.get('moving_time', 0))} vs {companion.get('athlete', {}).get('firstname', 'Unknown')}: {format_time(companion.get('moving_time', 0))}")
        print(f"Average Speed: You: {main_activity.get('average_speed', 'N/A'):.1f} km/h vs {companion.get('athlete', {}).get('firstname', 'Unknown')}: {companion.get('average_speed', 'N/A'):.1f} km/h")
        
        if main_activity.get('average_watts') and companion.get('average_watts'):
            print(f"Average Power: You: {main_activity['average_watts']:.1f} W vs {companion.get('athlete', {}).get('firstname', 'Unknown')}: {companion['average_watts']:.1f} W")
            
        if main_activity.get('average_heartrate') and companion.get('average_heartrate'):
            print(f"Average Heart Rate: You: {main_activity['average_heartrate']:.1f} bpm vs {companion.get('athlete', {}).get('firstname', 'Unknown')}: {companion['average_heartrate']:.1f} bpm")
            
        print("============================")

def main():
    """Main function to fetch and display activity data."""
    token = get_strava_token()
    if not token:
        print("Failed to get token")
        return
        
    activity, companion_activities = get_most_recent_activity(token)
    if not activity:
        print("No activities found")
        return
        
    print_activity_comparison(activity, companion_activities)

if __name__ == "__main__":
    main() 
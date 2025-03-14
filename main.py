import urequests as requests
import network
import time
import json
import gc
import machine
from machine import Pin
import credentials as creds

# Initialize status LED (built-in LED on D1 Mini)
led = Pin(2, Pin.OUT)
led.on()  # LED is active LOW, so on() turns it off

def blink_led(times=1, duration=0.2):
    """Blink the LED to indicate status."""
    for _ in range(times):
        led.off()  # Turn LED on
        time.sleep(duration)
        led.on()   # Turn LED off
        time.sleep(duration)

def connect_wifi():
    """Connect to WiFi network."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        try:
            wlan.connect(creds.WIFI_SSID, creds.WIFI_PASSWORD)
            attempt = 0
            while not wlan.isconnected() and attempt < 20:  # 20 second timeout
                blink_led(1, 0.1)  # Quick blink while connecting
                time.sleep(0.9)
                attempt += 1
            
            if not wlan.isconnected():
                print('WiFi connection failed!')
                return False
                
        except Exception as e:
            print('WiFi connection error:', e)
            return False
    
    print('WiFi connected!')
    print('Network config:', wlan.ifconfig())
    blink_led(3)  # 3 blinks for success
    return True

def get_strava_token():
    """Get a fresh Strava access token."""
    auth_url = "https://www.strava.com/oauth/token"
    payload = {
        'client_id': creds.STRAVA_CLIENT_ID,
        'client_secret': creds.STRAVA_CLIENT_SECRET,
        'refresh_token': creds.STRAVA_REFRESH_TOKEN,
        'grant_type': 'refresh_token'
    }
    
    try:
        print("Requesting Strava token...")
        response = requests.post(auth_url, json=payload)
        token_data = response.json()
        response.close()
        gc.collect()  # Free up memory
        print("Token received successfully")
        return token_data.get('access_token')
    except Exception as e:
        print('Token Error:', e)
        return None

def get_gear_distance():
    """Get the distance for the specified gear."""
    try:
        # Get access token
        access_token = get_strava_token()
        if not access_token:
            return None
            
        # Get gear data
        print("Fetching gear data...")
        gear_url = f"https://www.strava.com/api/v3/gear/{creds.GEAR_ID}"
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = requests.get(gear_url, headers=headers)
        gear_data = response.json()
        response.close()
        gc.collect()  # Free up memory
        
        # Calculate distance in kilometers
        distance_km = gear_data.get('distance', 0) / 1000
        return distance_km
        
    except Exception as e:
        print('Error getting gear data:', e)
        return None

def main():
    try:
        # Initialize hardware
        machine.freq(160000000)  # Set CPU frequency to 160MHz for better stability
        print("\n=== Starting Strava Gear Monitor ===")
        
        # Connect to WiFi
        if not connect_wifi():
            print("WiFi connection failed, going to sleep...")
            blink_led(5, 0.1)  # 5 quick blinks for error
            machine.deepsleep(60000)  # Sleep for 1 minute and try again
            return
        
        # Get gear distance
        distance = get_gear_distance()
        
        if distance is not None:
            print(f"\nBike Distance: {distance:.1f} km")
            blink_led(2)  # 2 blinks for successful data retrieval
        else:
            print("\nFailed to get distance")
            blink_led(5)  # 5 blinks for error
        
        # Clean up before sleep
        gc.collect()
        time.sleep(1)
        
        # Deep sleep for 1 hour to save power
        print("\nGoing to sleep for 1 hour...")
        machine.deepsleep(3600000)  # Sleep for 1 hour (in milliseconds)
        
    except Exception as e:
        print('Main loop error:', e)
        blink_led(10, 0.1)  # 10 quick blinks for critical error
        machine.deepsleep(60000)  # Sleep for 1 minute and try again

if __name__ == "__main__":
    main() 
import urequests as requests
import network
import time
import json
import socket
from machine import Pin, SPI, reset
from time import sleep
from credentials import WIFI_SSID, WIFI_PASSWORD, STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN, GEAR_ID
from max7219 import Matrix8x8
from custom_font import draw_text, draw_char  # Add this import
import machine

# Initialize SPI and display
spi = SPI(1, baudrate=10000000)
display = Matrix8x8(spi, Pin(15, Pin.OUT), 4)  # 4 modules
display.brightness(1)  # Set maximum brightness (0-15)

def setup_web_server():
    """Setup a simple web server for remote control."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 80))
        s.listen(5)
        s.setblocking(False)
        
        # Get and display IP address
        wlan = network.WLAN(network.STA_IF)
        ip = wlan.ifconfig()[0]
        print(f"\nWeb server started on http://{ip}/")
        print("You can visit this URL from any browser on your network to restart the device")
        return s
    except Exception as e:
        print(f"Failed to setup web server: {e}")
        return None

def check_for_restart_request(server_socket):
    """Check for incoming web requests to restart."""
    if server_socket is None:
        return
        
    try:
        conn, addr = server_socket.accept()
        print(f"Received connection from: {addr}")
        
        try:
            # Set blocking mode temporarily for reliable reading
            conn.setblocking(True)
            
            # Read and print the request for debugging
            request = conn.recv(1024)
            request_str = request.decode()
            print("Received request:", request_str)
            
            # Check if this is a restart request
            if 'restart' in request_str.lower():
                # Send restart response
                response = b"HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\n\r\nRestarting device..."
                conn.send(response)
                print("Response sent")
                conn.close()
                print("Connection closed")
                
                # Now restart with animation
                print("Starting restart sequence...")
                scroll_text("Updating...")  # Use scroll effect for "Updating..."
                sleep(0.5)  # Short pause after scrolling
                print("Calling reset()...")
                machine.reset()
            else:
                # Get current distance from file
                try:
                    current_distance = load_last_distance()
                    distance_str = f"{current_distance:.1f}km" if current_distance is not None else "Unknown"
                except:
                    distance_str = "Unknown"
                
                # Send normal response with current distance
                response = b"HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n"
                response += b"<html><body style='font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px;'>"
                response += b"<h1>Strava Gear km Display</h1>"
                response += f"<h2>Current Distance: {distance_str}</h2>".encode()
                response += b"<p>To restart the device, visit: <a href='/restart'>/restart</a></p>"
                response += b"</body></html>"
                conn.send(response)
                conn.close()
                
        except Exception as e:
            print(f"Error handling request: {e}")
            try:
                conn.close()
            except:
                pass
            
    except OSError as e:  # No connection waiting
        if str(e) != '[Errno 11] EAGAIN':  # Only print unexpected errors
            print(f"Connection error: {e}")
        pass

def restart_device():
    """Restart the D1 Mini."""
    scroll_text("Updating...")  # Update this function too for consistency
    sleep(0.5)
    reset()

def save_last_distance(distance):
    """Save the last known distance to a file."""
    try:
        with open('last_distance.txt', 'w') as f:
            f.write(str(distance))
    except:
        print("Could not save distance")

def load_last_distance():
    """Load the last known distance from file."""
    try:
        with open('last_distance.txt', 'r') as f:
            return float(f.read().strip())
    except:
        return None

def display_text(text):
    """Display text statically on the LED matrix displays."""
    display.fill(0)  # Clear display
    if text.replace('.', '').replace('k', '').replace('m', '').isdigit():
        # If the text is a number (allowing for decimal points and km suffix)
        draw_text(display, text.replace('km', ''), 0, 0, 'large')
    else:
        # For error messages and other text, use the default font
        display.text(text, 0, 0)
    display.show()

def animate_update(old_value, new_value):
    """Animate the update from old value to new value."""
    # First, show the difference with a + sign
    difference = new_value - old_value
    if difference > 0.1:  # Only animate if there's at least 0.1km increase
        # Show difference as whole number
        diff_text = f"+{int(difference)}"
        display_text(diff_text)
        sleep(2)  # Show the difference for 2 seconds
        
        # Now animate counting up from old to new value
        steps = 100  # Increased to 100 steps for maximum smoothness
        step_size = difference / steps
        for i in range(steps):  # Don't include the final step
            current = old_value + (step_size * i)
            display_text(f"{int(current):04d}")  # Show 4 digits with leading zeros
            sleep(0.02)  # Decreased to 20ms for ultra-smooth animation
        # Show final value with decimal
        display_text(f"{new_value:.1f}km")
    else:
        # If no change or negative change, just show new value
        display_text(f"{new_value:.1f}km")

def scroll_text(text, delay=0.05):
    """Scroll text across the LED matrix displays."""
    # Clear the display first
    display.fill(0)
    display.show()
    
    # Get the text width
    text_width = len(text) * 8  # Each character is typically 8 pixels wide
    
    # Scroll the text
    for i in range(32 + text_width):
        display.fill(0)  # Clear display
        display.text(text, 32 - i, 0)  # Keep consistent with static text position
        display.show()
        sleep(delay)

def connect_wifi():
    """Connect to WiFi network."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print('Connecting to WiFi network:', WIFI_SSID)
        try:
            wlan.connect(WIFI_SSID, WIFI_PASSWORD)
            # Wait up to 10 seconds for connection
            retry_count = 0
            while not wlan.isconnected() and retry_count < 10:
                print('Waiting for connection...')
                time.sleep(1)
                retry_count += 1
            
            if wlan.isconnected():
                print('Successfully connected to WiFi!')
                ip, subnet, gateway, dns = wlan.ifconfig()
                print(f'IP Address: {ip}')
                print(f'Subnet: {subnet}')
                print(f'Gateway: {gateway}')
                print(f'DNS: {dns}')
                return True
            else:
                print('Failed to connect to WiFi after 10 seconds')
                print('Please check your WIFI_SSID and WIFI_PASSWORD are correct')
                return False
        except Exception as e:
            print('WiFi connection error:', e)
            return False
    else:
        print('Already connected to WiFi')
        ip, subnet, gateway, dns = wlan.ifconfig()
        print(f'IP Address: {ip}')
        print(f'Subnet: {subnet}')
        print(f'Gateway: {gateway}')
        print(f'DNS: {dns}')
        return True

def get_strava_token():
    """Get a fresh Strava access token."""
    auth_url = "https://www.strava.com/oauth/token"
    payload = {
        'client_id': STRAVA_CLIENT_ID,
        'client_secret': STRAVA_CLIENT_SECRET,
        'refresh_token': STRAVA_REFRESH_TOKEN,
        'grant_type': 'refresh_token'
    }
    
    try:
        response = requests.post(auth_url, json=payload)
        token_data = response.json()
        response.close()
        return token_data.get('access_token')
    except Exception as e:
        print('Token Error:', e)
        return None

def get_gear_distance():
    """Get the distance and name for the specified gear."""
    try:
        # Get access token
        access_token = get_strava_token()
        if not access_token:
            return None, None
            
        # Get gear data
        gear_url = f"https://www.strava.com/api/v3/gear/{GEAR_ID}"
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = requests.get(gear_url, headers=headers)
        gear_data = response.json()
        response.close()
        
        # Get distance in kilometers and gear name
        distance_km = gear_data.get('distance', 0) / 1000
        gear_name = gear_data.get('name', 'Unknown Gear')
        return distance_km, gear_name
        
    except Exception as e:
        print('Error:', e)
        return None, None

def animate_initial_value(value):
    """Animate counting up to the initial value."""
    steps = 100  # Increased to 100 steps for maximum smoothness
    for i in range(steps):  # Don't include the final step
        current = (value * i) / steps
        display_text(f"{int(current):04d}")  # Show 4 digits with leading zeros
        sleep(0.02)  # Decreased to 20ms for ultra-smooth animation
    # Show final value with decimal
    display_text(f"{value:.1f}km")

def startup_animation():
    """Display a smooth startup animation."""
    # First clear the display
    display.fill(0)
    display.show()
    
    # Sweep animation - light up each column from left to right
    for x in range(32):  # Full width of 4 8x8 matrices
        for y in range(8):  # Height of matrix
            display.pixel(x, y, 1)
        display.show()
        sleep(0.02)  # Fast sweep
    
    sleep(0.2)  # Brief pause when fully lit
    
    # Sweep out animation - clear each column from left to right
    for x in range(32):
        for y in range(8):
            display.pixel(x, y, 0)
        display.show()
        sleep(0.02)
    
    # Show 0000 directly
    # display_text("0000")

def main():
    # Start with the startup animation
    startup_animation()
    
    # Connect to WiFi first since we need it for gear info
    if not connect_wifi():
        display_text("Error")
        return
    
    # Get IP address
    wlan = network.WLAN(network.STA_IF)
    ip_address = wlan.ifconfig()[0]
    
    # Setup web server for remote restart
    server_socket = setup_web_server()
    
    # Get gear distance and name
    distance, gear_name = get_gear_distance()
    
    if distance is not None and gear_name is not None:
        # Show gear name first
        scroll_text(f"{gear_name}")
        sleep(1)  # Pause after scrolling
        
        # Show IP address
        scroll_text(f"IP: {ip_address}")
        sleep(1)  # Pause after scrolling
        
        # Display last known distance immediately if available
        last_distance = load_last_distance()
        if last_distance is not None:
            animate_initial_value(last_distance)
        
        # Only animate if there's no stored value or if there's an actual increase
        if last_distance is None:
            animate_initial_value(distance)
        elif distance - last_distance > 0.1:
            animate_update(last_distance, distance)
        else:
            display_text(f"{distance:.1f}km")
        
        # Save the new distance
        save_last_distance(distance)
        print(f"Bike Distance: {distance:.1f}km")
        
        # Keep checking for restart requests without updating distance
        while True:
            check_for_restart_request(server_socket)
            sleep(1)
    else:
        # If error, keep showing last known distance if available
        last_distance = load_last_distance()
        if last_distance is not None:
            display_text(f"{last_distance:.1f}km")
        else:
            print("Failed to get distance")
            display_text("Error")

if __name__ == "__main__":
    main() 
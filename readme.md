# Strava LED Matrix Display Bike Gear Stats

A project that combines Strava cycling data with an ESP8266-based LED matrix display to show real-time gear statistics. The display shows your bike's mileage and features smooth animations for updates.

![LED Matrix Display](/_readme/d1mini_ledmatrix.jpeg)

## 🚲 Overview

This project creates a smart LED display that shows cycling gear statistics from Strava, perfect for monitoring your bike's mileage and other metrics. Features include:
- One-time display of current mileage at startup
- Smooth animations for value updates
- Web interface for remote restart
- Display of bike name and IP address at startup
- Fallback to last known distance when offline

## 🛠 Hardware Setup

The hardware setup consists of a D1 Mini (ESP8266) connected to four MAX7219 LED matrix modules chained together. As shown in the image above, the setup creates a 32x8 pixel display perfect for showing numerical values and scrolling text.

### Hardware Requirements

- ESP8266 D1 Mini Board
- 4x MAX7219 LED Matrix Modules (chained)
- USB Cable for power and programming
- Basic wiring/jumper cables (5 connections needed)

### Wiring Configuration

| LED Matrix Pin | D1 Mini Pin |
|---------------|-------------|
| VCC           | 5V         |
| GND           | Ground     |
| DIN           | D7         |
| CS            | D8         |
| CLK           | D5         |


## 💻 Software Components

### Core Files
- `d1_mini_gear_check.py`: Main program file handling LED control and Strava API communication
- `credentials.py`: Configuration file for storing sensitive data
- `max7219.py`: LED matrix driver (required)
- `custom_font.py`: Custom font definitions for the display

### Dependencies
- MicroPython for ESP8266
- `urequests` library for API calls
- `network` library for WiFi connectivity
- `max7219` library for LED matrix control
- `machine` and `spi` libraries for hardware control

## 📥 Installation Instructions

### 1. Set Up Development Environment

1. Install Python 3.x on your computer
2. Install `ampy` for file transfer:
   ```bash
   pip install adafruit-ampy
   ```
3. Install a serial terminal program (e.g., `screen` on macOS/Linux or PuTTY on Windows)

### 2. Prepare the D1 Mini

1. Download MicroPython firmware for ESP8266 from the [official website](https://micropython.org/download/esp8266/)
2. Flash MicroPython to your D1 Mini:
   ```bash
   # For Linux/macOS:
   # First, erase the flash
   esptool.py --port /dev/tty* erase_flash
   # Then, flash MicroPython
   esptool.py --port /dev/tty* --baud 460800 write_flash --flash_size=detect 0 esp8266-VERSION.bin

   # For Windows:
   # First, erase the flash
   esptool.py --port COM* erase_flash
   # Then, flash MicroPython
   esptool.py --port COM* --baud 460800 write_flash --flash_size=detect 0 esp8266-VERSION.bin
   ```

### 3. Configure the Project

1. Clone this repository
2. First, find your Strava gear IDs:
   - Copy `credentials_template.py` to `credentials.py`
   - Add only your Strava API credentials initially:
     ```python
     STRAVA_CLIENT_ID = "your_client_id"
     STRAVA_CLIENT_SECRET = "your_client_secret"
     STRAVA_REFRESH_TOKEN = "your_refresh_token"
     ```
   - Run the provided script to list all your bikes:
     ```bash
     python strava_gear.py
     ```
   - The script will show all your Strava gear with their IDs and current mileage
   - Note down the ID of the bike you want to display

3. Complete your credentials.py configuration with all settings:
   ```python
   # Strava API settings
   STRAVA_CLIENT_ID = "your_client_id"
   STRAVA_CLIENT_SECRET = "your_client_secret"
   STRAVA_REFRESH_TOKEN = "your_refresh_token"
   GEAR_ID = "your_bike_id"  # Use the ID from strava_gear.py output

   # WiFi settings
   WIFI_SSID = "your_wifi_name"
   WIFI_PASSWORD = "your_wifi_password"

### 4. Upload Files Using Ampy

Upload all required files to the D1 Mini:
```bash
# Replace /dev/ttyUSB* with your port (Windows: COMx)
ampy --port /dev/ttyUSB* put d1_mini_gear_check.py
ampy --port /dev/ttyUSB* put credentials.py
ampy --port /dev/ttyUSB* put max7219.py
ampy --port /dev/ttyUSB* put custom_font.py
ampy --port /dev/ttyUSB* put boot.py

```

### 5. Running the Project

1. Connect the hardware according to the wiring diagram
2. Power up the D1 Mini
3. The display will show:
   - Initial startup animation
   - Current bike mileage from Strava
   - Periodic updates with smooth animations
   - Scrolling bike name every minute

### 6. Web Interface

Once running, you can access the web interface:
1. The D1 Mini will display its IP address on startup
2. Visit `http://<device-ip>/` in your browser
3. You can view current distance and restart the device if needed

## 🤔 Troubleshooting

- If the display shows "Error", check your WiFi and Strava API credentials
- If no display, verify the wiring connections
- For connection issues, check the serial output using:
  ```bash
  screen /dev/ttyUSB0 115200
  ```

## 🚀 Future Improvements

- [ ] Web interface for dynamic gear selection
- [ ] Support for multiple bikes/devices
- [ ] Enhanced user configuration options
- [ ] Additional display modes and statistics

## 📝 Notes

- The system currently supports one bike at a time
- Gear ID must be manually configured in the credentials file
- Regular Strava API rate limits apply
- The display shows data at startup and can be refreshed via web interface
- Last known distance is stored and displayed during connection issues

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

## ✨ Acknowledgments

- Strava API for providing access to cycling data
- ESP8266 community for excellent documentation and support
- MicroPython community for the ESP8266 port

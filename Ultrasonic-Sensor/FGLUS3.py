import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import RPi.GPIO as GPIO

# Set up Google Sheets authentication
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name("/home/orang/Downloads/ussensor-3b3165d33254.json", scope)
client = gspread.authorize(creds)

# Open the Google Sheet
sheet = client.open('USsensor').sheet1

# Set up HC-SR04 sensor
GPIO.setmode(GPIO.BCM)
TRIG = 16
ECHO = 26
GLED = 20
RLED = 21
GPIO.setup(GLED, GPIO.OUT)
GPIO.setup(RLED, GPIO.OUT)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def get_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.2)
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    return distance

# Specify the cell for this sensor
status_col = 2    # Column B
status_row = 2    # Row 2

# Take 6 measurements and average the distance
distances = []
for i in range(6):
    distance = get_distance()
    distances.append(distance)
    print(f"Measurement {i+1}: {distance} cm")

average_distance = sum(distances) / len(distances)
average_distance = round(average_distance, 2)

# Determine status based on the average distance
if average_distance > 10:
    status = "not full"
    GPIO.output(GLED, GPIO.HIGH)
    GPIO.output(RLED, GPIO.LOW)
else:
    status = "full"
    GPIO.output(GLED, GPIO.LOW)
    GPIO.output(RLED, GPIO.HIGH)

# Update the specific cell with the status
sheet.update_cell(status_row, status_col, status)

print(f"Average Distance: {average_distance} Status: {status}")

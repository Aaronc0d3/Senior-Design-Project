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

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)

# Define sensor configurations
sensors = [
    {
        'name': 'Sensor1',
        'pins': {
            'TRIG': 23,
            'ECHO': 24,
            'GLED': 22,
            'RLED': 25
        },
        'status_row': 2,
        'status_col': 1
    },
    {
        'name': 'Sensor2',
        'pins': {
            'TRIG': 17,
            'ECHO': 27,
            'GLED': 2,
            'RLED': 3
        },
        'status_row': 2,
        'status_col': 2
    },
    {
        'name': 'Sensor3',
        'pins': {
            'TRIG': 6,
            'ECHO': 5,
            'GLED': 13,
            'RLED': 19
        },
        'status_row': 2,
        'status_col': 3
    },
    {
        'name': 'Sensor4',
        'pins': {
            'TRIG': 16,
            'ECHO': 26,
            'GLED': 20,
            'RLED': 21
        },
        'status_row': 2,
        'status_col': 4
    }
]

# Set up GPIO for all sensors
for sensor in sensors:
    for pin_name, pin_number in sensor['pins'].items():
        GPIO.setup(pin_number, GPIO.OUT if pin_name in ['TRIG', 'GLED', 'RLED'] else GPIO.IN)

def get_distance(trig_pin, echo_pin):
    """Measure distance using the ultrasonic sensor."""
    GPIO.output(trig_pin, False)
    time.sleep(0.2)
    GPIO.output(trig_pin, True)
    time.sleep(0.00001)
    GPIO.output(trig_pin, False)
   
    while GPIO.input(echo_pin) == 0:
        pulse_start = time.time()
    while GPIO.input(echo_pin) == 1:
        pulse_end = time.time()
       
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return round(distance, 2)

def process_sensor(sensor):
    """Process measurements for a single sensor and update its status."""
    # Take 6 measurements and average the distance
    distances = []
    print(f"\nProcessing {sensor['name']}:")
    for i in range(6):
        distance = get_distance(sensor['pins']['TRIG'], sensor['pins']['ECHO'])
        distances.append(distance)
        print(f"Measurement {i+1}: {distance} cm")

    average_distance = round(sum(distances) / len(distances), 2)

    # Determine status based on the average distance
    if average_distance > 10:
        status = "not full"
        GPIO.output(sensor['pins']['GLED'], GPIO.HIGH)
        GPIO.output(sensor['pins']['RLED'], GPIO.LOW)
    else:
        status = "full"
        GPIO.output(sensor['pins']['GLED'], GPIO.LOW)
        GPIO.output(sensor['pins']['RLED'], GPIO.HIGH)

    # Update the Google Sheet
    sheet.update_cell(sensor['status_row'], sensor['status_col'], status)
    print(f"{sensor['name']} - Average Distance: {average_distance} cm, Status: {status}")

def main():
    """Main function to process all sensors."""
    try:
        while True:
            for sensor in sensors:
                process_sensor(sensor)
            time.sleep(1)  # Wait before next round of measurements
           
    except KeyboardInterrupt:
        print("\nProgram stopped by user")
    except Exception as e:
        print(f"An error occurred: {e}")
if __name__ == "__main__":
    main()

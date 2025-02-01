import random
import time
import requests
from datetime import datetime

meter_id = [f"meter_{i}" for i in range(1, 11)]
url = "" 
# TODO: need to add url

# simulate meter readings
def generate_reading():
    meter_reading = random.randint(200, 600)
    return meter_reading

# send meter data to the server
def send_meter_data(meter_id, reading, timestamp):
    params = {
        "meterid": meter_id,
        "reading": reading,
        "timestamp": timestamp
    }
    
    try:
        response = requests.post(url, params=params)
        if response.status_code == 200:
            print(f"Successfully sent data for {meter_id} at {timestamp}")
        else:
            print(f"Failed to send data for {meter_id}")
    except Exception:
        print(f"Error sending data for {meter_id}")

# run the simulation
def meter_simulation():
    while True:
        meter_id = random.choice(meter_id)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        reading = generate_reading()
        send_meter_data(meter_id, timestamp, reading)
        time.sleep(5)
        # TODO: need to confirm the sending interval

if __name__ == "__main__":
    meter_simulation()

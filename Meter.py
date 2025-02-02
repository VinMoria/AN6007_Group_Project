import random
import time
import requests
from datetime import datetime, timedelta

user_data_list = [[str(i).zfill(8), 0] for i in range(1, 10)]
url = "http://127.0.0.1:5000/meter/sendReading"

# simulate meter readings
# def generate_reading():
# 	meter_reading = random.randint(200, 600)
# 	return meter_reading

# send meter data to the server


def send_meter_data(user_id, reading, timestamp):
	params = {
		"user_id": user_id,
		"reading": reading,
		"timestamp": timestamp
	}

	try:
		response = requests.post(url, json=params)
		if response.status_code == 200:
			print(f"Successfully sent data for {user_id} at {timestamp}")
		else:
			print(f"Failed to send data for {user_id}")
	except Exception as e:
		print(f"Error sending data for {user_id},{e}")

# run the simulation


def meter_simulation(time_start_str, time_end_str):
	format_str = "%Y-%m-%d %H:%M:%S"
	time_start = datetime.strptime(time_start_str, format_str)
	time_end = datetime.strptime(time_end_str, format_str)

	new_time = time_start
	while new_time <= time_end:
		running_range_start = new_time.replace(
			hour=1, minute=0, second=0, microsecond=0)
		runnint_range_end = new_time.replace(
			hour=23, minute=00, second=00, microsecond=0)
		if running_range_start <= new_time <= runnint_range_end:
			for user_data in user_data_list:
				user_id = user_data[0]
				reading = user_data[1] + random.randint(200, 600)
				timestamp = new_time.strftime("%Y-%m-%d %H:%M:%S")
				user_data[1] = reading
				send_meter_data(user_id, reading, timestamp)
		new_time = new_time + timedelta(minutes=30)
	print(new_time)
	time.sleep(0.2)

	# while True:
	# 	# meter_id = random.choice(meter_id)
	# 	timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	# 	print(timestamp)
	# 	reading = generate_reading()
	# 	send_meter_data("00000001", timestamp, reading)
	# 	time.sleep(5)
		# TODO: need to confirm the sending interval
if __name__ == "__main__":
	# send_meter_data("00000001",200,"2024-11-24 05:00:00")
	meter_simulation("2024-12-29 05:00:00", "2025-1-10 22:00:00")

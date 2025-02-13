import random
import requests
from datetime import datetime, timedelta
import time

user_data_list = []
server_ip = "127.0.0.1:5000"
send_reading_url = f"http://{server_ip}/meter/sendReading"
register_url = f"http://{server_ip}/user/register"
batch_url = f"http://{server_ip}/batch"


def send_meter_data(user_id, reading, timestamp):
	params = {
		"user_id": user_id,
		"reading": reading,
		"timestamp": timestamp
	}

	try:
		response = requests.post(send_reading_url, json=params)
		if response.status_code == 200:
			print(f"Successfully sent data for {user_id} at {timestamp}")
		else:
			print(f"Failed to send data for {user_id}")
	except Exception as e:
		print(f"Error sending data for {user_id},{e}")

# send register to server
def send_register(username, area):
	params = {
		"username": username,
		"area": area
	}

	try:
		response = requests.post(register_url, json=params)
		receive_data = response.json()
		if receive_data['status'] == 'success':
			print(f"Successfully sent data: {username},{area}")
			user_id = receive_data['user_id']
			user_data_list.append([user_id, 0])
			print(user_data_list)
		else:
			print(f"Failed to send data for {username},{area}")
	except Exception as e:
		print(f"Error sending data for {username},{area},{e}")

def send_batch():
	response = requests.get(batch_url)
	receive_data = response.json()
	if receive_data['status'] == 'success':
		print("Successfully sent batch")
	else:
		print(f"Failed: {receive_data['message']}")


# run the simulation
def meter_simulation(time_start_str, time_end_str):
	format_str = "%Y-%m-%d %H:%M:%S"
	time_start = datetime.strptime(time_start_str, format_str)
	time_end = datetime.strptime(time_end_str, format_str)

	new_time = time_start
	last_day = new_time.day  # 记录当前日期
	
	while new_time <= time_end:
		# 检查是否跨天
		if new_time.day != last_day:
			send_batch()
			last_day = new_time.day
			time.sleep(1)
			
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
		new_time = new_time + timedelta(hours=4)
		# time.sleep(0.2)
	print(new_time)


if __name__ == "__main__":

	# 注册用户
	send_register("Alice Johnson", "Orchard Road")
	send_register("Bob Smith", "Marina Bay")
	# send_register("Charlie Brown", "Sentosa")
	# send_register("Diana White", "Orchard Road")
	# send_register("Ethan Davis", "Marina Bay")
	# send_register("Fiona Wilson", "Sentosa")
	# send_register("George Taylor", "Sentosa")
	# send_register("Hannah Clark", "Marina Bay")
	# send_register("Isaac Lewis", "Orchard Road")
	# send_register("Jack Martin", "Orchard Road")

	# 发送读数
	meter_simulation("2024-11-25 05:00:00", "2024-12-01 22:00:00")
	# meter_simulation("2025-02-09 05:00:00", "2025-02-10 22:00:00")

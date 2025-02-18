from User import User
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor


class UserService:

	def __init__(self):
		print("UserService init")
		# 生成userID
		self.current_id = 0

		# 存储用户的dictionary
		self.user_dict = {
                    # "00000001":user_object,
		}

		# 存储一日的原始数据，batch job时储存文件
		self.daily_raw_data = []

		self.current_date = None

	def register(self, username, area):
		# 生成用户ID
		self.current_id += 1
		new_user_id = str(self.current_id).zfill(8)

		# 创建用户对象
		new_user = User(username, area, new_user_id)
		self.user_dict[new_user_id] = new_user
		# print(self.user_dict)

		# 返回分配的用户ID
		return new_user_id

	# 接收读数时

	def receive_reading(self, user_id, timestamp, reading):
		self.current_date = timestamp[:10]
		self.user_dict[user_id].receive_reading(timestamp, reading)
		# 记录读数原始数据
		self.daily_raw_data.append((
                    user_id,
                    timestamp,
                    reading
                ))

	# 获取用户显示数据
	def get_user_display_data(self, user_id):
		return self.user_dict[user_id].get_display_data()

	# 一天结束后的批量处理
	def batch_job(self):
		# 多线程处理 User的batch_job
		with ThreadPoolExecutor() as executor:
			futures = [executor.submit(self.user_dict[user_id].batch_job) 
					  for user_id in self.user_dict]
			
			for future in futures:
				future.result()

		record_dir = Path("records")
		record_dir.mkdir(exist_ok=True)

		# 存储日原始数据
		if self.daily_raw_data:
			# 将daily_raw_data转换为DataFrame
			df = pd.DataFrame(self.daily_raw_data, columns=['user_id', 'timestamp', 'reading'])
			# 确保raw_records目录存在

			# 生成带时间戳的文件名
			filename = record_dir / f"daily_raw_data_{self.current_date}.csv"
			# 保存为CSV文件
			df.to_csv(filename, index=False)
			# 清空daily_daily_raw_data
			self.daily_raw_data = []

		# 是否为月末最后一天
		tmp_current_date = datetime.strptime(self.current_date, "%Y-%m-%d")
		next_day = tmp_current_date + timedelta(days=1)
		if tmp_current_date.month != next_day.month:
			# 是月末最后一天，则触发月度计算
			user_month_usage = []
			for user_id in self.user_dict:
				user_month_usage.append([user_id, self.user_dict[user_id].month_usage_history[-1][0][:7],self.user_dict[user_id].month_usage_history[-1][1]])
			df = pd.DataFrame(user_month_usage, columns=['user_id', 'timestamp', 'usage'])
			# 存储月度数据
			filename = record_dir / f"monthly_usage_data_{self.current_date}.csv"
			df.to_csv(filename, index=False)

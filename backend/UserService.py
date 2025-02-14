from User import User
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path


class UserService:

	def __init__(self):
		print("UserService init")
		# 生成userID
		self.current_id = 0

		# 存储用户的dictionary
		self.user_dict = {
                    # "00000001":user_object,
		}

		# self.user_id_set = set()
		# self.area_set = set()

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

		# # 注册在目录中
		# self.user_id_set.add(new_user_id)
		# self.area_set.add(area)

		# 返回分配的用户ID
		return new_user_id

	# 接收读数时

	def receive_reading(self, user_id, timestamp, reading):
		self.current_date = timestamp[:10]
		# 将时间戳字符串转换为日期格式（保留年月日部分）
		date_str = timestamp[:10]  # 截取前10个字符"YYYY-MM-DD"
		self.user_dict[user_id].receive_reading(date_str, reading)
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
		# 计算User的用电量
		for user_id in self.user_dict:
			self.user_dict[user_id].batch_job()


		record_dir = Path("records")
		record_dir.mkdir(exist_ok=True)

		# 存储原始数据
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
			df = pd.DataFrame(user_month_usage, columns=['user_id', 'timestamp', 'reading'])
			# 存储月度数据
			filename = record_dir / f"monthly_usage_data_{self.current_date}.csv"
			df.to_csv(filename, index=False)

	# # 管理员查询
	# def admin_query(self, start_time, end_time, area, period_type):
	# 	if area == "all":
	# 		filtered_df = self.raw_df[self.raw_df['timestamp'].between(start_time, end_time)]
	# 	else:
	# 		filtered_df = self.raw_df[self.raw_df['area'] == area]
	# 		filtered_df = filtered_df[filtered_df['timestamp'].between(start_time, end_time)]

	# 	# 确保 timestamp 列是 datetime 格式
	# 	filtered_df['timestamp'] = pd.to_datetime(filtered_df['timestamp'])

	# 	# 一次性完成分组、计算用电量和汇总
	# 	consumption_df = (filtered_df.groupby([pd.Grouper(key='timestamp', freq=period_type), 'user_id'])['reading']
    #                 .agg(['max', 'min'])
    #                 .assign(consumption=lambda x: x['max'] - x['min'])
    #                 .reset_index()
    #                 .groupby('timestamp')['consumption']
    #                 .sum())

	# 	return consumption_df.tolist()

	# # 存储数据
	# def store_data(self):
	# 	# 确保backup目录存在
	# 	backup_dir = Path("backup")
	# 	backup_dir.mkdir(exist_ok=True)

	# 	# 删除旧的备份文件
	# 	for old_file in backup_dir.glob("daily_raw_data_*.csv"):
	# 		old_file.unlink()
	# 	for old_file in backup_dir.glob("user_dict_*.pkl"):
	# 		old_file.unlink()

	# 	# 将raw_df存储到csv文件中，按当前时间命名
	# 	now = datetime.now()
	# 	filename = backup_dir / f"daily_raw_data_{now.strftime('%Y-%m-%d_%H-%M-%S')}.csv"
	# 	self.raw_df.to_csv(filename, index=False)

	# 	# 将user_dict直接存储为二进制文件
	# 	filename = backup_dir / f"user_dict_{now.strftime('%Y-%m-%d_%H-%M-%S')}.pkl"
	# 	with open(filename, 'wb') as f:
	# 		pickle.dump(self.user_dict, f)

	# 	print(f"store_data success on {now.strftime('%Y-%m-%d %H:%M:%S')}")

	# # 加载备份数据
	# def load_data(self):
	# 	# 检查backup目录是否存在且有文件
	# 	backup_path = Path("backup")
	# 	if not backup_path.exists() or not any(backup_path.iterdir()):
	# 		return

	# 	# 直接获取唯一的数据文件
	# 	daily_raw_data_file = next(backup_path.glob("daily_raw_data_*.csv"))
	# 	self.raw_df = pd.read_csv(daily_raw_data_file)

	# 	# 直接获取唯一的用户字典文件
	# 	user_dict_file = next(backup_path.glob("user_dict_*.pkl"))
	# 	with open(user_dict_file, 'rb') as f:
	# 		self.user_dict = pickle.load(f)

	# 	# 更新current_id
	# 	self.current_id = len(self.user_dict)
	# 	print(f"load_data success on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
	# 	return

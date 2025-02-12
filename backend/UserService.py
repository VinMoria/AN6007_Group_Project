from User import User
import pandas as pd
from datetime import datetime
from pathlib import Path
import pickle

class UserService:

	def __init__(self):
		print("UserService init")
		# 自增的生成ID
		self.current_id = 0

		# 存储用户的dictionary
		self.user_dict = {
                    # "00000001":user_object,
		}

		# TODO: 需要数据恢复
		self.user_id_set = set()
		self.area_set = set()

		self.raw_df = pd.DataFrame(
                    columns=['user_id', 'area', "username", 'timestamp', 'reading'])
		self.load_data()

	def register(self, username, area):
		# 生成用户ID
		self.current_id += 1
		new_user_id = str(self.current_id).zfill(8)

		# 创建用户对象
		new_user = User(username, area, new_user_id)
		self.user_dict[new_user_id] = new_user
		print(self.user_dict)

		# 注册在目录中
		self.user_id_set.add(new_user_id)
		self.area_set.add(area)

		# 返回分配的用户ID
		return new_user_id

	def receive_reading(self, user_id, timestamp, reading):
		self.user_dict[user_id].receive_reading(timestamp, reading)
		# 更新底层数据
		self.raw_df.loc[len(self.raw_df)] = [user_id, self.user_dict[user_id].area,
                                       self.user_dict[user_id].username, timestamp, reading]

	def get_user_display_data(self, user_id):
		return self.user_dict[user_id].get_display_data()

	def admin_query(self, start_time, end_time, area, period_type):
		if area == "all":
			filtered_df = self.raw_df[self.raw_df['timestamp'].between(start_time, end_time)]
		else:
			filtered_df = self.raw_df[self.raw_df['area'] == area]
			filtered_df = filtered_df[filtered_df['timestamp'].between(start_time, end_time)]

		# 确保 timestamp 列是 datetime 格式
		filtered_df['timestamp'] = pd.to_datetime(filtered_df['timestamp'])
		
		# 一次性完成分组、计算用电量和汇总
		consumption_df = (filtered_df.groupby([pd.Grouper(key='timestamp', freq=period_type), 'user_id'])['reading']
                    .agg(['max', 'min'])
                    .assign(consumption=lambda x: x['max'] - x['min'])
                    .reset_index()
                    .groupby('timestamp')['consumption']
                    .sum())

		return consumption_df.tolist()
	
	# 存储数据
	def store_data(self):
		# 确保backup目录存在
		backup_dir = Path("backup")
		backup_dir.mkdir(exist_ok=True)
		
		# 删除旧的备份文件
		for old_file in backup_dir.glob("raw_data_*.csv"):
			old_file.unlink()
		for old_file in backup_dir.glob("user_dict_*.pkl"):
			old_file.unlink()
		
		# 将raw_df存储到csv文件中，按当前时间命名
		now = datetime.now()
		filename = backup_dir / f"raw_data_{now.strftime('%Y-%m-%d_%H-%M-%S')}.csv"
		self.raw_df.to_csv(filename, index=False)

		# 将user_dict直接存储为二进制文件
		filename = backup_dir / f"user_dict_{now.strftime('%Y-%m-%d_%H-%M-%S')}.pkl"
		with open(filename, 'wb') as f:
			pickle.dump(self.user_dict, f)

		print(f"store_data success on {now.strftime('%Y-%m-%d %H:%M:%S')}")

	# 加载备份数据
	def load_data(self):
		# 检查backup目录是否存在且有文件
		backup_path = Path("backup")
		if not backup_path.exists() or not any(backup_path.iterdir()):
			return

		# 直接获取唯一的数据文件
		raw_data_file = next(backup_path.glob("raw_data_*.csv"))
		self.raw_df = pd.read_csv(raw_data_file)

		# 直接获取唯一的用户字典文件
		user_dict_file = next(backup_path.glob("user_dict_*.pkl"))
		with open(user_dict_file, 'rb') as f:
			self.user_dict = pickle.load(f)

		# 更新current_id
		self.current_id = len(self.user_dict)
		print(f"load_data success on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
		return


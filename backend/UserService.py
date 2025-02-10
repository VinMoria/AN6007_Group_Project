from User import User
import pandas as pd


class UserService:
	# 自增的生成ID

	def __init__(self):
		print("UserService init")
		self.current_id = 0

		# 存储用户的dictionary
		self.user_dict = {
                    # "00000001":user_object,
		}

		self.user_id_set = set()
		self.area_set = set()

		self.raw_df = pd.DataFrame(
                    columns=['user_id', 'area', "username", 'timestamp', 'reading'])

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

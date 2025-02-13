from collections import deque
from datetime import datetime


class User:
	def __init__(self, username, area, user_id):
		self.username = username
		self.area = area
		self.user_id = user_id

		# 记录当前是哪一天
		self.current_day_timestamp = None

		# 记录一天最早和最晚的读数
		self.day_first_reading = None
		self.day_latest_reading = None

		# 记录历史用量 （滑动窗口，队列）
		self.day_usage_history = deque(maxlen=10)
		self.week_usage_history = deque(maxlen=10)
		self.month_usage_history = deque(maxlen=10)


	# 读数只记录一天最早和最晚的记录
	def receive_reading(self, timestamp, reading):
		if self.day_first_reading is None:
			self.day_first_reading = reading
			self.day_latest_reading = reading

		else:
			self.day_latest_reading = reading

		self.current_day_timestamp = timestamp



	# 获取User的数据，用于dashboard
	def get_display_data(self):
		res = {
			"username": self.username,
			"area": self.area,
			"user_id": self.user_id,
			"day_usage_history": list(self.day_usage_history),
			"week_usage_history": list(self.week_usage_history),
			"month_usage_history": list(self.month_usage_history),
		}
		return res
		
	# 每日结束后，进行批量处理
	def batch_job(self):

		self.day_usage_history.append([self.current_day_timestamp, self.day_latest_reading - self.day_first_reading])
		# 是否跨周
		current_day = datetime.strptime(self.current_day_timestamp, "%Y-%m-%d")
		if len(self.week_usage_history) == 0 or current_day.isocalendar()[1] != datetime.strptime(self.week_usage_history[-1][0], "%Y-%m-%d").isocalendar()[1]:
			self.week_usage_history.append([self.current_day_timestamp, self.day_latest_reading - self.day_first_reading])
		else:
			self.week_usage_history[-1][1] += self.day_latest_reading - self.day_first_reading

		# 是否跨月
		if len(self.month_usage_history) == 0 or current_day.month != datetime.strptime(self.month_usage_history[-1][0], "%Y-%m-%d").month:
			self.month_usage_history.append([self.current_day_timestamp, self.day_latest_reading - self.day_first_reading])
		else:
			self.month_usage_history[-1][1] += self.day_latest_reading - self.day_first_reading
		
		# 重置
		self.day_first_reading = self.day_latest_reading
		self.day_latest_reading = None
		self.current_day_timestamp = None

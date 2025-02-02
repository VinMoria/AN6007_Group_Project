from collections import deque


class User:
	def __init__(self, username, area, user_id):
		self.username = username
		self.area = area
		self.user_id = user_id

		# 记录上次接受的时刻， 用于判断是否跨时间段
		self.latest_timestamp = None

		# 记录最新用量
		self.latest_day_usage = 0
		self.latest_week_usage = 0
		self.latest_month_usage = 0

		# 记录历史用量 （滑动窗口，队列）
		self.day_usage_history = deque(maxlen=30)  # 30 days
		self.week_usage_history = deque(maxlen=6)  # 52 weeks
		self.month_usage_history = deque(maxlen=12)  # 12 months

	def receive_reading(self, timestamp, reading):
		# 根据读数更新最新用量和历史用量
		print(timestamp, reading)
		pass

	def get_data(self):
		res = {
			"username": self.username,
			"area": self.area,
			"user_id": self.user_id,
			"latest_day_usage": self.latest_day_usage,
			"latest_week_usage": self.latest_week_usage,
			"latest_month_usage": self.latest_month_usage,
			"day_usage_history": list(self.day_usage_history),
			"week_usage_history": list(self.week_usage_history),
			"month_usage_history": list(self.month_usage_history),
		}
		return res

from collections import deque
from datetime import datetime

class User:
	def __init__(self, username, area, user_id):
		self.username = username
		self.area = area
		self.user_id = user_id

		# 记录上次接受的时刻， 用于判断是否跨时间段
		self.latest_timestamp = None

		# 最新读数
		self.latest_reading = 0

		# 记录最新用量
		self.latest_day_usage = 0
		self.latest_week_usage = 0
		self.latest_month_usage = 0

		# 记录历史用量 （滑动窗口，队列）
		self.day_usage_history = deque(maxlen=30)  # 30 days
		self.week_usage_history = deque(maxlen=6)  # 52 weeks
		self.month_usage_history = deque(maxlen=12)  # 12 months

	# 根据读数更新最新用量和历史用量
	def receive_reading(self, timestamp, reading):
		
		if self.latest_timestamp is None:
			self.latest_timestamp = timestamp
			self.latest_reading = reading
			return

		# 将字符串转换为 datetime 对象
		format_str = "%Y-%m-%d %H:%M:%S"
		time1 = datetime.strptime(timestamp, format_str)
		time2 = datetime.strptime(self.latest_timestamp, format_str)

		# 检查是否同一天
		same_day = time1.date() == time2.date()

		# 检查是否同一周
		same_week = time1.isocalendar()[1] == time2.isocalendar()[1] and time1.isocalendar()[0] == time2.isocalendar()[0]

		# 检查是否同一个月
		same_month = time1.month == time2.month and time1.year == time2.year

		usage_diff = reading - self.latest_reading

		# 对日 周 月 有相似的逻辑
		# 如果最新的读数没有跨越时间周期，则累计在最新用量中
		# 如果跨越时间周期了，则将之前的最新用量存入历史用量，然后最新用量重新计数
		if same_day:
			self.latest_day_usage += usage_diff
		else:
			self.day_usage_history.append(self.latest_day_usage)
			self.latest_day_usage = usage_diff

		if same_week:
			self.latest_week_usage += usage_diff
		else:
			self.week_usage_history.append(self.latest_week_usage)
			self.latest_week_usage = usage_diff
		

		if same_month:
			self.latest_month_usage += usage_diff
		else:
			self.month_usage_history.append(self.latest_month_usage)
			self.latest_month_usage = usage_diff

		self.latest_reading = reading
		self.latest_timestamp = timestamp
		

	# 获取User的数据，用于dashboard
	def get_display_data(self):
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
		

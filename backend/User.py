from collections import deque
from datetime import datetime


class User:
	def __init__(self, username, area, user_id):
		self.username = username
		self.area = area
		self.user_id = user_id

		# 记录一天的所有读数
		self.day_readings = []

		# 记录历史用量 （滑动窗口，队列）
		self.day_usage_history = deque(maxlen=10)
		self.week_usage_history = deque(maxlen=10)
		self.month_usage_history = deque(maxlen=10)
		self.day_detail_usage_history = []


	# 读数只记录一天最早和最晚的记录
	def receive_reading(self, timestamp, reading):
		self.day_readings.append([timestamp, reading])


	# 获取User的数据，用于dashboard
	def get_display_data(self):
		res = {
			"username": self.username,
			"area": self.area,
			"user_id": self.user_id,
			"day_usage_history": list(self.day_usage_history),
			"week_usage_history": self.format_usage_history("W"),
			"month_usage_history": self.format_usage_history("M"),
			"day_detail_usage_history": self.day_detail_usage_history,
		}
		return res
	
	def format_usage_history(self, type):
		ans = []
		if type == "W":
			for record in self.week_usage_history:
				# 将日期转换为周数格式
				date_obj = datetime.strptime(record[0], "%Y-%m-%d")
				week_num = date_obj.isocalendar()[1]
				ans.append([f"{date_obj.year} W{week_num}", record[1]])

		elif type == "M":
			for record in self.month_usage_history:
				ans.append([record[0][:7], record[1]])

		return ans

		
	# 每日结束后，进行批量处理
	def batch_job(self):
		if len(self.day_readings) <= 1:
			return
		
		# 计算一天的用电量
		day_usage = self.day_readings[-1][1] - self.day_readings[0][1]
		# 读书表中的第一个可能是昨天的最后读数，因此读取最后一个读数的日期
		day_timestamp = self.day_readings[-1][0][:10]

		self.day_usage_history.append([day_timestamp, day_usage])
		# 是否跨周
		current_day = datetime.strptime(day_timestamp, "%Y-%m-%d")
		if len(self.week_usage_history) == 0 or current_day.isocalendar()[1] != datetime.strptime(self.week_usage_history[-1][0], "%Y-%m-%d").isocalendar()[1]:
			self.week_usage_history.append([day_timestamp, day_usage])
		else:
			self.week_usage_history[-1][1] += day_usage

		# 是否跨月
		if len(self.month_usage_history) == 0 or current_day.month != datetime.strptime(self.month_usage_history[-1][0], "%Y-%m-%d").month:
			self.month_usage_history.append([day_timestamp, day_usage])
		else:
			self.month_usage_history[-1][1] += day_usage
		
		# 一日的细节用量
		self.day_detail_usage_history = []

		for i,reading in enumerate(self.day_readings):
			if i == 0:
				continue
			usage = reading[1] - self.day_readings[i-1][1]
			self.day_detail_usage_history.append([reading[0], usage])

		# 重置，留下前一天的最后一个读数，用于计算两天之间的用量
		self.day_readings = [self.day_readings[-1]]

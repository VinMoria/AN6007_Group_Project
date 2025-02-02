from flask import Flask, request, jsonify, render_template, send_file, send_from_directory
from user import User
import json
import os
import pandas as pd

# 初始化存储空间

# 自增的生成ID
current_id = 0

# 存储用户的dictionary
user_dict = {
	# "00000001":user_object,
}

# 存储底层数据的dataframe
raw_df = pd.DataFrame(
	columns=['user_id', 'area', "username", 'timestamp', 'reading'])


app = Flask(__name__)


# 首页
@app.route('/')
def index():
	return render_template('index.html')


# 新用户注册
@app.route('/register', methods=['POST'])
def register():
	global current_id
	global user_dict

	try:
		# 接收前端数据
		receive_data = request.get_json()
		username = receive_data['username']
		area = receive_data['area']

		# 生成用户ID
		current_id += 1
		new_user_id = str(current_id).zfill(8)

		# 创建用户对象
		new_user = User(username, area, new_user_id)
		user_dict[new_user_id] = new_user
		print(user_dict)

		# 返回用户ID
		return jsonify({'user_id': new_user_id, 'status': 'success'})
	except Exception as e:
		return jsonify({'status': 'error', 'message': str(e)})


# 接收电表读数
@app.route('/meter/sendReading', methods=['POST'])
def meter_send_reading():
	global user_dict
	global raw_df
	try:
		receive_data = request.get_json()
		timestamp = receive_data['timestamp']
		reading = receive_data['reading']
		user_id = receive_data['user_id']
		user_dict[user_id].receive_reading(timestamp, reading)
		raw_df.loc[len(raw_df)] = [user_id, user_dict[user_id].area,
                             user_dict[user_id].username, timestamp, reading]
		print(raw_df)
		return jsonify({'status': 'success'})
	except Exception as e:
		return jsonify({'status': 'error', 'message': str(e)})


# 获取用户数据
@app.route('/user/getData', methods=['GET'])
def get_user_data():
	try:
		global user_dict
		user_id = request.args.get('user_id')
		user_data = user_dict[user_id].get_data()
		ans = dict(user_data, **{'status': 'success'})
		return jsonify(ans)
	except Exception as e:
		return jsonify({'status': 'error', 'message': str(e)})


if __name__ == '__main__':
	app.run(debug=True)
	print("Hello")

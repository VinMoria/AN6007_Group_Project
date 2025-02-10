from flask import Flask, request, jsonify, render_template, send_file, send_from_directory
import json
import os
import pandas as pd
from Service import Service



# 初始化服务
service = Service()

app = Flask(__name__)


# 新用户注册
@app.route('/register', methods=['POST'])
def register():
	global current_id
	global user_dict

	try:
		# 解析入参
		receive_data = request.get_json()
		username = receive_data['username']
		area = receive_data['area']

		# 注册用户
		new_user_id = service.register(username, area)

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
		# 解析入参
		receive_data = request.get_json()
		timestamp = receive_data['timestamp']
		reading = receive_data['reading']
		user_id = receive_data['user_id']

		# 更新用户数据	
		service.receive_reading(user_id, timestamp, reading)

		return jsonify({'status': 'success'})
	except Exception as e:
		return jsonify({'status': 'error', 'message': str(e)})


# 获取用户数据，用于用户dashboard界面
@app.route('/user/getData', methods=['GET'])
def get_user_data():
	global user_dict
	try:
		# 解析入参
		user_id = request.args.get('user_id')

		# 获取用户数据
		user_data = service.get_user_display_data(user_id)

		# 组装返回数据
		ans = dict(user_data, **{'status': 'success'})
		return jsonify(ans)
	except Exception as e:
		return jsonify({'status': 'error', 'message': str(e)})
	


#TODO 管理员相关的功能可以放到后面再说
# 允许管理员根据筛选条件获取csv的原始数据
@app.route('/admin/getRaw',methods=["POST"])
def admin_get_raw_():
	try:
		global raw_df
		receive_data = request.get_json()
		# TODO 根据传入的参数进行筛选

		# 生成csv文件
		os.makedirs("temp", exist_ok=True)
		file_path = "temp/raw_data.csv"
		raw_df.to_csv(file_path, index=False)
		return send_file(file_path, as_attachment=True)
	
	except Exception as e:
		return jsonify({'status': 'error', 'message': str(e)})


# 允许管理员获取UserID和AreaID的目录，用于筛选时显示全量
@app.route('/admin/catalogue', methods=["GET"])
def admin_get_catalogue():
	try:
		global user_id_set
		global area_set
		return jsonify({'user_id_set': list(user_id_set), 'area_set': list(area_set)})
	except Exception as e:
		return jsonify({'status': 'error', 'message': str(e)})


if __name__ == '__main__':
	app.run(debug=True)

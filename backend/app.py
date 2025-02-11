from flask import Flask, request, jsonify, send_file
from UserService import UserService
from io import BytesIO
from apscheduler.schedulers.background import BackgroundScheduler


# 初始化服务
user_service = UserService()
app = Flask(__name__)

# 创建定时任务
scheduler = BackgroundScheduler()
scheduler.add_job(func=user_service.store_data, trigger="interval", seconds=5)
scheduler.start()


# 新用户注册
@app.route('/user/register', methods=['POST'])

def register():
	global current_id
	global user_dict

	try:
		# 解析入参
		receive_data = request.get_json()
		username = receive_data['username']
		area = receive_data['area']

		# 注册用户
		new_user_id = user_service.register(username, area)

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
		user_service.receive_reading(user_id, timestamp, reading)

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
		user_data = user_service.get_user_display_data(user_id)

		# 组装返回数据
		ans = dict(user_data, **{'status': 'success'})
		return jsonify(ans)
	except Exception as e:
		return jsonify({'status': 'error', 'message': str(e)})
	

# 允许管理员获取csv的原始数据
@app.route('/admin/getRaw',methods=["GET"])
def admin_get_raw_():
	try:
		# 使用 BytesIO 替代 StringIO
		buffer = BytesIO()
		user_service.raw_df.to_csv(buffer, index=False)
		
		# 将指针移到开始
		buffer.seek(0)
		
		return send_file(
			buffer,
			mimetype='text/csv',
			as_attachment=True,
			download_name='raw_data.csv'
		)
	
	except Exception as e:
		return jsonify({'status': 'error', 'message': str(e)})


# 允许管理员获取UserID和AreaID的目录，用于筛选时显示全量
@app.route('/admin/catalogue', methods=["GET"])
def admin_get_catalogue():
	try:
		user_id_set = user_service.user_id_set
		area_set = user_service.area_set
		return jsonify({'user_id_set': list(user_id_set), 'area_set': list(area_set)})
	except Exception as e:
		return jsonify({'status': 'error', 'message': str(e)})
	
@app.route('/admin/query', methods=["POST"])
def admin_query():
	try:
		# 解析入参
		receive_data = request.get_json()
		start_time = receive_data['start_time']
		end_time = receive_data['end_time']
		area = receive_data['area']
		period_type = receive_data['period_type']

		#查询数据
		ans = user_service.admin_query(start_time, end_time, area, period_type)
		return jsonify({'status': 'success', 'data': ans})
	
	except Exception as e:
		return jsonify({'status': 'error', 'message': str(e)})


if __name__ == '__main__':
	try:
		app.run(debug=True)
	finally:
		scheduler.shutdown()

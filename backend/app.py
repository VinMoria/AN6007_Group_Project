from flask import Flask, request, jsonify, send_file
from UserService import UserService
from io import BytesIO
from apscheduler.schedulers.background import BackgroundScheduler
from pathlib import Path
import pickle
from datetime import datetime
import zipfile
from SimpleLog import SimpleLog


# 配置日志
logger = SimpleLog("records")

# 确保records目录存在
Path("records").mkdir(exist_ok=True)

# 存储数据
def store_data(user_service):
	# 确保backup目录存在
	backup_dir = Path("backup")
	backup_dir.mkdir(exist_ok=True)

	# 删除旧的备份文件
	for old_file in backup_dir.glob("user_service_*.pkl"):
		old_file.unlink()

	# 将user_service直接存储为二进制文件
	filename = backup_dir / f"user_service_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pkl"
	with open(filename, 'wb') as f:
		pickle.dump(user_service, f)

	print(f"store_data success on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# 加载备份数据
def load_data():
	# 检查backup目录是否存在且有文件
	backup_path = Path("backup")
	if not backup_path.exists() or not any(backup_path.iterdir()):
		return

	user_service_file = next(backup_path.glob("user_service_*.pkl"))
	with open(user_service_file, 'rb') as f:
		user_service = pickle.load(f)
	print(f"load_data success")

	return user_service


# 初始化服务
# 尝试数据恢复
user_service = load_data()
if user_service is None:
	user_service = UserService()

app = Flask(__name__)

# 定时保存UserService，用于恢复
scheduler = BackgroundScheduler()
scheduler.add_job(func=store_data, args=[user_service], trigger="interval", seconds=5)
scheduler.start()

# 是否在批量处理
in_batch_job = False


# 新用户注册
@app.route('/user/register', methods=['POST'])
def register():
	global in_batch_job
	logger.info("Received request at /user/register")
	if in_batch_job:
		logger.warning("System is in batch job mode, rejecting request")
		return jsonify({'status': 'error', 'message': 'System is maintaining, please try again later.'})

	global current_id
	global user_dict

	try:
		# 解析入参
		receive_data = request.get_json()
		username = receive_data['username']
		area = receive_data['area']
		logger.info(f"Registering new user: {username} in area {area}")

		# 注册用户
		new_user_id = user_service.register(username, area)
		logger.info(f"Successfully registered user with ID: {new_user_id}")

		# 返回用户ID
		return jsonify({'user_id': new_user_id, 'status': 'success'})
	except Exception as e:
		logger.error(f"Error in register: {str(e)}")
		return jsonify({'status': 'error', 'message': str(e)})


# 接收电表读数
@app.route('/meter/sendReading', methods=['POST'])
def meter_send_reading():
	global in_batch_job
	logger.info("Received request at /meter/sendReading")
	if in_batch_job:
		logger.warning("System is in batch job mode, rejecting request")
		return jsonify({'status': 'error', 'message': 'System is maintaining, please try again later.'})

	global user_dict
	global raw_df
	try:
		# 解析入参
		receive_data = request.get_json()
		timestamp = receive_data['timestamp']
		reading = receive_data['reading']
		user_id = receive_data['user_id']
		logger.info(f"Receiving reading from user {user_id}: {reading} at {timestamp}")

		# 更新用户数据	
		user_service.receive_reading(user_id, timestamp, reading)
		logger.info("Successfully updated user reading")

		return jsonify({'status': 'success'})
	except Exception as e:
		logger.error(f"Error in meter_send_reading: {str(e)}")
		return jsonify({'status': 'error', 'message': str(e)})


# 获取用户数据，用于用户dashboard界面
@app.route('/user/getData', methods=['GET'])
def get_user_data():
	global in_batch_job
	logger.info("Received request at /user/getData")
	if in_batch_job:
		logger.warning("System is in batch job mode, rejecting request")
		return jsonify({'status': 'error', 'message': 'System is maintaining, please try again later.'})

	global user_dict
	try:
		# 解析入参
		user_id = request.args.get('user_id')
		logger.info(f"Fetching data for user {user_id}")

		# 获取用户数据
		user_data = user_service.get_user_display_data(user_id)
		logger.info("Successfully retrieved user data")

		# 组装返回数据
		ans = dict(user_data, **{'status': 'success'})
		return jsonify(ans)
	except Exception as e:
		logger.error(f"Error in get_user_data: {str(e)}")
		return jsonify({'status': 'error', 'message': str(e)})
	

# 批处理
@app.route('/batch', methods=["GET"])
def batch():
	global in_batch_job
	logger.info("Received request at /batch")
	try:
		in_batch_job = True
		logger.info("Starting batch job")
		user_service.batch_job()
		logger.flush()
		# 压缩records目录
		record_dir = Path("records")
		record_dir.mkdir(exist_ok=True)
		
		# 创建内存中的压缩文件
		buffer = BytesIO()
		with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
			for file in record_dir.glob("*"):
				zipf.write(file, file.name)
		
		# 将指针移到开始
		buffer.seek(0)
		
		# 清空records目录
		for file in record_dir.glob("*"):
			file.unlink()

		in_batch_job = False
		# 返回压缩文件作为附件
		return send_file(
			buffer,
			mimetype='application/zip',
			as_attachment=True,
			download_name='records.zip'
		)
	
	
	except Exception as e:
		logger.error(f"Error in batch: {str(e)}")
		return jsonify({'status': 'error', 'message': str(e)})


if __name__ == '__main__':
	try:
		app.run(debug=True)
	finally:
		scheduler.shutdown()


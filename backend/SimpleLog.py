import time
import os


class SimpleLog:
    def __init__(self, path):
        self.memory_list = []
        self.path = path

    def info(self, message):
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log_message = f"{now} - INFO: {message}"
        self.memory_list.append(log_message)
        print(log_message)

    def warning(self, message):
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log_message = f"{now} - WARNING: {message}"
        self.memory_list.append(log_message)
        print(log_message)

    def error(self, message):
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log_message = f"{now} - ERROR: {message}"
        self.memory_list.append(log_message)
        self.flush()
        print(log_message)
        
    def flush(self):
        # 如果文件不存在，则创建
        if not os.path.exists(f"{self.path}"):
            os.makedirs(f"{self.path}")
            
		# 追加写入
        with open(f"{self.path}/app.log", "a") as f:
            for log_message in self.memory_list:
                f.write(log_message + "\n")
                
        # 清空内存缓冲区
        self.memory_list = []
        
        

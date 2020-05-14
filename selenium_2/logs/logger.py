import logging
from logging.config import fileConfig
import os
from datetime import datetime

dir_path = './logs/'
# dir_path = 'C:/Users/Mia/PycharmProjects/selenium_2/logs/' # 設定 logs 目錄
filename = "{:%Y-%m%d-%H%M}".format(datetime.now()) + '.log' # 設定檔名

# 層級順序：debug、info、warning、error、critical
# 若將logging 的 level 設為 logging.INFO 的時候，所有debug()的訊息將會被自動忽略，其餘顯示
# 若將logging 的 level 設成 logging.ERROR 的時候，所有 debug(), info(), warning()的訊息將會被忽略，error、critical會顯示
# 若無設定，logging 的 level 預設會是 logging.WARNING
 
# fileConfig('logging_config.ini')
# logger = logging.getLogger('MainLogger')

# fh = logging.FileHandler('{:%Y-%m%d-%H%M}.log'.format(datetime.now()))
# formatter = logging.Formatter(fmt='%(asctime)s | %(levelname)-8s | %(lineno)04d | %(message)s',
# 								datefmt='%Y-%m-%d %H:%M')

# fh.setFormatter(formatter)
# logger.addHandler(fh) # 新增FileHandler

# logger = logging.getLogger()
# logger.debug('often makes a very good meal of %s', 'visiting tourists')

# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s %(levelname)s %(message)s',
#                     datefmt='%Y-%m-%d %H:%M',
#                     handlers=[logging.FileHandler('my.log', 'w', 'utf-8'), ])

def create_logger(log_folder):
	# config
	logging.captureWarnings(True) # 捕捉 py waring message
	formatter = logging.Formatter(fmt='%(asctime)s | %(levelname)-8s | %(lineno)04d | %(message)s',
								datefmt='%Y-%m-%d %H:%M')
	my_logger = logging.getLogger('py.warnings') # 捕捉 py waring message
	my_logger.setLevel(logging.INFO)

	# 若不存在目錄則新建
	if not os.path.exists(dir_path+log_folder):
		os.makedirs(dir_path+log_folder)

	# file handler
	fileHandler = logging.FileHandler(dir_path+log_folder+'/'+filename, 'w', 'utf-8')
	fileHandler.setFormatter(formatter)
	my_logger.addHandler(fileHandler)

	# console handler
	consoleHandler = logging.StreamHandler()
	consoleHandler.setLevel(logging.DEBUG)
	consoleHandler.setFormatter(formatter)
	my_logger.addHandler(consoleHandler)

	return my_logger
	#################################################################
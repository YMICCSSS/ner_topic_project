from logs.logger import create_logger
import requests
requests.packages.urllib3.disable_warnings()    # 關閉警告訊息
 
def main(logger):
    url = "https://tw.yahoo.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    results = requests.get(url, verify=False, headers=headers)
    results.encoding = 'utf-8'  # 修改編碼
    data = results.text
    logger.info(data)   # 將 yahoo html 記到 log file 中
 
if __name__ == '__main__':
    logger = create_logger('tutorial')  # 在 logs 目錄下建立 tutorial 目錄
    logger.info('Start \n')
 
    try:
        main(logger)
    except Exception as e:
        logger.exception("Runtime Error Message:")
 
    logger.info("Export Done! \n")
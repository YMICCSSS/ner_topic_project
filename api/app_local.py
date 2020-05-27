#!/usr/bin/env python
# coding: utf-8

# In[21]:


# 引用Web Server套件
from flask import Flask, request
from flask_cors import CORS,cross_origin
import json
import pymysql

# 設定Server啟用細節
app = Flask(__name__,static_url_path = "/images" , static_folder = "./images/" )
# https://medium.com/@charming_rust_oyster_221/flask-%E5%AF%A6%E7%8F%BE-cors-%E8%B7%A8%E5%9F%9F%E8%AB%8B%E6%B1%82%E7%9A%84%E6%96%B9%E6%B3%95-c51b6e49a8b5
# 同源政策(Same-origin policy)限制了程式碼(特別是Ajax)和不同網域資源間的互動，對本地html而言，Web API是跨來源的資源。
# 若資源是允許被任不同網域資源存取，則需要回傳帶有 Access-Control-Allow-Origin 標頭值

# =========== 加CROS方法一 CORS(app) =======================
# cors = CORS(app) # 這裡面所有@app.route()的請求都允許CORS
# cors = CORS(app, resources={r"/api/*": {"origins": "*"}}) # 只有路徑為/api/*的請求才允許CORS
# 加了這句只有route是'/api'才允許，route("/")就不接受
# app.config['CORS_HEADERS'] = 'Content-Type' # 可以不加
# =========================================================
# =========== 加CROS方法二 @cross_origin() =================
# 在@app.route()下面加上裝飾器 @cross_origin()
# 只允許特定路徑的請求
# =========================================================


# 啟動server對外接口，使外面能連進來
@app.route("/")
# @cross_origin() # 這個路徑為('/')的請求不允許CROS
def callback():
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    return 'OK'


@app.route('/api', methods=['GET'])
@cross_origin() # 只對路徑為('/api')的請求允許CROS
def getapi():
    if 'name' in request.args:
        name = request.args['name']
        road = request.args['road']
        return getdata(name, road)
    else:
        return "Error: No storeid provided. Please specify a storeid."


# In[22]:


def getdata(name, road):
    # ===== 連結MySQL =====
    with open('./password.txt', 'r', encoding='utf8') as f:
        password = f.read()

    # 設定好連線資訊，
    connection = pymysql.connect(
        host = '34.66.10.69',
        user = 'tibame',
        passwd = password,
        db = 'Store_db',
        charset = 'utf8',
        port = 3306
    )
    # connection = pymysql.connect(
    #     host = '35.247.162.117',
    #     user = 'root',
    #     passwd = password,
    #     db = 'dining_rec',
    #     charset = 'utf8',
    #     port = 3306
    # )
    # ===== 取得指令操作變數 =====
    c = connection.cursor() # 可以有多個人連線，有連線人數上限

    # ============ select =============
    tablename = 'stores'
    para = "%" + road + "%"

    sql = '''
    SELECT * from `{tablename}` where name = '{name}' and addr like '{para}'
    '''.format(tablename=tablename, name=name, para=para)

    c.execute(sql)
    lst_columns = [i[0] for i in c.description]
    x = c.fetchall()
    dic_data = {}
    for row in x:
        for col in range(len(row)):
            dic_data[lst_columns[col]] = row[col]

    # 轉成json回傳
    j = json.dumps(dic_data, ensure_ascii=False) # 中文
    print(type(j), j)

    # # ===== 關閉MySQL連線 =====
    connection.commit() # 若是"新增"、"刪除"、"修改"，要commit才會執行指令
    connection.close()
    return j


# In[23]:


'''
啟動Server
'''
if __name__ == "__main__":
    app.run(host='0.0.0.0')


# In[24]:


'''
Application 運行（heroku版）
'''

# import os
# if __name__ == "__main__":
#     app.run(host='0.0.0.0',port=os.environ['PORT'])


# In[ ]:





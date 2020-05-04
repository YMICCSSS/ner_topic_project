#!/usr/bin/env python
# coding: utf-8

# In[21]:


# 引用Web Server套件
from flask import Flask, request
import json
import pymysql

# 設定Server啟用細節
app = Flask(__name__,static_url_path = "/images" , static_folder = "./images/" )

# 啟動server對外接口，使外面能連進來
@app.route("/")
def callback():
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    return 'OK'

@app.route('/api', methods=['GET'])
def getapi():
    if 'storeid' in request.args:
        storeid = request.args['storeid']
        return getdata(storeid)
    else:
        return "Error: No storeid provided. Please specify a storeid."


# In[22]:


def getdata(storeid):
    # ===== 連結MySQL =====
    with open('./password.txt', 'r', encoding='utf8') as f:
        password = f.read()

    # 設定好連線資訊，
    connection = pymysql.connect(
        host = '35.247.162.117',
        user = 'root',
        passwd = password,
        db = 'dining_rec',
        charset = 'utf8',
        port = 3306
    )

    # ===== 取得指令操作變數 =====
    c = connection.cursor() # 可以有多個人連線，有連線人數上限

    # ============ select =============
    # ['id_store', 'id_category', 'store_name', 'zone', 'address', 'reviews', 'stars', 'star_mean', 'star_std', 'star_mad', 'reviews_by_month', 'stars_by_month', 'img']
    tablename = 'store'
    col_id = 'id_store'
    val_id = storeid
    sql_select = '''
    SELECT * from `{tablename}` where `{col_id}` = {val_id}
    '''.format(tablename=tablename, col_id=col_id, val_id=val_id)
    c.execute(sql_select)
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
# if __name__ == "__main__":
#     app.run(host='0.0.0.0')


# In[24]:


'''
Application 運行（heroku版）
'''

import os
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=os.environ['PORT'])


# In[ ]:





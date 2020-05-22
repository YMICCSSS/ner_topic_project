# -*- coding: utf-8 -*-
# 匯入必要模組
from sqlalchemy import create_engine
import csv
import pymysql
import codecs
import pandas as pd
import os
import glob
# 初始化資料庫連線，使用pymysql模組
# MySQL的使用者：tibame, 密碼:tibame2020, 埠：3306,資料庫：Storedata2 ip=34.66.10.69
engine = create_engine('mysql+pymysql://tibame:tibame2020@34.66.10.69:3306/Store_db')

# 查詢語句，選出employee表中的所有資料
# sql = '''
# select * from all_data;
# '''
# read_sql_query的兩個引數: sql語句， 資料庫連線
# df = pd.read_sql_query(sql, engine)
# 輸出employee表的查詢結果
# print(df)

#取出資料夾中，各區的名子
x = os.listdir("台北市")
zonename = x[1:]
dir =  {x:i for x,i in enumerate(zonename)} #由字典建立各區索引
print(zonename)

#取出各區中的每一個店家的csv
for i,write in enumerate(zonename):
    all = []
    getname = glob.glob(r"台北市\{}\*_review.csv".format(write))
    for i,ls in enumerate(getname):
        new = ls.replace(r"台北市\{}".format(write),"")
        # 因為"\"放在str中最後一個字用replace會出錯，所以才要分開寫
        new = new.replace("\\","")
        all.append(new)

    for i in all:
        if i !="豪香熱炒_review.csv":
            df = pd.read_csv("台北市"+"\{}\\".format(write)+i)
            print(write+" "+i+" "+"讀取成功")

    # 將新建的DataFrame儲存為MySQL中的資料表，不儲存index列,如果存在就追加
            df.to_sql('reviews', engine, if_exists='append',index= False)
            print(write+" "+i+" "+"寫入成功")
        else:
            continue
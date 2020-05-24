#cjo4
from sqlalchemy import create_engine
import csv
import pymysql
import codecs
import pandas as pd
import os
import glob
#初始化資料庫連線，使用pymysql模組
#MySQL的使用者：tibame, 密碼:tibame2020, 埠：3306,資料庫：Store_db
engine = create_engine('mysql+pymysql://tibame:tibame2020@34.66.10.69:3306/Store_db')

#店家清單路徑
df = pd.read_csv("台北市\stores_1.csv")
df = df.drop(["id"],axis=1)
#刪除重複的欄位
df.drop_duplicates("addr","first",inplace=True)


df.to_sql('stores', engine, if_exists='append', index=False)



print("寫入成功")



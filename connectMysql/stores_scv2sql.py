#cjo4
from sqlalchemy import create_engine
import pandas as pd
import pymysql

#初始化資料庫連線，使用pymysql模組
#MySQL的使用者：tibame, 密碼:tibame2020, 埠：3306,資料庫：Store_db
engine = create_engine('mysql+pymysql://tibame:tibame2020@34.66.10.69:3306/Store_db')


#店家清單路徑
df = pd.read_csv("台北市\stores.csv")
df = df.drop(["id"],axis=1)
#刪除重複的欄位
df.drop_duplicates("addr","first",inplace=True)

db = pymysql.connect("34.66.10.69","tibame","tibame2020","Store_db" )
cursor = db.cursor()
#建立一個店家名稱加上區域的名稱來判斷是否是唯一的店家，用在之後評論家上sotre_id
# 創建店家清單字典

number = "select `addr`,`name` from `stores`"
cursor.execute(number)
data = cursor.fetchall()

data= [data[i][0] for i in range(len(data))]

series_tf =  df["addr"].isin(data)
#~ = 將True False 反轉
df = df[~series_tf]
df.to_sql('stores', engine, if_exists='append', index=False)

print("寫入成功")



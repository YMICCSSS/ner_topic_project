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
# MySQL的使用者：tibame, 密碼:tibame2020, 埠：3306,資料庫：Store_db ip=34.66.10.69
engine = create_engine('mysql+pymysql://tibame:tibame2020@34.66.10.69:3306/Store_db')

#建立pymysql物件，使我們可以用pymysql操作資料庫
db = pymysql.connect("34.66.10.69","tibame","tibame2020","Store_db" )
cursor = db.cursor()

##助教說資料庫存取次數少一點比較好所以先建一個字典,如果mysql語法有用{}，{}一定要加引號''才讀得到
#建立一個店家名稱加上區域的名稱來判斷是否是唯一的店家，用在之後評論家上sotre_id
number = "select `stores_id`,`name`,`district` from `stores`"
cursor.execute(number)
data = cursor.fetchall()
print(data[0])
print(data[0][0])
# 創建店家清單字典
data= {data[i][1]+data[i][2]:data[i][0] for i in range(len(data))}

data2=[]
#建立一個論目前有的storeid的字典
number2 = "select distinct `stores_id` from `reviews`"
cursor.execute(number2)
data2 = cursor.fetchall()
#創建已有的評論中不重複的store_id的字典
data2= [data2[i][0] for i in range(len(data2))]

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
        new = ls.replace("台北市\{}\\".format(write),"")
        # 因為"\"放在str中最後一個字用replace會出錯，所以才要分開寫
        # new = new.replace("\\","") 這個不用看，先放在這邊
        all.append(new)

    for i in all:
        df = pd.read_csv("台北市"+"\{}\\".format(write)+i)
        print(write+" "+i+" "+"讀取成功")
        #讀取到這個檔案在Mysql中的id,並加到所有評論中的store_id欄位
        i = i.replace("_review.csv","")
        print(i)
        print(i+write in data)
        if (i+write in data) == True:
            print("店家id ",data[i+write])
            df["stores_id"] = [data[i+write]]*len(df)
            df = df.drop(['id'], axis=1)
            print(df)

            #如果店家清單的store_id ，不存在於現有評論的store_id中，這筆csv才寫入資料庫
            if not (data[i+write] in data2) ==True :
            # df = df.rename(columns={"id": "stores_id"})->改名備用程式
            # 將新建的DataFrame儲存為MySQL中的資料表，不儲存index列,如果存在就追加
                df.to_sql('reviews', engine, if_exists='append',index= False)
                print(write+" "+i+" "+"寫入成功")
            else:
                print("這家重複不寫入")
        else:
            continue


db.close()




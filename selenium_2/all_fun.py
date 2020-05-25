import time, datetime
from dateutil.relativedelta import relativedelta
import os
import re
import pandas as pd


def find_tags(driver, tagName, parent=None, logger=None):
    msg = '開始 find_tags:' + tagName
    logger.info(msg)
    count = 1
    taglen = 0
    time.sleep(2)
    tags = driver.find_elements_by_class_name(tagName)

    if tagName == 'section-layout-flex-horizontal': # 排序的下拉式選單tag會抓到2個，第二個才是下拉式選單
        taglen = 1

    while not len(tags) > taglen:
        if count > 100:
            msg = '已經重新找100次tag了，放棄'
            logger.info(msg)
            return tags

        time.sleep(1)
        if parent == None:
            tags = driver.find_elements_by_class_name(tagName)
        else:
            tags = parent.find_elements_by_class_name(tagName) 
        msg = '第' + str(count) + '次重新抓tag:' + tagName
        logger.info(msg)
        count += 1
    time.sleep(2)
    return tags

# ==================== 儲存店家清單.csv、店家評論.csv ========================================
def save_csv(path, lst, logger=None):
    if len(lst) == 0:
        return []
    lst.sort(key=lambda x: x['tmpid'], reverse=True)
    df = pd.DataFrame.from_dict(lst, orient='columns')
    print('df_now:\n', df)

    df.insert(loc=0, column='id', value=range(1,len(df.index)+1)) # 插入'id'為第一行
    del df['tmpid']

    if os.path.exists(path): # 如果stores.csv已經存在了，合併新舊dataFrame
        df_ori = pd.read_csv(path, encoding='utf8')
        # print('df_ori:', df_ori)
        saved_latest_id = int(df_ori.iloc[-1]['id']) # 最後一列的id欄位
        newrows = len(df.index)
        df['id'] = pd.Series(range(saved_latest_id + 1, saved_latest_id + newrows + 1))
        df = pd.concat([df_ori, df], ignore_index=False)
        # 店家清單的評論數量佔無法更新，想直接去更新資料庫
    msg = '儲存 dataframe ->.csv，path:' + path
    logger.info(msg)
    # print('df_saved:', df)
    df.to_csv(path, index=False, encoding="utf-8")
    return []

# ==================== 將日期由"1 個月前"-->"2020/04/10形式" ====================
def get_real_date(date):
    now = datetime.datetime.now()
    realdate = now
    subdate = int(date.split(' ')[0])
    if '天' in date:
        realdate = now + relativedelta(days=-subdate)
    if '週' in date:
        realdate = now + relativedelta(weeks=-subdate)
    elif '月' in date:
        realdate = now + relativedelta(months=-subdate)
    elif '年' in date:
        realdate = now + relativedelta(years=-subdate)

    return realdate.strftime('%Y/%m/%d')

# ==================== 檢查店家名稱是否有特殊符號 ====================
# 因為是用店家名稱作為檔案名儲存，若有特殊符號無法存檔，將特殊符號轉換再儲存
def checkName(name, logger=None):
    # 檔名不能含有\/:*?"<>| 符號
    dic_mark = {'\\': '[反斜槓]',
                '/': '[斜槓]',
                '*': '[星號]',
                '?': '[問號]',
                '"': '[雙引號]',
                '<': '[左角括號]',
                '>': '[右角括號]',
                '|': '[豎線]'}
    newname = name
    lst_mark = []
    for s in name:
        if s in dic_mark: # 檢查店名是否有含特殊符號
            lst_mark.append(s)
    if len(lst_mark) > 0:
        for mark in lst_mark:
            newname = newname.replace(mark, dic_mark[mark])
        msg = '原始店名含有特殊符號：' + name + '，修正後店名' + newname
        logger.info(msg)
    return newname
    
def get_road(addr):
    addr = re.sub(r"\b\d+..市..區", '', addr)
    addr = re.sub(r"..區..市\d+\b", '', addr)
    return addr

def check_district_info(addrinfo):
    if '區 ' in addrinfo or '鎮' in addrinfo or '鄉' in addrinfo or ('宜蘭市' in addrinfo):
        return True
    else:
        return False
import time, datetime
from dateutil.relativedelta import relativedelta
import os
import pandas as pd
from selenium.webdriver import Chrome

def find_tags(driver, tagName, parent=None):
    print('開始 find_tags:', tagName)
    count = 1
    taglen = 0
    time.sleep(2)
    tags = driver.find_elements_by_class_name(tagName)

    if tagName == 'section-layout-flex-horizontal': # 排序的下拉式選單tag會抓到2個，第二個才是下拉式選單
        taglen = 1

    while not len(tags) > taglen:
        if count > 100:
            print('已經重新找100次tag了，放棄')
            break

        time.sleep(1)
        if parent == None:
            tags = driver.find_elements_by_class_name(tagName)
        else:
            tags = parent.find_elements_by_class_name(tagName)
        print('第' + str(count) + '次重新抓tag:', tagName)
        count += 1
    time.sleep(2)
    return tags


def save_csv(path, lst):
    if len(lst) == 0:
        return
    lst.sort(key=lambda x: x['tmpid'], reverse=True)
    df = pd.DataFrame.from_dict(lst, orient='columns')
    print('df_now:', df)

    df.insert(loc=0, column='id', value=range(1,len(df.index)+1)) # 插入'id'為第一行
    del df['tmpid']

    if os.path.exists(path): # 如果stores.csv已經存在了，合併新舊dataFrame
        df_ori = pd.read_csv(path, encoding='utf8')
        print('df_ori:', df_ori)
        saved_latest_id = int(df_ori.iloc[-1]['id']) # 最後一列的id欄位
        newrows = len(df.index)
        df['id'] = pd.Series(range(saved_latest_id + 1, saved_latest_id + newrows + 1))
        df = pd.concat([df_ori, df], ignore_index=False)
        # 店家清單的評論數量佔無法更新，想直接去更新資料庫

    print('儲存 dataframe ->.csv，path:', path)
    print('df_saved:', df)
    df.to_csv(path, index=False, encoding="utf-8")


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


def checkName(name):
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

        print('原始店名含有特殊符號：', name, '，修正後店名', newname)
    return newname

def start():
    driver = Chrome('./chromedriver')

    # url = 'https://www.google.com.tw/maps'
    # url = 'https://www.google.com.tw/maps/@25.0422976,121.5238281,17.29z' # 中正區北商位置
    # url = 'https://www.google.com.tw/maps/@25.029295,121.5439541,14.9z' # 信義區北醫位置
    # url = 'https://www.google.com.tw/maps/@25.0680263,121.5239719,16z' # 中山區中山國小位置
    url = 'https://www.google.com.tw/maps/@25.0476077,121.5256058,17.02z'  # 中山區長安東路

    driver.get(url)
    start_time = time.time()
    time.sleep(2)  # 等待3秒
    # ================= 搜尋條件 =================
    # district = '中山區' # 這個區的餐廳才拿資料
    city = '台北市'
    keyword = '熱炒'  # 關鍵字
    totalpage = 10  # 總共要下載到幾頁的資料
    # ===========================================
    # =========== global 所需變數 =================
    district = ''
    folder = ''
    stores_path = ''
    folder_keyword = './csv/' + keyword + '/'
    # folder = './csv/' + district + keyword + '/'
    # stores_path = folder + 'stores.csv'
    if not os.path.exists(folder_keyword):
        os.mkdir(folder_keyword)
    page = 0
    print('輸入搜尋關鍵字:', keyword)
    lst_store = []
    dic_store = {}
    lst_store_csv = []
    # df_stores = pd.DataFrame()

    lst_review = []
    dic_review = {}
    # df_reviews = pd.DataFrame()
    bfinal = False
    # ===========================================

    dic_tag = {
        'input': 'tactile-searchbox-input',
        'stores': 'section-result',
        'store_info': 'section-info-action-button',
        'reviews_div': 'section-rating-term-list',
        'allreviews': 'widget-pane-link',
        'label': 'aria-label',
        'ddl': 'section-layout-flex-horizontal',
        'sort_item': 'action-menu-entry',
        'loading': 'section-loading',
        'review_date': 'section-review-publish-date',
        'review_star': 'section-review-stars',
        'review_text': 'section-review-review-content',
        'price': 'section-result-cost',
        'back_store': 'ozj7Vb3wnYq__action-button-clickable',
        'back_list': 'section-back-to-list-button',
        'next_page': 'n7lv7yjyC35__section-pagination-button-next'
    }

    # =============== Start =====================
    input = find_tags(driver, dic_tag['input'])[0]
    input.send_keys(keyword)

    print('點擊搜尋')
    driver.find_element_by_id('searchbox-searchbutton').click()
    time.sleep(5)

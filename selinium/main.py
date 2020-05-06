from selenium.webdriver import Firefox
import time,datetime
import traceback, os
import pandas as pd
from selenium.webdriver import Chrome
from dateutil.relativedelta import relativedelta
# driver = Firefox(executable_path = './geckodriver')
driver = Chrome('./chromedriver')

# url = 'https://www.google.com.tw/maps'
url = 'https://www.google.com.tw/maps/@25.0422976,121.5238281,17.29z' # 北商位置

driver.get(url)
start_time = time.time()
time.sleep(3) # 等待3秒
# ================= 搜尋條件 =================
district = '大同區' # 這個區的餐廳才拿資料
keyword = '大腸麵線'    # 關鍵字
totalpage = 1      # 總共要下載到幾頁的資料
# ===========================================
# =========== global 所需變數 =================
folder = './csv/' + district + keyword + '/'
stores_path = folder + 'stores.csv'
if not os.path.exists(folder) :
    os.mkdir(folder)
page = 0
print('輸入搜尋關鍵字:', keyword)
lst_store = []
dic_store = {}
df_stores = pd.DataFrame()

lst_review = []
dic_review = {}
df_reviews = pd.DataFrame()
bfinal = False
# ===========================================
def find_tags(tagName, parent=None):
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

# 目前位置
# mylocation = driver.find_elements_by_id('widget-mylocation')
# print(len(mylocation))
# while len(mylocation) == 0:
#     print('mylocation')
#     mylocation = driver.find_elements_by_id('widget-mylocation')
# mylocation[0].click()

dic_tag = {
    'input':'tactile-searchbox-input',
    'stores':'section-result',
    'store_info':'section-info-action-button',
    'reviews_div':'section-rating-term-list',
    'allreviews':'widget-pane-link',
    'label':'aria-label',
    'ddl':'section-layout-flex-horizontal',
    'sort_item':'action-menu-entry',
    'loading':'section-loading',
    'review_date':'section-review-publish-date',
    'review_star':'section-review-stars',
    'review_text':'section-review-review-content',
    'price':'section-result-cost',
    'back_store':'ozj7Vb3wnYq__action-button-clickable',
    'back_list':'section-back-to-list-button',
    'next_page':'n7lv7yjyC35__section-pagination-button-next'
}

def save_csv(df, path, lst):
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
    df = pd.read_csv(path, encoding='utf8')

def get_real_date(date):
    now = datetime.datetime.now()
    realdate = now
    subdate = int(date.split(' ')[0])
    if '天' in date:
        realdate = now + relativedelta(days=-subdate)
    elif '月' in date:
        realdate = now + relativedelta(months=-subdate)
    elif '年' in date:
        realdate = now + relativedelta(years=-subdate)

    return realdate.strftime('%Y/%m/%d')

# =============== Start =====================
input = find_tags(dic_tag['input'])[0]
input.send_keys(keyword)

print('點擊搜尋')
driver.find_element_by_id('searchbox-searchbutton').click()
time.sleep(5)

while not bfinal:
    try:
        sessions = find_tags(dic_tag['stores'])
        count_thispage = len(sessions)
        print('sessions數，一開始:', count_thispage)
        count_store = 0
        total_store = 0

        page += 1
        print('進入第', page, '頁')
        if page > totalpage:
            bfinal = True
            break

        for i in range(count_thispage):
            if bfinal:
                print('跳出本頁搜尋列表')
                break
            dic_store = {} # 每個店家的資訊存進dic_store
            choose = False # selenium.common.exceptions.StaleElementReferenceException: Message: stale element reference: element is not attached to the page document

            sessions = find_tags(dic_tag['stores'])

            if sessions[i].get_attribute(dic_tag['label']) != '':
                ad = sessions[i].find_elements_by_class_name('ad-badge')[0] # 會有多個廣告tag，只看第一個
                name = sessions[i].get_attribute(dic_tag['label'])
                pricetag = sessions[i].find_elements_by_class_name(dic_tag['price'])[0].get_attribute(dic_tag['label'])
                price = ''
                if pricetag != None:
                    price = pricetag.split(' ')[-1][0]
                review_path = folder + name + '_review.csv'
                saved_latest_date = ''
                saved_latest_review = ''
                if os.path.exists(review_path):
                    df_cur = pd.read_csv(review_path)
                    saved_latest_date = df_cur.iloc[-1]['date'] # 最後一列的column'date'的值
                    saved_latest_review = df_cur.iloc[-1]['text']
                    print('第'+ str(i+1) + '個店家:', name ,'的評論已經存過，已存的最新評論日期為', saved_latest_date)
                    # continue
                addr = ''
                if 'display' not in ad.get_attribute('style') :
                    print('跳過這個廣告店家:', name)
                    continue # 廣告，跳過

                sessions[i].click()
                print('=== 點擊第'+ str(i+1) + '個店家:', name, '===')

                infolines = find_tags(dic_tag['store_info'])

                for infoline in infolines:
                    addr = infoline.get_attribute(dic_tag['label'])
                    if '地址' in addr:
                        if district in addr:
                            addr = addr.split('、')[-1]
                            print('地址:', addr)
                            choose = True
                            break
                        else:
                            print('不是',district, '跳過')
                if choose:
                    count_store += 1
                    total_store += 1
                    lst_review = [] # 每個店家的所有review存進lst_review
                    dic_store['tmpid'] = total_store
                    dic_store['name'] = name
                    dic_store['price'] = price
                    dic_store['addr'] = addr

                    reviews_div = find_tags(dic_tag['reviews_div']) # 先找到包住"所有評論"tag的框框，再找"所有評論"的tag，若此店家完全無評論就找不到"所有評論的tag"
                    allreviews = reviews_div[-1].find_elements_by_class_name(dic_tag['allreviews']) # 若此店家完全無評論就找不到"所有評論的tag"
                    print('搜尋"所有評論"這個tag')
                    time.sleep(2)
                    try:
                        reviews_test = find_tags(dic_tag['allreviews'])
                        print('fine~~~~~~~~~~')
                    except Exception as e:
                        print('error~~~~~~~~,', type(e), str(e))
                        traceback.print_exc()
                    if len(allreviews) > 0:
                        for j in allreviews:
                            if '評論' in j.get_attribute(dic_tag['label']):
                                j.click()
                                print('已點擊"所有評論"，總共有:', j.get_attribute(dic_tag['label']))
                                sort = find_tags(dic_tag['ddl'])

                                print('點擊選擇排序的下拉式選單:')
                                sort[-1].click() # 第0個是"撰寫評論"，所以選第二個

                                menuitem = find_tags(dic_tag['sort_item'])
                                for item in menuitem:
                                    if item.text == '最新':
                                        item.click()
                                        print('點擊選擇依時間最新來排序')
                                        break

                                print('開始找section-loading')
                                time.sleep(3)
                                loading = driver.find_elements_by_class_name(dic_tag['loading'])

                                loading_count = 0
                                record_date_count = 0 # 記錄評論筆數
                                record_time = 0       # 記錄loading次數
                                while len(loading) != 0:
                                    loading_count += 1
                                    print('loading評論第' + str(loading_count) + '次')
                                    time.sleep(3)
                                    loading = driver.find_elements_by_class_name(dic_tag['loading'])

                                    lstdate = driver.find_elements_by_class_name(dic_tag['review_date'])
                                    time.sleep(2)
                                    if loading_count - record_time >= 30: # 目前loading次數 與 紀錄loading次數 相差 60次以上
                                        if len(lstdate) > record_date_count: # 目前評論數 > 紀錄的評論數-->就更新紀錄的評論數
                                            print('原本紀錄的loading次數:', record_time, ',更新為:', loading_count)
                                            print('原本紀錄的評論數:',record_date_count, ',更新為:', len(lstdate))
                                            record_date_count = len(lstdate)
                                            record_time = loading_count
                                        else:
                                            print('無法載入新的評論，Chrome 掛掉了，放棄載入新的評論', name)
                                            bfinal = True
                                            break
                                    loading_date = lstdate[-1].text
                                    print('saved_latest_date：',saved_latest_date, 'loading_date：', get_real_date(loading_date), get_real_date(loading_date) < saved_latest_date)
                                    if '年' in loading_date and  int(loading_date.split(' ')[0]) > 1:
                                        print('目前最後一個評論已超過二年，不需再往下滑了')
                                        break
                                    elif saved_latest_date != '' and get_real_date(loading_date) < saved_latest_date:
                                        print('目前最後一個評論日期', get_real_date(loading_date), '已 < 最新儲存日期:', saved_latest_date, '，不需再往下滑了')
                                        break
                                    elif len(loading) == 0:
                                        print('沒有section-loading了，停止往下滑')
                                        break
                                    loading[-1].click()

                                each_review = find_tags(dic_tag['review_text'])

                                print('開始顯示所有評論數量:', len(each_review))
                                print('=========================================')

                                stars = driver.find_elements_by_class_name(dic_tag['review_star'])
                                publish_date = driver.find_elements_by_class_name(dic_tag['review_date'])
                                for k in range(len(each_review)):
                                    word = each_review[k].text.split('(原始評論)')
                                    # ======= 每個評論的字典都要先清空，不然會連動到上一個塞進List的dict  =============
                                    dic_review = {}
                                    review_date = publish_date[k].text
                                    review_star = stars[k].get_attribute(dic_tag['label']).split(' ')[1]
                                    dic_review['tmpid'] = k+1
                                    dic_review['date'] = get_real_date(review_date)
                                    dic_review['star'] = review_star
                                    review_text = ''
                                    if each_review[k].text != "":
                                        if len(word) > 1:
                                            review_text = word[0].replace('(由 Google 提供翻譯)', '')
                                        else:
                                            review_text = each_review[k].text

                                    review_text = '"' + review_text.replace('\r', '').replace('\n', '，') + '"'
                                    print('第' + str(k + 1) + '筆:', '日期:', review_date, '星等:', review_star, '評論:',review_text)
                                    dic_review['text'] = review_text

                                    if '年' in publish_date[k].text and  int(publish_date[k].text.split(' ')[0]) > 1:
                                        print('超過二年的評論不使用，擷取評論結束')
                                        break
                                    elif saved_latest_date != '' and get_real_date(review_date) == saved_latest_date and review_text == saved_latest_review:
                                        print('這個評論日期 == 最新儲存日期，且評論內容 == 最新儲存評論內容，擷取評論結束')
                                        break
                                    elif saved_latest_date != '' and get_real_date(review_date) < saved_latest_date:
                                        print('這個評論日期', get_real_date(review_date) , '已 < 最新儲存日期:', saved_latest_date, '，擷取評論結束')
                                        break
                                    elif review_text == '""':
                                        print('空白評論不儲存！')
                                        continue
                                    lst_review.append(dic_review)
                                    print('append:',lst_review)
                                break

                        print('====== 將該店家的review list放進該店家資訊的dic_store ===============')
                        print(lst_review)
                        dic_store['review'] = len(lst_review)  # 將該店家的review list放進該店家資訊的dic_store裡
                        if not os.path.exists(review_path):
                            lst_store.append(dic_store)  # 若該店家已存過就不重複

                        lst_columns = ['編號', '評論日期', '評論星等', '評論內容']
                        print('開始儲存review,', review_path)
                        save_csv(df_reviews, review_path, lst_review)
                    else:
                        print('這個店家完全沒有評論, ', name)

                    if not bfinal:
                        back_store = find_tags(dic_tag['back_store'])
                        back_store[0].click()
                        print('已點擊返回店家資訊:', len(back_store))
                        time.sleep(2)

                if not bfinal:
                    back_list = find_tags(dic_tag['back_list'])
                    back_list[0].click()
                    print('已點擊返回搜尋列表')
                    time.sleep((2))

        print('目前這頁爬完了，換下一頁')
        print('目前在第', page, '頁，已點過的店家數:', count_store)

        lst_columns = ['店名', '地址', '評論']
        print('開始儲存店家list')
        save_csv(df_stores, stores_path, lst_store)

        if bfinal:
            print('跳出while')
            break
        try:
            nextpage = driver.find_element_by_id(dic_tag['next_page'])
            print('已點擊下一頁')
            print(lst_store)
            count_store = 0
            if nextpage.get_attribute('disabled') != 'true':
                nextpage.click()
                time.sleep((2))
            else:
                bfinal = True
                print('最後一頁了')
        except Exception as e:
            bfinal = True
            print(e)
            print('最後一頁了，找不到 next_page tag')
            # traceback.print_exc()
    except Exception as e:
        print(e)
        print('except')
        save_csv(df_stores, stores_path, lst_store)
        traceback.print_exc()
print('結束了~~~~~~~~~~~~~~~~')
time.sleep(5)
end_time = time.time()
total_time = end_time-start_time
# print(time.strftime("%H:%M:%S", total_time))

m, s = divmod(total_time, 60)
h, m = divmod(m, 60)

print ("花費時間，時:%02d, 分:%02d, 秒:%02d" % (h, m, s))
# print('{:d}:{:02d}:{:02d}'.format(h, m, s)) # Python 3
# print(f'{h:d}:{m:02d}:{s:02d}') # Python 3.6+
# driver.close()
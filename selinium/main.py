from selenium.webdriver import Firefox
import time
import traceback, os
import pandas as pd
from selenium.webdriver import Chrome
# driver = Firefox(executable_path = './geckodriver')
driver = Chrome('./chromedriver')

# url = 'https://www.google.com.tw/maps'
url = 'https://www.google.com.tw/maps/@25.0422976,121.5238281,17.29z' # 北商位置

driver.get(url)
start_time = time.time()
time.sleep(3) # 等待3秒
# ================= 搜尋條件 =================
district = '中山區' # 這個區的餐廳才拿資料
keyword = '燒烤'    # 關鍵字
totalpage = 1      # 總共要下載到幾頁的資料
# ===========================================
folder = './csv/' + district + keyword + '/'
stores_path = folder + 'stores.csv'
if not os.path.exists(folder) :
    os.mkdir(folder)
page = 0
print('輸入搜尋關鍵字:', keyword)

def find_tags(tagName):
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
        tags = driver.find_elements_by_class_name(tagName)
        print('第' + str(count) + '次重新抓tag:', tagName)
        count += 1
    return tags

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
    'reviews':'widget-pane-link',
    'label':'aria-label',
    'ddl':'section-layout-flex-horizontal',
    'sort_item':'action-menu-entry',
    'loading':'section-loading',
    'review_date':'section-review-publish-date',
    'review_star':'section-review-stars',
    'review_text':'section-review-review-content',
    'back_store':'ozj7Vb3wnYq__action-button-clickable',
    'back_list':'section-back-to-list-button',
    'next_page':'n7lv7yjyC35__section-pagination-button-next'
}

input = find_tags(dic_tag['input'])[0]
input.send_keys(keyword)

print('點擊搜尋')
driver.find_element_by_id('searchbox-searchbutton').click()
time.sleep(5)
bfinal = False

def save_csv(df, path, lst):
    df = pd.DataFrame.from_dict(lst, orient='columns')

    if os.path.exists(path): # 如果stores.csv已經存在了，合併新舊dataFrame
        df_ori = pd.read_csv(path, encoding='utf8')
        df = pd.concat([df_ori, df], ignore_index=True)

    print('儲存 dataframe ->.csv，path:', path)
    print(df)
    df.to_csv(path, index=True, encoding="utf-8")

def getReview():
    pass

lst_store = []
dic_store = {}
df_stores = pd.DataFrame()

lst_review = []
dic_review = {}
df_reviews = pd.DataFrame()
# id, name, addr, open, star, review, date


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
            choose = False
            # selenium.common.exceptions.StaleElementReferenceException: Message: stale element reference: element is not attached to the page document

            sessions = find_tags(dic_tag['stores'])

            if sessions[i].get_attribute(dic_tag['label']) != '':
                ad = sessions[i].find_elements_by_class_name('ad-badge')[0] # 會有多個廣告tag，只看第一個
                name = sessions[i].get_attribute(dic_tag['label'])
                review_path = folder + name + '_review.csv'
                if os.path.exists(review_path):
                    print('第'+ str(i+1) + '個店家:', name ,'的評論已經存過，直接跳下一家店')
                    continue
                addr = ''
                if 'display' not in ad.get_attribute('style') :
                    print('跳過這個廣告店家:', name)
                    continue # 廣告，跳過
                # if i == 1 :
                #     print('已搜尋'+ str(i) + '個店家了，不想找了休息')
                #     break
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
                    dic_store['id'] = total_store
                    dic_store['name'] = name
                    dic_store['addr'] = addr

                    reviews = find_tags(dic_tag['reviews'])

                    print('搜尋"所有評論"這個tag')
                    time.sleep(2)
                    for j in reviews:
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
                                if '年' in lstdate[-1].text and  int(lstdate[-1].text.split(' ')[0]) > 1:
                                    print('目前最後一個評論已超過二年，不需再往下滑了')
                                    break
                                if len(loading) == 0:
                                    print('沒有section-loading了，停止往下滑')
                                    break
                                loading[-1].click()

                            each_review = find_tags(dic_tag['review_text'])

                            print('開始顯示所有評論數量:', len(each_review))
                            print('=========================================')

                            stars = driver.find_elements_by_class_name(dic_tag['review_star'])
                            publish_date = driver.find_elements_by_class_name(dic_tag['review_date'])
                            for k in range(len(each_review)):
                                if '年' in publish_date[k].text and  int(publish_date[k].text.split(' ')[0]) > 1:
                                    print('超過二年的評論不使用，擷取評論結束')
                                    break

                                word = each_review[k].text.split('(原始評論)')
                                # ======= 每個評論的字典都要先清空，不然會連動到上一個塞進List的dict  =============
                                dic_review = {}
                                review_date = publish_date[k].text
                                review_star = stars[k].get_attribute(dic_tag['label']).split(' ')[1]
                                dic_review['id'] = k+1
                                dic_review['date'] = review_date
                                dic_review['star'] = review_star
                                review_text = ''
                                if each_review[k].text != "":
                                    if len(word) > 1:
                                        review_text = word[0].replace('(由 Google 提供翻譯)', '')
                                    else:
                                        review_text = each_review[k].text

                                review_text = '"' + review_text.replace('\r', '').replace('\n', '，') + '"'
                                # print('第' + str(k + 1) + '筆:', '日期:', review_date, '星等:', review_star, '評論:',review_text)

                                dic_review['text'] = review_text
                                lst_review.append(dic_review)
                            break
                    # break
                    dic_store['review'] = len(lst_review)  # 將該店家的review list放進該店家資訊的dic_store裡
                    lst_store.append(dic_store)

                    lst_columns = ['編號', '評論日期', '評論星等', '評論內容']
                    save_csv(df_reviews, review_path, lst_review)

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
        save_csv(df_stores, stores_path, lst_store)

        if bfinal:
            print('跳出while')
            break

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
    except:
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
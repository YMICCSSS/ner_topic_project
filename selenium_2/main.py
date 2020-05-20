from selenium.webdriver import Firefox
from selenium.webdriver import Chrome
import time
import traceback, os
import pandas as pd
from all_fun import find_tags, save_csv, get_real_date, checkName, get_road
from logs.logger import create_logger
driver = Chrome('./chromedriver')
# driver = Firefox(executable_path = './geckodriver')
# 經度,緯度,zoom縮放，北25.15(士林)、南25(文山)、西121.46(關渡)、東121.6(內湖)
# 緯度0.03跳五次、經度0.05跳三次
# 西南(25,    121.46)-->(25,   121.61)東南
# 西北(25.16,,121.46)-->(25.16,121.61)東北
# ================= 搜尋條件 =================
city = '台北市'
keyword = '熱炒'    # 關鍵字
totalpage = 15      # 總共要下載到幾頁的資料
# ============================================
def geturl():
    try:
        lst_location = []
        # ================== 搜尋中心點的經度、緯度 ================== 
        latitude = 25.15      # 最南邊
        latitude_max = 25.16  # 最北邊
        longitude = 121.6     # 最西邊121.46
        longitude_min = 121.6 # 最東邊121.46
        longitude_max = 121.62
        # ========================================================== 
        latitude_step = 0.03  # 緯度間隔
        longitude_step = 0.05 # 經度間隔
        url_base = 'https://www.google.com.tw/maps/'
        restart_limit = ((latitude_max - latitude)//latitude_step) * ((longitude_max - longitude_min)//longitude_step) + 10
        lst_location = []
        while latitude < latitude_max: # 0, 0.03, 0.06, 0.09, 0.12, 0.15
            while longitude < longitude_max: # 45, 51, 56, 61
                location = '@' + str(round(latitude,2)) + ',' + str(round(longitude,2)) + ',15z' # 經度,緯度,zoom縮放
                msg = '========= 產生url座標:', location, '==========='
                logger.info(msg)
                # print('========= 產生url座標:', location, '===========')
                lst_location.append(location)
                url_new = url_base + location
                longitude += longitude_step
                yield url_new
            latitude += latitude_step
            longitude = longitude_min
        logger.error('座標已全數跑完')
        bComplete = True
        return ''
    except Exception as e:
        logger.error(e)

# =========== global 所需變數 =================
logger = create_logger(keyword+'/'+city)  # 在 logs 目錄下建立 tutorial 目錄
logger.info('Start')
start_time = time.time()

lst_store = lst_store_csv = lst_review = []
dic_store = dic_review = {}
bfinal = bError = bComplete = False
page = notcity_count = restart = restart_limit = 0
district = folder = stores_path = url_location = ''

folder_key_city = './csv/'+ keyword + '/' + city + '/'
if not os.path.exists(folder_key_city) :
    os.makedirs(folder_key_city)
# ===========================================
def reset_paras():
    global page, notcity_count
    global bfinal, bError
    global district, folder, stores_path
    global lst_store, dic_store, lst_store_csv, lst_review, dic_review

    district = folder = stores_path = ''
    page = notcity_count = 0
    bfinal = bError = False
    lst_store = lst_store_csv = lst_review = []
    dic_store = dic_review = {}
    
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

# =============== Start =====================
def start(bError):
    # url = 'https://www.google.com.tw/maps/@25.03,121.5,15z'
    global url_location
    url = url_location

    if not bError :         # 如果是因為Error重新啟動瀏覽器，不改變搜尋中心點
        url = next(url_gen)     
        url_location = url
    else:
        logger.info('不更新搜尋中心', url_location)
    driver.get(url)
    time.sleep(2) # 等待2秒

    input = find_tags(driver, dic_tag['input'], logger=logger)[0] # 找到搜尋欄的tag
    input.send_keys(keyword) # 寫入要搜尋的字
    msg = '輸入搜尋關鍵字:' + keyword + '，點擊搜尋'
    logger.info(msg)
    driver.find_element_by_id('searchbox-searchbutton').click()
    time.sleep(5)

url_gen = geturl()
start(False) # 需要取得URL
while True:
    if bfinal : 
        if bComplete: # 跑完所有經緯度
            logger.info('所有經緯度座標都跑完了，結束~~~~~~~~~')
            break
        else:
            # 【Error 或 頁數跑完要換下一個搜尋座標中心點】，都會將瀏覽器關閉、重開、變數reset，重新再搜尋
            driver.close()
            restart += 1
            print('restart 第', restart, '次')
            reset_paras()
            driver = Chrome('./chromedriver')
            start(bError) # 如果是因為Error重新啟動瀏覽器，不改變搜尋中心點
            # if restart > 15:
            #     print('restart > 15，結束~~~~~~~~~~~~~')
            #     break
    while not bfinal:
        try:
            results = find_tags(driver, dic_tag['stores'], logger=logger)
            stores_thispage = len(results)
            count_store = 0
            total_store = 0

            page += 1
            msg = '進入第' + str(page) + '頁, 店家數:' + str(stores_thispage)
            logger.info(msg)
            if page > totalpage:
                print('目前頁數', page, '已超過設定頁數：', totalpage)
                bfinal = True
                break

            for i in range(stores_thispage):
                if bfinal:
                    print('跳出本頁搜尋列表')
                    break
                dic_store = {} # 每個店家的資訊存進dic_store
                choose = False # selenium.common.exceptions.StaleElementReferenceException: Message: stale element reference: element is not attached to the page document

                results = find_tags(driver, dic_tag['stores'], logger=logger)

                if results[i].get_attribute(dic_tag['label']) != '':
                    ad = results[i].find_elements_by_class_name('ad-badge')[0] # 會有多個廣告tag，只看第一個
                    name_ori = results[i].get_attribute(dic_tag['label'])
                    name = checkName(name_ori, logger=logger) # 若含有特殊符號，無法作為檔名儲存
                    pricetag = results[i].find_elements_by_class_name(dic_tag['price'])[0].get_attribute(dic_tag['label']) # 找到價錢tag
                    price = ''
                    if pricetag != None:
                        price = pricetag.split(' ')[-1][0]
                    saved_latest_date = ''
                    saved_latest_review = ''

                    addr = ''
                    if 'display' not in ad.get_attribute('style') :
                        print('跳過這個廣告店家:', name)
                        continue # 廣告，跳過

                    results[i].click()
                    msg = '=== 點擊第'+ str(i+1) + '個店家: ' + name + ' ==='
                    logger.info(msg)

                    infolines = find_tags(driver, dic_tag['store_info'], logger=logger)

                    for infoline in infolines:
                        addrinfo = infoline.get_attribute(dic_tag['label'])
                        if '地址' in addrinfo:
                            addr = addrinfo.split('、')[-1] # 取得店家完整地址
                            if not city in addr:
                                msg = addr + ' ，不是 ' + city + ' 跳過'
                                # print(msg) # 不是台北市的店家不要抓
                                logger.info(msg)
                                choose = False
                                notcity_count += 1
                                break
                        elif '區 ' in addrinfo:
                            district = addrinfo.split(' ')[1] # 2GVC+6W 中正區 台北市
                            choose = True
                        elif '里 'in addrinfo or '區 ' in addrinfo:
                            district = addrinfo.split(' ')[-1].replace('台北市', '') # 3G36+P4 永樂里 台北市大同區
                            choose = True
                    if choose:
                        folder = folder_key_city + district + '/' # 路徑為./csv/熱炒/stores.csv
                        stores_path = folder_key_city + 'stores.csv'
                        review_path = folder + name + '_review.csv' # 路徑為./csv/熱炒/行政區/店名_review.csv
                        if not os.path.exists(folder):
                            os.makedirs(folder)
                        msg = '區：' + district + name
                        logger.info(msg)

                        # ============== 若此店家已儲存過評論，取出目前已存的最後一筆評論日期、評論內容 =======================
                        df_cur = pd.DataFrame()
                        if os.path.exists(review_path):
                            df_cur = pd.read_csv(review_path, encoding='utf8', engine='python')
                            if df_cur.empty:
                                msg = '此店家完全無評論，跳下一個店家'
                                logger.info(msg)
                                back_list = find_tags(driver, dic_tag['back_list'], logger=logger)
                                back_list[0].click()
                                msg = '已點擊返回搜尋列表'
                                logger.info(msg)
                                time.sleep(2)
                                continue
                            else:
                                saved_latest_date = df_cur.iloc[-1]['date']  # 最後一列的column'date'的值
                                saved_latest_review = df_cur.iloc[-1]['text'] # 最後一列的column'text'的值
                                msg = '第' + str(i + 1) + '個店家: ' + name + ' 的評論已經存過，已存的最新評論日期為' + saved_latest_date
                                logger.info(msg)

                        empty_review = 0 # 紀錄空白評論數
                        total_review = 0
                        count_store += 1
                        total_store += 1
                        lst_review = [] # 每個店家的所有review存進lst_review
                        dic_store['tmpid'] = total_store
                        dic_store['name'] = name
                        dic_store['price'] = price
                        dic_store['city'] = city
                        dic_store['district'] = district
                        dic_store['road'] = get_road(addr)
                        dic_store['addr'] = addr
                        try:
                            reviews_div = find_tags(driver, dic_tag['reviews_div'], logger=logger) # 先找到包住"所有評論"tag的框框，再找"所有評論"的tag，若此店家完全無評論就找不到"所有評論的tag"
                            allreviews = reviews_div[-1].find_elements_by_class_name(dic_tag['allreviews']) # 若此店家完全無評論就找不到"所有評論的tag"
                            print('搜尋"所有評論"這個tag')
                        except Exception as e:
                            msg = '店家完全沒有評論，error~~~~~~~~，except，開始儲存店家list'
                            logger.error(msg)
                            logger.error(e)
                            traceback.print_exc()
                            df_empty = pd.DataFrame(columns=['id','date','star','text'])
                            df_empty.to_csv(review_path, index=False, encoding="utf-8") # 無評論店家存空白.csv檔案，仍要有column名稱
                            lst_store = save_csv(stores_path, lst_store, logger=logger)  # 儲存後回傳空的list
                            bError = True
                            bfinal = True

                        if len(allreviews) > 0:
                            for j in allreviews:
                                if '評論' in j.get_attribute(dic_tag['label']):
                                    j.click()
                                    msg = '已點擊"所有評論"，總共有:' + j.get_attribute(dic_tag['label'])
                                    logger.info(msg)
                                    total_review = int(j.get_attribute(dic_tag['label']).split(' ')[0].replace(',','')) # 總共有幾則評論
                                    sort = find_tags(driver, dic_tag['ddl'], logger=logger) # 找到能依"最新日期, 相關度..."排序的下拉選單tag

                                    msg = '點擊選擇排序的下拉式選單:' + str(sort[-1].is_displayed())
                                    logger.info(msg)
                                    sort[-1].click() # 第0個是"撰寫評論"，所以選第二個

                                    menuitem = find_tags(driver, dic_tag['sort_item'], logger=logger) # 下拉選單中的所有選項
                                    for item in menuitem:
                                        if item.text == '最新':
                                            item.click()
                                            print('點擊選擇依時間最新來排序')
                                            break

                                    msg = '開始找section-loading'
                                    # print(msg)
                                    logger.info(msg)
                                    time.sleep(2)
                                    loading = driver.find_elements_by_class_name(dic_tag['loading']) # 找到loading tag點擊，就等於將滾輪往下滑，可以載入新的評論
                                    time.sleep(2)
                                    loading_count = 0 # 紀錄目前往下滑的loading次數
                                    record_time = 0  # 每往下滑loading 20次，就儲存一次loading次數
                                    record_date_count = 0 # 每往下滑loading 20次，就儲存一次目前取得的評論筆數
                                    while len(loading) != 0:
                                        loading_count += 1
                                        msg = 'loading評論第' + str(loading_count) + '次'
                                        # print(msg, end=',')
                                        logger.info(msg)
                                        loading = driver.find_elements_by_class_name(dic_tag['loading'])
                                        time.sleep(2)
                                        lstdate = find_tags(driver, dic_tag['review_date'], logger=logger) # 取得目前載入的評論數目

                                        if loading_count - record_time >= 20: # 目前loading次數 與 紀錄loading次數 相差 20次以上就更新紀錄
                                            if len(lstdate) > record_date_count: # 目前載入的評論數 > 紀錄的評論數-->就更新紀錄的評論數
                                                msg = '原本紀錄的loading次數:' + str(record_time) + ',更新為:' + str(loading_count)
                                                # print(msg)
                                                logger.info(msg)
                                                msg = '原本紀錄的評論數:' + str(record_date_count) + ',更新為:' + str(len(lstdate))
                                                # print(msg)
                                                logger.info(msg)
                                                record_date_count = len(lstdate)
                                                record_time = loading_count
                                            else:
                                                msg = '無法載入新的評論，Chrome 掛掉了，放棄載入新的評論 ' + name
                                                # print(msg)
                                                logger.error(msg)
                                                bError = True # 正常來說，每下滑一次就會取得新的評論，
                                                bfinal = True # 所以每下滑20次檢查一次，目前載入的評論數目會 > 已記錄的評論數才對
                                                break         # 若沒大於，代表它一直往下滑，但卻沒有載入新的評論數-->瀏覽器掛掉了
                                        loading_date = lstdate[-1].text

                                        msg = '最新已儲存日期：' + saved_latest_date + ', 目前此筆評論日期：' + get_real_date(loading_date) + ', loading displayed:' + str(loading[-1].is_displayed())
                                        # print(msg)
                                        logger.info(msg)

                                        if saved_latest_date != '' and get_real_date(loading_date) < saved_latest_date:
                                            msg = '目前最後一個評論日期：' + get_real_date(loading_date) + '已 < 最新儲存日期:' + saved_latest_date + '，不需再往下滑了'
                                            # print(msg)
                                            logger.info(msg)
                                            break
                                        elif len(loading) == 0:
                                            msg = '沒有section-loading了，停止往下滑'
                                            logger.info(msg)
                                            # print(msg)
                                            break
                                        if not loading[-1].is_displayed(): # 若元素沒有出現在畫面上，但仍要對它做動作，會出現錯誤"element not interactable”
                                            msg = 'loading[-1]還沒出現，等2秒'
                                            logger.error(msg)
                                            # print(msg)
                                            time.sleep(2)
                                            if not loading[-1].is_displayed():
                                                msg = 'loading[-1]沒有顯示，放棄載入新的評論 ' + name
                                                # print(msg)
                                                logger.error(msg)
                                                break
                                        loading[-1].click()

                                    each_review = find_tags(driver, dic_tag['review_text'], logger=logger)

                                    msg = '開始顯示所有評論數量:' +  str(len(each_review))
                                    # print(msg)
                                    logger.info(msg)
                                    print('=========================================')

                                    stars = find_tags(driver, dic_tag['review_star'], logger=logger) # 找到評論的星星數
                                    publish_date = find_tags(driver, dic_tag['review_date'], logger=logger) # 找到評論發表日期
                                    for k in range(len(each_review)):
                                        word = each_review[k].text.split('(原始評論)')
                                        # ======= 每個評論的字典都要先清空，不然會連動到上一個塞進List的dict  =============
                                        dic_review = {}
                                        review_date = publish_date[k].text # '1 週前'
                                        review_star = stars[k].get_attribute(dic_tag['label']).split(' ')[1] #' 5 顆星 '
                                        dic_review['tmpid'] = k+1
                                        dic_review['name'] = name
                                        dic_review['date'] = get_real_date(review_date)
                                        dic_review['star'] = review_star
                                        review_text = ''
                                        if each_review[k].text != "":
                                            if len(word) > 1:
                                                review_text = word[0].replace('(由 Google 提供翻譯)', '') # 非中文的話只取google翻譯過後的中文
                                            else:
                                                review_text = each_review[k].text

                                        review_text = '"' + review_text.replace('\r', '').replace('\n', '，') + '"' # 評論裡的換行符號改成"，"
                                        print('第' + str(k + 1), end=',')
                                        # print('第' + str(k + 1), 'date:', get_real_date(review_date) == saved_latest_date, 'review:', review_text == saved_latest_review)
                                        # print('第' + str(k + 1) + '筆:', '日期:', review_date, '星等:', review_star, '評論:',review_text)
                                        dic_review['text'] = review_text
                                        if saved_latest_date != '' and get_real_date(review_date) == saved_latest_date and review_text == saved_latest_review:
                                            msg = '這個評論日期 == 最新儲存日期，且評論內容 == 最新儲存評論內容，擷取評論結束'
                                            # print(msg)
                                            logger.info(msg)
                                            break
                                        elif saved_latest_date != '' and get_real_date(review_date) < saved_latest_date:
                                            msg = '這個評論日期：' + get_real_date(review_date) + '已 < 最新儲存日期：' + saved_latest_date +'，擷取評論結束'
                                            # print(msg)
                                            logger.info(msg)
                                            break
                                        elif saved_latest_date != '' and not '天' in review_date:
                                            msg = '只更新一週內的評論，超過的不更新，這個評論日期：' + get_real_date(review_date)
                                            # print(msg)
                                            logger.info(msg)
                                            break
                                        elif review_text == '""':
                                            msg = '空白評論不儲存！'
                                            # print(msg, end=',')
                                            empty_review += 1
                                            continue
                                        lst_review.append(dic_review)
                                    break

                            # print('====== 將該店家的review list放進該店家資訊的dic_store ===============')
                            dic_store['review'] = len(lst_review)  # 紀錄已儲存的評論數
                            dic_store['empty_review'] = empty_review # 紀錄空白的評論數
                            if not os.path.exists(review_path):
                                lst_store.append(dic_store)  # 若該店家已存過就不重複更新stores.csv

                            msg = '開始儲存review：' + review_path + '，總評論數：' + str(total_review) + '，儲存評論筆數：' + str(len(lst_review)) + '、空白評論筆數：' + str(empty_review)
                            # print(msg)
                            logger.info(msg)
                            lst_review = save_csv(review_path, lst_review, logger=logger) # 儲存後回傳空的list
                        else:
                            msg = '這個店家完全沒有評論, 仍要存檔, ' +  name + review_path
                            # print(msg)
                            logger.info(msg)
                            df_empty = pd.DataFrame(columns=['id','date','star','text'])
                            df_empty.to_csv(review_path, index=False, encoding="utf-8") # 無評論店家存空白.csv檔案，仍要有column名稱
                            lst_store = save_csv(stores_path, lst_store, logger=logger)  # 儲存後回傳空的list
                            bError = True
                            bfinal = True

                        if not bfinal:
                            back_store = find_tags(driver, dic_tag['back_store'], logger=logger)
                            back_store[0].click()
                            msg = '已點擊返回店家資訊'
                            # print(msg)
                            logger.info(msg)

                    if not bfinal:
                        back_list = find_tags(driver, dic_tag['back_list'], logger=logger)
                        back_list[0].click()
                        msg = '已點擊返回搜尋列表'
                        # print(msg)
                        logger.info(msg)
                        time.sleep(2)
            msg = '目前這頁爬完了，換下一頁，目前在第' + str(page) + '頁，已點過的店家數:' + str(count_store) + '開始儲存店家list'
            # print(msg)
            logger.info(msg)
            lst_store = save_csv(stores_path, lst_store, logger=logger) # 儲存後回傳空的list

            if bfinal:
                msg = '跳出while'
                # print(msg)
                logger.info(msg)
                break
            if notcity_count > 15:
                bfinal = True
                bError = True
                msg = '此搜尋中心非 ' + city + ' 的店家有' + str(notcity_count) + '筆，跳出while，換個中心點重跑'
                # print(msg)
                logger.info(msg)
                break
            try:
                nextpage = driver.find_element_by_id(dic_tag['next_page']) # 找到可以點擊下一頁的tag
                count_store = 0
                if nextpage.get_attribute('disabled') != 'true':
                    msg = '已點擊下一頁'
                    # print(msg)
                    logger.info(msg)
                    nextpage.click()
                    time.sleep(2)
                else:
                    bfinal = True # 若真的是最後一頁，tag的屬性disabled="true"，無法點擊
                    msg = '最後一頁了，下一頁disabled="true"'
                    # print(msg)
                    logger.info(msg)
            except Exception as e:
                msg = '最後一頁了，找不到 next_page tag，except，開始儲存店家list'
                # print(msg)
                # print(e)
                logger.error(msg)
                logger.error(e)
                lst_store = save_csv(stores_path, lst_store, logger=logger) # 儲存後回傳空的list
                traceback.print_exc()
                bfinal = True
        except Exception as e:
            msg = 'except，開始儲存店家list'
            logger.error(msg)
            logger.error(e)
            lst_store = save_csv(stores_path, lst_store, logger=logger) # 儲存後回傳空的list
            traceback.print_exc()
            bError = True
            bfinal = True
print('結束了~~~~~~~~~~~~~~~~')
time.sleep(3)
end_time = time.time()
total_time = end_time-start_time

m, s = divmod(total_time, 60)
h, m = divmod(m, 60)
print ("花費時間，時:%02d, 分:%02d, 秒:%02d" % (h, m, s))
logger.info("花費時間，時:%02d, 分:%02d, 秒:%02d" % (h, m, s))
# print(time.strftime("%H:%M:%S", total_time))
# print('{:d}:{:02d}:{:02d}'.format(h, m, s)) # Python 3
# print(f'{h:d}:{m:02d}:{s:02d}') # Python 3.6+
driver.close()
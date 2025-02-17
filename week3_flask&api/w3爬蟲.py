from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from pymongo import MongoClient
from pymongo import errors
from caldate import convert_date


# MongoDB連接設定
# uri = "mongodb://training:Bkmsz3024@192.168.31.89:30241/?authSource=2024_training&authMechanism=SCRAM-SHA-1"

# try:
#     client = MongoClient(uri)
#     print(client.server_info())
#     db = client['2024_training'] #client_db
#     collection = db['youqi'] # db_collection

# except errors.ConnectionFailure as err:
#     print(err)



driver = webdriver.Chrome()

# 打開網址
driver.get("https://www.google.com/maps/place/%E7%A2%B3%E4%BD%90%E9%BA%BB%E9%87%8C+(%E9%AB%98%E9%9B%84%E7%BE%8E%E8%A1%93%E9%A4%A8%E5%BA%97)/@22.6634005,120.287902,17z/data=!4m16!1m9!3m8!1s0x346e05acb0d030a1:0xeaf475aece122885!2z56Kz5L2Q6bq76YeMICjpq5jpm4Tnvo7ooZPppKjlupcp!8m2!3d22.6622046!4d120.2905735!9m1!1b1!16s%2Fg%2F1tgntzlj!3m5!1s0x346e05acb0d030a1:0xeaf475aece122885!8m2!3d22.6622046!4d120.2905735!16s%2Fg%2F1tgntzlj?entry=ttu")
time.sleep(1)

try:
    # 等待評論按鈕出現
    review_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//button[contains(@aria-label, '評論')]"))
    )
    # 滾動到評論按鈕並點擊
    ActionChains(driver).move_to_element(review_button).click().perform()
    time.sleep(1) 


    # 找到評論區塊的元素
    review_pane = driver.find_element(By.XPATH,'//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]')
    # 初始化最後的滾動高度
    last_height = driver.execute_script("return arguments[0].scrollHeight", review_pane)
    count = 1
    while True:
        # 滾動到區塊底部
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", review_pane)
        time.sleep(1)
        # count += 1
        # if count == 10:
        #     break
        # 檢查區塊的高度變化，如果高度停止變化則break
        new_height = driver.execute_script("return arguments[0].scrollHeight", review_pane)
        if new_height == last_height:
            break
        last_height = new_height

    # 抓取評論區域的HTML
    page_source = driver.page_source
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(page_source, 'html.parser')
    
    total = soup.find(class_='jANrlb')
    total_star = total.find(class_='fontDisplayLarge').get_text()
    print(f"總星級: {total_star}")
    total_comment = total.find(class_='fontBodySmall').get_text()
    print(f"總評價數: {total_comment}")

    review_elements = soup.find_all('div', class_='jJc9Ad')  #個別評論
    for review in review_elements:
        name = review.find(class_='d4r55').get_text()
        print(f"姓名: {name}")
        star = review.find('span',class_='kvMYJc').get('aria-label')
        print(f"星等: {star}")
        commenttime = review.find('span',class_='rsqaWe').get_text()
        date = convert_date(commenttime)
        print(f"時間: {date}")
        if(review.find('span',class_='wiI7pd')):
            comment = review.find('span',class_='wiI7pd').get_text()
        else:
            comment = '無'
        print(f"內文: {comment}")
        # if(review.find('div',class_='wiI7pd')):
        #     store_comment = review.find('div',class_='wiI7pd').get_text()
        # else:
        #     store_comment = '無'
        # print(f"業主回應: {store_comment}")

        print()  # 分行
    

        # # 將評論資訊插入MongoDB
        # review_data = {
        #     'name': name,
        #     'star': star,
        #     'comment_time': commenttime,
        #     'comment': comment,
        #     'store_comment': store_comment
        # }
        # collection.insert_one(review_data)


        
finally:
    driver.quit()

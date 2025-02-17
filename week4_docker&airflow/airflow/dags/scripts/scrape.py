from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
from pymongo import MongoClient
from pymongo import errors
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

driver = None

# 初始化 WebDriver
def initialize_driver(url):
    driver = webdriver.Remote(command_executor="http://192.168.31.90:4444", options=webdriver.ChromeOptions())
    driver.get(url)
    return driver


# 連接 MongoDB
def connect_mongo():
    uri = "mongodb://training:Bkmsz3024@192.168.31.89:30241/?authSource=2024_training&authMechanism=SCRAM-SHA-1"
    try:
        client = MongoClient(uri)
        print('MongoDB connect success!')
        return client['2024_training']['youqi']
    except errors.ConnectionFailure as err:
        print(err)


# 將資料插入 MongoDB
def insert_mongo(collection, reviews):
    for review in reviews:
        # 檢查是否已存在相同的評論
        existing_review = collection.find_one({
            'name': review['name']
        })
        if existing_review is None:
            collection.insert_one(review)
        else:
            print(f"評論已存在: {review['name']}，不插入。")

# 點擊評論按鈕並滾動到底部
def click_and_scroll(driver):
        review_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(@aria-label, '評論')]"))
        )
        ActionChains(driver).move_to_element(review_button).click().perform()
        time.sleep(1)
        
        review_pane = driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]')
        last_height = driver.execute_script("return arguments[0].scrollHeight", review_pane)
        
        while True:
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", review_pane)
            time.sleep(5)
            new_height = driver.execute_script("return arguments[0].scrollHeight", review_pane)
            if new_height == last_height:
                break
            last_height = new_height

        page_source = driver.page_source
        print("HTML長度:", len(page_source))
        return page_source


def scrape_reviews(page_source):      
        soup = BeautifulSoup(page_source, 'html.parser')

        total = soup.find(class_='jANrlb')
        total_star = total.find(class_='fontDisplayLarge').get_text()
        total_comment = total.find(class_='fontBodySmall').get_text()
        print(f"總星級: {total_star}")
        print(f"總評價數: {total_comment}")

        review_elements = soup.find_all('div', class_='jJc9Ad')  # 個別評論
        reviews = []
        
        # 印出評論
        for review in review_elements:
            name = review.find(class_='d4r55').get_text()
            print(f"姓名: {name}")
            star = review.find('span', class_='kvMYJc').get('aria-label')
            print(f"星等: {star}")
            commenttime = review.find('span', class_='rsqaWe').get_text()
            date = convert_date(commenttime)
            print(f"時間: {date}")
            comment = review.find('span', class_='wiI7pd').get_text() if review.find('span', class_='wiI7pd') else '無'
            print(f"內文: {comment}")
            
            # 將評論資料加入列表
            reviews.append({
                'name': name,
                'star': star,
                'date': date,
                'comment': comment
            })
            print()  # 分行
        
        return reviews
    # try:
    #     review_button = WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.XPATH, "//button[contains(@aria-label, '評論')]"))
    #     )
    #     ActionChains(driver).move_to_element(review_button).click().perform()
    #     time.sleep(1)
        
    #     review_pane = driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]')
    #     last_height = driver.execute_script("return arguments[0].scrollHeight", review_pane)
        
    #     while True:
    #         driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", review_pane)
    #         time.sleep(1)
    #         i = 1
    #         if i == 1:
    #             break

    #         new_height = driver.execute_script("return arguments[0].scrollHeight", review_pane)
    #         if new_height == last_height:
    #             break
    #         last_height = new_height
        
    #     page_source = driver.page_source
    #     soup = BeautifulSoup(page_source, 'html.parser')

    #     total = soup.find(class_='jANrlb')
    #     total_star = total.find(class_='fontDisplayLarge').get_text()
    #     total_comment = total.find(class_='fontBodySmall').get_text()
    #     print(f"總星級: {total_star}")
    #     print(f"總評價數: {total_comment}")

    #     review_elements = soup.find_all('div', class_='jJc9Ad')  # 個別評論
    #     reviews = []
        
    #     # 印出評論
    #     for review in review_elements:
    #         name = review.find(class_='d4r55').get_text()
    #         print(f"姓名: {name}")
    #         star = review.find('span', class_='kvMYJc').get('aria-label')
    #         print(f"星等: {star}")
    #         commenttime = review.find('span', class_='rsqaWe').get_text()
    #         date = convert_date(commenttime)
    #         print(f"時間: {date}")
    #         comment = review.find('span', class_='wiI7pd').get_text() if review.find('span', class_='wiI7pd') else '無'
    #         print(f"內文: {comment}")
            
    #         # 將評論資料加入列表
    #         reviews.append({
    #             'name': name,
    #             'star': star,
    #             'comment_time': commenttime,
    #             'date': date,
    #             'comment': comment
    #         })
    #         print()  # 分行
    # finally:
    #     driver.quit()
    
    # return reviews

def convert_date(relative_date_str):
    today = datetime.today()
    
    if '天前' in relative_date_str:
        days = int(relative_date_str.split('天前')[0])
        return (today - timedelta(days=days)).strftime('%Y-%m-%d')
    elif '週前' in relative_date_str:
        weeks = int(relative_date_str.split('週前')[0])
        return (today - timedelta(weeks=weeks)).strftime('%Y-%m-%d')
    elif '個月前' in relative_date_str:
        months = int(relative_date_str.split('個月前')[0])
        return (today - relativedelta(months=months)).strftime('%Y-%m-%d')
    elif '年前' in relative_date_str:
        years = int(relative_date_str.split('年前')[0])
        return (today - relativedelta(years=years)).strftime('%Y-%m-%d')
    else:
        return "無法識別的日期格式"



# 主程序
# if __name__ == "__main__":
#     url = "https://maps.app.goo.gl/HFxwW2CsYUyK1riv8"

#     collection = connect_mongo()
#     driver = initialize_driver(url)

#     try:
#         click_and_scroll(driver)  # 使用新的合併函數
#         reviews = scrape_reviews(driver)
#         insert_mongo(collection, reviews)
#     finally:
#         driver.quit()

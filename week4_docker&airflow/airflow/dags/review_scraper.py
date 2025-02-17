from airflow import DAG
from airflow.decorators import task
from airflow.exceptions import AirflowSkipException
from datetime import datetime, timedelta
from scripts.scrape import click_and_scroll, scrape_reviews, insert_mongo
from selenium import webdriver
from pymongo import MongoClient, errors

# 預設參數
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 0, 
}


with DAG('review_scraper', default_args=default_args, schedule_interval='@daily', catchup=False) as dag:

    # 定義上下文管理器
    class MongoDB:
        def __init__(self):
            self.collection = None
            self.client = None  # 儲存 MongoClient 實例

        def __enter__(self):
            try:
                # 嘗試連接到 MongoDB
                uri = "mongodb://training:Bkmsz3024@192.168.31.89:30241/?authSource=2024_training&authMechanism=SCRAM-SHA-1"
                self.client = MongoClient(uri)  # 替換為你的 MongoDB URI
                self.collection = self.client['2024_training']['youqi'] 
                return self.collection
            except errors.ConnectionError as e:
                raise RuntimeError("Failed to connect to MongoDB") from e

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.client:
                self.client.close()  # 關閉 MongoClient 連接（或可選）
    
    class WebDriverContext:
        def __init__(self, url):
            self.url = url
            self.driver = None

        def __enter__(self):
            self.driver = webdriver.Remote(command_executor="http://192.168.31.90:4444", options=webdriver.ChromeOptions())
            self.driver.get(self.url)
            return self.driver

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.driver:
                self.driver.quit()
    
    # 連接 MongoDB
    @task
    def run_connect_mongo():
        try:
            with MongoDB() as coll:
                collection = coll  # 獲取集合
        except RuntimeError as e:
            raise AirflowSkipException(f"MongoDB connection failed: {str(e)}")  # 讓任務失敗

    # 抓取完整 HTML
    @task
    def run_click_and_scroll(url):
        with WebDriverContext(url) as driver:
            page_source = click_and_scroll(driver)
            
        # 將 page_source 寫入文件
        with open('page_source.html', 'w', encoding='utf-8') as f:
            f.write(page_source)

    # 從 HTML 讀取所需資料
    @task
    def run_scrape_reviews():
        # 從文件讀取 page_source
        with open('page_source.html', 'r', encoding='utf-8') as f:
            page_source = f.read()
            
        return scrape_reviews(page_source)

    # 插入MongoDB
    @task
    def run_insert_mongo(reviews):
        with MongoDB() as collection:
            insert_mongo(collection, reviews)


    # 定義每個 task 的依賴關係
    connect_mongo_task = run_connect_mongo()
    click_and_scroll_task = run_click_and_scroll('https://www.google.com/maps/place/%E7%A2%B3%E4%BD%90%E9%BA%BB%E9%87%8C+(%E9%AB%98%E9%9B%84%E7%BE%8E%E8%A1%93%E9%A4%A8%E5%BA%97)/@22.6634005,120.287902,17z/data=!4m16!1m9!3m8!1s0x346e05acb0d030a1:0xeaf475aece122885!2z56Kz5L2Q6bq76YeMICjpq5jpm4Tnvo7ooZPppKjlupcp!8m2!3d22.6622046!4d120.2905735!9m1!1b1!16s%2Fg%2F1tgntzlj!3m5!1s0x346e05acb0d030a1:0xeaf475aece122885!8m2!3d22.6622046!4d120.2905735!16s%2Fg%2F1tgntzlj?entry=ttu')
    scrape_reviews_task = run_scrape_reviews()
    insert_mongo_task = run_insert_mongo(scrape_reviews_task)

    # 定義 task 的依賴關係
    connect_mongo_task >> click_and_scroll_task >> scrape_reviews_task >> insert_mongo_task

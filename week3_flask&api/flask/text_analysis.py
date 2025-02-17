import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import matplotlib
import re
from datetime import datetime
from wordcloud import WordCloud 
import jieba
import jieba.analyse
import requests
import json
import zh_processor as zh
from sklearn.feature_extraction.text import CountVectorizer

from data_loader import read_data
plt.rcParams['font.sans-serif']=['SimHei'] #使中文能正常顯示


class text_analysis:
    def __init__(self):
    
        positive_words = read_data('flask/dict/positive.txt').split(',')
        negative_words = read_data('flask/dict/negative.txt').split(',')

        df_positive_words = pd.DataFrame({'word': positive_words, 'sentiment': 'positive'})
        df_negative_words = pd.DataFrame({'word': negative_words, 'sentiment': 'negative'})

        # 合併 DataFrame
        df_words = pd.concat([df_negative_words, df_positive_words], ignore_index=True)
        
        url = 'http://127.0.0.1:8000/data/users'
        # 發送GET請求
        response = requests.get(url)
        self.df0 = pd.read_json(response.json()) 

        # 資料清理
        df_clean = zh.data_clean(self.df0)
        # 斷句
        df1 = zh.sentence_segmenation(df_clean)
        # 斷詞
        df2 = zh.tokenization(df1)
        
        # 停用字字典
        with open("flask/dict/stopwords.txt", "r", encoding="utf-8") as tf:
            stopword = tf.read().split('\n')
        df3 = zh.remove_stopword(df2, stopword=stopword) #移除停用字

        # 合併斷詞結果、情緒字典
        self.merge = pd.merge(df3, df_words, on='word', how='left')
        self.merge = self.merge[(self.merge['sentiment']=='positive')|(self.merge['sentiment']=='negative')]


    
    def monthly_star(self): # 計算每月平均星數

        # 保留月份資料
        start_date = pd.Timestamp('2023-08-01')
        end_date = pd.Timestamp('now')
        merge_month = self.merge[(self.merge['comment_time'] >= start_date) & (self.merge['comment_time'] <= end_date)]

        # 轉換star格式
        merge_month['star'] = merge_month['star'].replace(' 顆星', '', regex=True).astype(float)

        # 計算平均星星值
        merge_month.set_index('comment_time', inplace=True)  # 設置索引

        star_size = merge_month.resample('M')['star'].mean().reset_index()                   #依照月份採樣，計算平均(mean)star
        star_size['month'] = star_size['comment_time'].dt.to_period('M').astype(str)  #將2024-06-06轉成month字串
        star_size = star_size[['month', 'star']]

        return star_size
    

    def monthly_comment(self):  # 計算月均評論數
    
        start_date = pd.Timestamp('2023-08-01')
        end_date = pd.Timestamp('now')
        merge_month = self.df0[(self.df0['comment_time'] >= start_date) & (self.df0['comment_time'] <= end_date)]

        # 依照月份做Groupby，用size()計算總數
        comment_size = merge_month.groupby([merge_month['comment_time'].dt.to_period('M')]).size().reset_index(name='size')

        # 將date格式轉換成month
        comment_size['month'] = comment_size['comment_time'].astype(str)

        comment_size = comment_size[['month', 'size']]
        
        return comment_size
    

    def monthly_sentiment(self):# 計算每月正負情緒總數

        merge_sentiment = pd.merge(self.df0, self.merge[['name', 'word', 'sentiment']], on='name', how='left')

        # 保留月份資料
        start_date = pd.Timestamp('2023-08-01')
        end_date = pd.Timestamp('now')
        merge_month = merge_sentiment[(merge_sentiment['comment_time'] >= start_date) & (merge_sentiment['comment_time'] <= end_date)]

        # 計算每則評論中posi和nega的數量
        merge_month['positive'] = merge_month['sentiment'].apply(lambda x: 1 if x == 'positive' else 0)
        merge_month['negative'] = merge_month['sentiment'].apply(lambda x: 1 if x == 'negative' else 0)

        # 按照評論分組
        result = merge_month.groupby(['comment_time','comment']).agg({'positive': 'sum', 'negative': 'sum'}).reset_index()

        # 沒有情緒填'0'
        result = result.fillna(0)

        # 分類
        def classify_comment(row):
            if row['positive'] > row['negative']:
                return 'positive'
            elif row['negative'] > row['positive']:
                return 'negative'
            else:
                return 'neutral'

        # 把評論分類
        result['type'] = result.apply(classify_comment, axis=1)

        # 依照月份計算各類型評論的數量
        result['month'] = pd.to_datetime(result['comment_time']).dt.to_period('M').astype(str)
        monthly_sen = result.groupby(['month', 'type']).size().unstack(fill_value=0).reset_index()
        monthly_sen = monthly_sen[['month', 'positive', 'negative', 'neutral']]
    
        return monthly_sen

    def word_cloud(self):
        word_count = self.merge.groupby('word').size().reset_index(name='size')
        word_count = word_count.sort_values(by='size',ascending=False)
        return word_count.head(30)
    
    def get_correlation(self):
        self.merge['word'] = self.merge['word'].astype(str)
        table = self.merge.groupby('name')['word'].apply(lambda x: ' '.join(x)).reset_index()
        vectorizer = CountVectorizer()
        x = vectorizer.fit_transform(table['word'])
        result = pd.DataFrame(x.toarray(), columns=vectorizer.get_feature_names_out(), index=table['name'])
        result

        # 計算pearson correlation
        correlation_ma = np.corrcoef(result.values, rowvar=False)
        correlation_ma

        columns = result.columns
        index =  result.columns
        correlation_df = pd.DataFrame(correlation_ma, index=index, columns=columns)

        # 往前移，重置index
        correlation_df.reset_index(drop=True,inplace=True)
        re_index = correlation_df.columns.tolist()
        correlation_df.insert(0, 'item1', re_index)

        correlation_index = correlation_df.melt(id_vars=['item1'], var_name='item2', value_name='correlation')
        correlation_index = correlation_index[correlation_index['correlation']!= 1]
        return correlation_index
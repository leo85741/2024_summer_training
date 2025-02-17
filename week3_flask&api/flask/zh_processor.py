# 套件說明
    # Pandas: 一個資料分析的函式庫，提供了DataFrame等資料格式，與資料處理的函數。
    # jieba: 中文斷詞套件
    # wordcloud: 文字雲繪圖工具。
    # matplotlib: 繪圖工具。
import pandas as pd
import jieba
from wordcloud import WordCloud # pip install wordcloud
import matplotlib.pyplot as plt
from tkinter import font
import re
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP'] # 設定中文字型, 參考：https://pyecontech.com/2020/03/27/python_matplotlib_chinese/
FontPath = './SourceHanSansTW-Regular.otf' # 設定文字雲字型

# 資料初步清理
def data_clean(df):
    # input: dataframe, output: dataframe
    # 清除內文為空值的文章
    df = df.dropna(subset=['comment'])

    # 將兩個換行符號取代為句號
    df['comment'] = df['comment'].str.replace('\n\n', '。')
    # df['comment'] = df['comment'].str.replace('http\S+', '')
    df['comment'] = df['comment'].str.replace('\n', '')
    
    df = df[df['comment'] != '無']
    # 刪除純數字
    df = df[~df['comment'].apply(lambda x: bool(re.fullmatch(r'\d+', x)))]
    return df


# 斷句
def sentence_segmenation(df):
    # input: dataframe, output: dataframe
    
    # 以標點符號斷句
    df['comment']=df['comment'].apply(lambda x:split_sentence(x))
    df=df.explode('comment').reset_index(drop=True)
    return df


def split_sentence(text):
    punctuation=['。','？','！']
    sentences=[]
    start_index=0

    for index,char in enumerate(text):
        if char in punctuation and index>start_index:
            sentences.append(text[start_index:index+1].strip())
            start_index=index+1
            
    if start_index < len(text):
        sentences.append(text[start_index:].strip())
    return sentences


# 斷詞
def tokenization(df, user_dict_path=None):
    # input: dataframe, output: dataframe

    # 1. 初始化斷詞引擎：不一定要設定，只使用內建效果也可以
    # 參考網址：https://raw.githubusercontent.com/ldkrsi/jieba-zh_TW/master/jieba/dict.txt
    
    # 2. 設定初始字典
    
    if user_dict_path:
        jieba.load_userdict(user_dict_path)  # 設定繁體字典

    # 斷詞前先將標點符號清除，並清除空字串
    
    # 3. 若有使用自定義字典，設定自定義字典

    # 4. 斷詞前先將標點符號清除，並清除空字串
    # 5. 使用jieba進行斷詞
    df['comment'] = df['comment'].apply(lambda x: list(jieba.cut(re.sub(r'[^\w\s]', '', x))))
    df=df.explode('comment').reset_index(drop=True)
    
    return df


# 移除停用字
def remove_stopword(df, stopword):
    # input: dataframe 與停用字列表, output: dataframe
    
    # 切成字串格式
    df['comment'] = df['comment'].astype(str)
    df['word'] = df['comment'].apply(lambda x: ''.join([word for word in x.split() if word not in stopword]))
    df=df.drop(columns=['comment'])
    df=df[df['word']!=''].reset_index(drop=True)
    
    return df


# 計算詞頻
def word_frequency_calculation(df):
    # input: dataframe, output: 詞頻表 dataframe
    # 計算 word 裡面相同的詞出現幾次
    df_freq = df['word'].value_counts().reset_index()
    df_freq.columns = ['word', 'frequency']
    
    return df_freq


# 繪製長條圖
def plot_bar_chart(df_freq, top_n):
    # input: dataframe 與 top_n（畫出前幾個詞頻最大的詞）
    # 選取前 top_n 的詞
    top_words = df_freq.head(top_n)

    plt.figure(figsize=(10, 6))
    plt.barh(top_words['word'], top_words['frequency'], color='blue', height=0.5)
    plt.xlabel('Frequency')
    plt.ylabel('Words')
    
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()
    

# 繪製文字雲
def plot_wordcloud(df, top_n):
    # 選取前 top_n 的詞
    top_words = df.head(top_n)
    
    # 創建詞頻字典
    word_freq_dict = dict(zip(top_words['word'], top_words['frequency']))
    
    font = './SourceHanSansTW-Regular.otf' #中文字型路徑
    
    # 創建文字雲
    wordcloud = WordCloud(width=800, height=400, background_color='white', font_path=font).generate_from_frequencies(word_freq_dict)
    
    # 繪製文字雲
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(f'Top {top_n} Words by Frequency')
    plt.show()
    
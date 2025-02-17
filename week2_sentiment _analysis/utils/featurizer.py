import pandas as pd
import numpy as np 
import nltk
import math
nltk.download("punkt") # 下載需要用到的語料庫
import matplotlib.pyplot as plt


###計算詞頻

#計算某文字在各chapter中出現次數
def term_frequency_chapter(df):
    # input: dataframe, output: dataframe
    # Hint: 可透過['chapter', 'word']兩欄位進行計算

    return df


#計算每個文章中總共有多少字
def term_frequency_document(df):
    # input: dataframe, output: dataframe
    # Hint: 以['chapter']欄位分群計算各文章的字

    return df


# 算tf
def tf(df):
    # input: dataframe, output: dataframe
    # Hint: 該詞在文章中出現的比例

    return df


# 算idf
def idf(df):
    # input: dataframe, output: dataframe
    # Hint: 該詞出現在幾篇文章中

    return df


# tfidf
def tfidf(df):
    # input: dataframe, output: dataframe
    # Hint: tf和idf相乘即得出tfidf

    return df


# 由小到大檢視tfidf
def sort_tfidf(df):
    # input: dataframe, output: dataframe
    # Hint: 可參考expected output

    return df


# 找出每個chapter前10名的TFIDF
def top10_tfidf(df):
    # input: dataframe, output: dataframe
    # Hint: 可參考expected output

    return df


# 統計每個字出現在每篇tfidf前10名的次數
def word_top10_tfidf(df):
    # input: dataframe, output: dataframe
    # Hint: 可參考expected output

    return df


### ngram

# bigram
def bigram(df):
    # input: dataframe, output: dataframe
    # Hint: 從['sentence']欄位求出

    return df


# trigram
def trigram(df):
    # input: dataframe, output: dataframe
    # Hint: 從['sentence']欄位求出

    return df


# bigram 次數
def bigram_times(df):
    # input: dataframe, output: dataframe
    # Hint: 可參考expected output

    return df


# 拆成兩個columns 分別為word1 word2
def bigram_split(df):
    # input: dataframe, output: dataframe
    # Hint: 可參考expected output

    return df


# 計算street跟其他字一起出現的頻率
def bigram_street(df):
    # input: dataframe, output: dataframe
    # Hint: 可參考expected output

    return df

### 計算每個字的correlation

# 轉成DTM格式
def DTM_df(df):
    # input: dataframe, output: dataframe
    # Hint: sklearn有提供相關套件

    return df


# 計算每個字對每篇文章的pearson correlation
def pearsoncorrelation_df(df):
    # input: dataframe, output: dataframe
    # Hint: pandas有提供function，但是算得很慢，也可以用numpy的

    return df


# 轉成一對一的格式後，把correlation值為1的去掉
def melt_df(df):
    # input: dataframe, output: dataframe
    # Hint: 可參考expected output

    return df


### 列出跟 elizabeth 還有my最相關的前6個字

# elizabeth
def elizabeth_diagram(df):
    # input: dataframe, output: dataframe
    # Hint: 可參考expected output

    return df 


# pride
def pride_diagram(df):
    # input: dataframe, output: dataframe
    # Hint: 可參考expected output

    return df
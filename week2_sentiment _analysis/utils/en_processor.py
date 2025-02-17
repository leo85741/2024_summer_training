# 套件說明
    # Pandas: 一個資料分析的函式庫，提供了DataFrame等資料格式，與資料處理的函數。
    # NLTK: 全名為Natural Language Tool Kit，自然語言處理工具。Python所提供的NLP工具有許多，如Spacy、Scikit-learn、Gensim等，每個套件有不同的用法與目的，以下會以NLTK為主要的處理工具，大家也可以嘗試看看其他不同的工具處理。
        # (參考資料：https://www.upgrad.com/blog/python-nlp-libraries-and-applications/)
    # re: 正規表達式套件。(好用的小工具：https://regex101.com/)
    # wordcloud: 文字雲繪圖工具。
    # matplotlib: 繪圖工具。
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
import matplotlib.pyplot as plt
from wordcloud import WordCloud 
import re
from collections import Counter
nltk.download('punkt')
nltk.download('wordnet')  #詞性
nltk.download('averaged_perceptron_tagger')
nltk.download('omw-1.4')
nltk.download('stopwords')



# 斷句
def sentence_segmenation(df):
    # input: dataframe, output: dataframe
    # Hint: 使用 NLTK 套件的斷句函示進行斷句，一個 row 為一個句子
    
    sentences = []
    for text in df['text']:
        # 使用sent_tokenize斷句
        sentences.extend(sent_tokenize(text))
    
    # 創建新 DataFrame，其中每行是一個句子
    df_sentences = pd.DataFrame({'sentence':sentences})
 
    return df_sentences





# 斷詞
def tokenization(df):
    # input: dataframe, output: dataframe
    
    # 使用 NLTK 套件的斷詞函式進行斷詞
    tokenized_df = df
    tokenized_df['token'] = df['sentence'].apply(word_tokenize)
    
    # 將 DataFrame 處理成一個 row 一個斷詞的結果
    tokenized_df = tokenized_df.explode('token').reset_index(drop=True)
    
    return tokenized_df






# 資料初步清理
def data_clean(df):
    # input: dataframe, output: dataframe
    # Hint: 使用 re 

   # 1. 使用 re 套件並用正規表達式比對出章節每個句子所屬的章節，並在 DataFrame 中新增一個章節的欄位
    chapter_pattern = re.compile(r'CHAPTER\s+[IVXLCDM]+', re.IGNORECASE)
    chapter = None
    chapters = []
    count = 0
    
    for sentence in df['sentence']:
        match = chapter_pattern.match(sentence)
        if match:
#             chapter = match.group()
            count+=1   #計算章節數
        chapters.append(count)
    
    df['chapter'] = chapters
    
    # 2. 清除 CHAPTER 的句子，並將長度小於 1 的句子刪除
    df = df[~df['sentence'].str.match(chapter_pattern)]
    df = df[df['sentence'].str.len() > 1]
    
    # 3. 清除文本中的標點符號、數字以及換行符號
    df['sentence'] = df['sentence'].apply(lambda x: re.sub(r'[^\w\s]', '', x))  # 清除標點符號
    df['sentence'] = df['sentence'].apply(lambda x: re.sub(r'\d+', '', x))     # 清除數字
    df['sentence'] = df['sentence'].apply(lambda x: x.replace('\n', ' '))      # 清除換行符號
    df['sentence'] = df['sentence'].apply(lambda x: x.strip())                 # 去除前後空白
    
    return df






# 字詞正規化-大小寫轉換
def case_conversion(df):
    # input: dataframe, output: dataframe
    df['word'] = df['token'].str.lower()
    return df






# 字詞正規化-Stemming
def stemming(df):
    # input: dataframe, output: dataframe

    # 1. 初始化一個 PorterStemmer的物件，並存在 porter 變數中
    porter = PorterStemmer()
    
    # 2. 使用 PorterStemmer 將斷詞進行字根還原
    df['word'] = df['word'].astype(str)
#     df['stem_token'] = df['word'].apply(lambda x: ' '.join([porter.stem(word) for word in word_tokenize(x)]))
    df['stem_token'] = df['word'].apply(lambda x: porter.stem(x))

    
    # 小提醒：nltk許多function變數規定為字串，因此可以將word轉為字串格式，以確保後續不會有錯誤

    return df






# 轉換詞性標示方式 (Lemmatization 之前先定義好此轉換函式)
# 因為 nltk 的 WordNetLemmatizer 輸入的詞性和 pos_tag 函式所標記的方式不同，因此需要先將 pos 的欄位轉換成是以 wordnet 的標示方式 => 呼叫 get_wordnet_pos 函式進行轉換
def get_wordnet_pos(treebank_tag):
    # input: 詞性, output: wordnet 詞性
    # Hint: 使用 NLTK 的 wordnet 函式
    
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return None
    
    

    
    
    
# 字詞正規化-Lemmatization
def lemmatization(df):
    # input: dataframe, output: dataframe

    
    # 1. 使用 word 欄位字詞，利用 NLTK 套件進行詞性標註並存在 pos 欄位中
    df['word'] = df['word'].astype(str)
    df['pos'] = df['word'].apply(lambda word: nltk.pos_tag([word])[0][1])
    
    
    
    # 2. 將 datafram 中的詞和詞性(轉換過後的)使用 WordNetLemmatizer 產生 lemma
    # 2.1 初始化 Lemmatizer
    lemmatizer = WordNetLemmatizer()
    
    # 2.2 使用 WordNetLemmatizer 產生 lemma
    # 定義字詞正規化的函式
    def lemmatize_text(word, pos_tag):
        pos = get_wordnet_pos(pos_tag)  # 取第一個詞性標記的 wordnet 詞性
        if pos:
            return lemmatizer.lemmatize(word, pos=pos)
        else:
            return lemmatizer.lemmatize(word)  # 預設使用名詞詞性進行詞形還原

    # 將每個詞進行詞形還原
    df['lemma'] = df.apply(lambda row: lemmatize_text(row['word'], row['pos']), axis=1)
    
    # Hint: 1) 利用以上 get_wordnet_pos 轉換詞性表示 
    #       2) 有些詞性轉換過後無法被 WordNetLemmatizer 辨識，就可以不必將詞性當作參數

    return df








# 移除停用字
def remove_stopword(df, stopword):
    # input: dataframe 與停用字列表, output: dataframe
    # Hint: 而移除停用字的方式是依照條件來篩選資料：將 df['token'] 沒有在停用字裡的字保留，這邊要特別注意的是要先做字詞的正規化(Text Normalization)，使用轉成小寫英文的 token (即 df['word'])再來進行比對，否則有些字不會被去除。例如：I、Because...
    df = df[~df['word'].isin(stopword)]
    return df






# 計算詞頻
def word_frequency_calculation(df):
    # input: dataframe, output: 詞頻表 dataframe
    # 計算 lemma_token 裡面相同的詞出現幾次
    
    # 計算詞頻
    word_counts = Counter(df['lemma'])

    # 將詞頻字典轉換為 DataFrame
    df_freq = pd.DataFrame(word_counts.items(), columns=['word', 'frequency']).sort_values(by='frequency', ascending=False)
    df_freq.reset_index(drop=True, inplace=True)
    return df_freq






# 繪製長條圖
def plot_bar_chart(df, top_n):
    # input: dataframe 與 top_n（畫出前幾個詞頻最大的詞）
    
    # 選取前 top_n 的詞
    top_words = df.head(top_n)

    plt.figure(figsize=(10, 6))
    plt.barh(top_words['word'], top_words['frequency'], color='blue', height=0.5)
    plt.xlabel('Frequency')
    plt.ylabel('Words')
    plt.title(f'Top {top_n} Words by Frequency')
    
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()

    
    
    
# 繪製文字雲
def plot_wordcloud(df, top_n):
    # input: dataframe 與 top_n（畫出前幾個詞頻最大的詞）
    # 選取前 top_n 的詞
    top_words = df.head(top_n)
    
    # 創建詞頻字典
    word_freq_dict = dict(zip(top_words['word'], top_words['frequency']))

    # 創建文字雲
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_freq_dict)

    # 繪製文字雲
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(f'Top {top_n} Words by Frequency')
    plt.show()
    
    
    
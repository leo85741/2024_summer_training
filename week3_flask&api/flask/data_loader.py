import pandas as pd

# 資料蒐集
def read_data(path):
    # input: 資料路徑, output: dataframe
    # 讀入資料並以 Dataframe 格式儲存
    if path.endswith('.txt'):
        #open讀取檔案，'r'表示只讀
        with open(path, 'r', encoding='utf-8') as file:
            lines = file.read()

        return lines
    elif path.endswith('.csv'):
        return pd.read_csv(path)
    
    return None
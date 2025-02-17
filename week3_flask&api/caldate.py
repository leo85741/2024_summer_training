from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

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

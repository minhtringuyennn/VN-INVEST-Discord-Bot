# Import python modules
import re, pytz
import numpy as np
import pandas as pd
from datetime import datetime 
from datetime import timedelta
from dateutil import parser
import pytz

def format_value(val, basic = True):
    if basic == True:
        return "{:,.0f}".format(float(val))
    else:
        return "{:,.2f}".format(float(val))

def format_percent(val):
    val = float(val)
    if val > 0:
        return "+{:,.2f}%".format(float(val))
    if val == 0:
        return "{:,.2f}%".format(float(val))
    if val < 0:
        val = -val
        return "-{:,.2f}%".format(float(val))

def get_current_time(val):
    time =  parser.isoparse(val)
    time_zone = pytz.timezone('Asia/Ho_Chi_Minh')
    time = time.astimezone(time_zone).strftime('%Y-%m-%d, %H:%M:%S')
    return str(time)

def get_today_date():
    today = datetime.now()
    today = today.strftime('%Y-%m-%d')
    return today

# Return last year date
def get_last_year_date():
    today = datetime.now()
    last_year = today - timedelta(days=365)
    last_year = last_year.strftime('%Y-%m-%d')
    return last_year

def convert_date(text, date_type = '%Y-%m-%d'):
    return datetime.strptime(text, date_type)

def convert_text_dateformat(text, origin_type = '%Y-%m-%d', new_type = '%Y-%m-%d'):
    return convert_date(text, origin_type).strftime(new_type)

def calc_break_day(data, start_date, end_date):
    dt_chart = data['date'].index
    # print(dt_chart)
    dt_chart = pd.to_datetime(dt_chart).strftime("%Y-%m-%d").tolist()
    
    dt_all = []
    delta =  datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')
    for i in range(delta.days + 1):
        day = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=i)
        dt_all.append(day.strftime('%Y-%m-%d'))
    
    res = [i for i in dt_chart + dt_all if i not in dt_chart or i not in dt_all]
    
    return res

def _isOHLC(data):
    try:
        cols = dict(data.columns)
    except:
        cols = list(data.columns)

    defau_cols = ['high', 'low', 'close', 'open']

    if all(col in cols for col in defau_cols):
        return True
    else:
        return False

def _isOHLCV(data):
    try:
        cols = dict(data.columns)
    except:
        cols = list(data.columns)

    defau_cols = ['high', 'low', 'close', 'open', 'volume']

    if all(col in cols for col in defau_cols):
        return True
    else:
        return False
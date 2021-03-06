# Import python modules
import re, pytz
import numpy as np
import pandas as pd
from datetime import datetime 
from datetime import timedelta
from dateutil import parser

import stock_modules.fetch as fetch

def convertDailyToWeek(data):
    try:
        data['Datetime'] = pd.to_datetime(data['date'])
        data = data.set_index(pd.DatetimeIndex(data['Datetime']))
        
        agg_dict = {'open': 'first',
                    'high': 'max',
                    'low': 'min',
                    'close': 'last',
                    'volume': 'sum'}

        dfw = data.resample('W').agg(agg_dict)
        dfw.index = dfw.index - pd.tseries.frequencies.to_offset("6D")
        
        df = dfw[['high','low','open','close', 'volume']].copy()
        df.columns = ['high','low','open','close', 'volume']
        df['date'] = dfw.index.strftime('%Y-%m-%d')
        df.reset_index(drop=True, inplace=True)
        return df.dropna()
    except:
        return data

def format_value(val, basic = True, sign = False):
    try:
        val = float(val)
    except TypeError:
        return "None"
    
    if basic == True:
        res = "{:,.0f}".format(val)
    else:
        res = "{:,.2f}".format(val)
    
    if sign:
        if val > 0:
            res = "+{}".format(res)
        elif val < 0:
            res = "{}".format(res)
    
    return res
    
def format_percent(val, multiply = 1.0, basic = False):
    try:
        val = float(val) * multiply
    except TypeError:
        return "None"
    
    if basic == False:
        if val > 0:
            return "+{:,.2f}%".format(val)
        if val == 0:
            return "{:,.2f}%".format(val)
        if val < 0:
            val = -val
            return "-{:,.2f}%".format(val)
    elif basic == True:
        if val > 0:
            return "+{:,.0f}%".format(val)
        if val == 0:
            return "{:,.0f}%".format(val)
        if val < 0:
            val = -val
            return "-{:,.0f}%".format(val)
    
def get_current_time(val):
    try:
        time =  parser.isoparse(val)
        time_zone = pytz.timezone('Asia/Ho_Chi_Minh')
        time = time.astimezone(time_zone).strftime('%Y-%m-%d, %H:%M:%S')
        return str(time)
    except:
        return get_today_date()
    
def get_today_date():
    today = datetime.now()
    today = today.strftime('%Y-%m-%d')
    return today

# Return last year date
def get_last_year_date(delta = 365):
    today = datetime.now()
    last_year = today - timedelta(days=delta)
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
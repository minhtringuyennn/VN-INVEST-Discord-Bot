# Import lib
from bs4 import BeautifulSoup
from datetime import datetime

import re, time, requests

import numpy as np
import pandas as pd
import logging as logging

import stock_modules.utils as utils

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
HEADERS = {'content-type': 'application/x-www-form-urlencoded', 'User-Agent': 'Mozilla'}

# Struct
class Stocks():
    def __init__(self, symbols, start, end):
        self.symbols = symbols
        self.start = utils.convert_text_dateformat(start, new_type = '%d/%m/%Y')
        self.end = utils.convert_text_dateformat(end, new_type = '%d/%m/%Y')

# Load data from API
class DataLoader():
    def __init__(self, symbols, start, end, minimal = True):
        self.symbols = symbols
        self.start = start
        self.end = end
        self.minimal = minimal

    def fetchPrice(self):
        loader = FetchDailyPrice(self.symbols, self.start, self.end)
        stock_data = loader.batch_download()

        if self.minimal:
            minimal_data = stock_data[['date', 'high','low','open','close', 'volume']]
            return minimal_data
        else:
            return stock_data

# Fetch daily stock price from API
class FetchDailyPrice(Stocks):
    def __init__(self, symbols, start, end):
        self.symbols = symbols
        self.start = start
        self.end = end
        super().__init__(symbols, start, end)

    def batch_download(self):
        stock_datas = []
        
        # Check symbols contains list of stocks or not
        if not isinstance(self.symbols, list):
            symbols = [self.symbols]
        else:
            symbols = self.symbols

        for symbol in symbols:
            stock_datas.append(self.download_new(symbol))

        data = pd.concat(stock_datas, axis=1)
        return data

    def download_new(self, symbol):
        # Convert date
        start_date = utils.convert_text_dateformat(self.start, origin_type = '%d/%m/%Y', new_type = '%Y-%m-%d')
        end_date = utils.convert_text_dateformat(self.end, origin_type = '%d/%m/%Y', new_type = '%Y-%m-%d')
        
        # API
        API_VNDIRECT = 'https://finfo-api.vndirect.com.vn/v4/stock_prices/'
        query = 'code:' + symbol + '~date:gte:' + start_date + '~date:lte:' + end_date
        
        delta = datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')
        
        params = {
            "sort": "date",
            "size": delta.days + 1,
            "page": 1,
            "q": query
        }
        
        # Get reponse from API
        res = requests.get(API_VNDIRECT, params=params, headers=HEADERS)
        data = res.json()['data']  
        data = pd.DataFrame(data)
        
        # Define label
        stock_data = data[['date', 'adClose', 'close', 'pctChange', 'average', 'nmVolume',
                        'nmValue', 'ptVolume', 'ptValue', 'open', 'high', 'low']].copy()
        stock_data.columns = ['date', 'adjust', 'close', 'change_perc', 'avg',
                        'volume_match', 'value_match', 'volume_reconcile', 'value_reconcile',
                        'open', 'high', 'low']

        # Clean up data
        # stock_data = stock_data.set_index('date').apply(pd.to_numeric, errors='coerce')
        stock_data = stock_data.sort_index(ascending=False) # Sort table
        stock_data.fillna(0, inplace=True) # Fill NaN --> 0
        
        # Add volumn column
        stock_data['volume'] = stock_data.volume_match

        # Add label
        iterables = [stock_data.columns.tolist(), [symbol]]

        # Logging
        logging.info('data {} from {} to {} clone successfully!' \
                     .format(symbol,
                             utils.convert_text_dateformat(self.start, origin_type = '%d/%m/%Y', new_type = '%Y-%m-%d'),
                             utils.convert_text_dateformat(self.end, origin_type='%d/%m/%Y', new_type='%Y-%m-%d')))

        # Return data
        return stock_data

class FetchCategories():
    def __init__(self):
        super().__init__()
        
    def fetchFloor(self, floor = "HOSE"):
        if floor != "HOSE" and floor != "HNX" and floor != "UPCOM":
            logging.info('Floor is not support!'.format(floor))
            return None
        
        # API
        API_VNDIRECT = f'https://finfo-api.vndirect.com.vn/stocks?floor={floor}'
        
        # Get reponse from API
        res = requests.get(API_VNDIRECT, headers=HEADERS)
        data = res.json()['data']  
        data = pd.DataFrame(data)
        
        stock_data = data[['symbol', 'companyName', 'listedDate', 'delistedDate', 'floor', 'industryName']].copy()

        # Clean up data
        stock_data = stock_data.sort_index() # Sort table
        stock_data.fillna(0, inplace=True) # Fill NaN --> 0

        # Logging
        logging.info('data from floor {} clone successfully!'.format(floor))

        # Return data
        return stock_data
    
    def fetchVN30(self):
        # API
        API_VNDIRECT = 'https://finfo-api.vndirect.com.vn/stocks?indexCode=VN30'
        
        # Get reponse from API
        res = requests.get(API_VNDIRECT, headers=HEADERS)
        data = res.json()['data']  
        data = pd.DataFrame(data)
        
        stock_data = data[['symbol', 'companyName', 'listedDate', 'delistedDate', 'floor', 'industryName']].copy()

        # Clean up data
        stock_data = stock_data.sort_index() # Sort table
        stock_data.fillna(0, inplace=True) # Fill NaN --> 0

        # Logging
        logging.info('data VN30 clone successfully!')

        # Return data
        return stock_data
    
    def batch_download(self, symbols):
        stock_datas = []
        
        # Check symbols contains list of stocks or not
        if not isinstance(symbols, list):
            symbols = [symbols]

        for symbol in symbols:
            stock_datas.append(self.download_new(symbol))
        
        data = pd.concat(stock_datas)
        logging.info('batch clone successfully with {} stocks!'.format(len(symbols)))
        
        return data
    
    def download_new(self, symbol):
        # API
        API_VNDIRECT = f'https://finfo-api.vndirect.com.vn/stocks?symbol={symbol}'
        
        # Get reponse from API
        res = requests.get(API_VNDIRECT, headers=HEADERS)
        data = res.json()['data']  
        data = pd.DataFrame(data)
        
        stock_data = data[['symbol', 'companyName', 'listedDate', 'delistedDate', 'floor', 'industryName']].copy()
        
        # Clean up data
        stock_data.fillna(0, inplace=True) # Fill NaN --> 0

        # Logging
        logging.info('data stock {} clone successfully!'.format(symbol))

        # Return data
        return stock_data

def fetchCurrentPrice(symbol):
    # API
    FIREANT_API = f'https://www.fireant.vn/api/Data/Markets/Quotes?symbols={symbol}'
    
    # Get reponse from API
    res = requests.get(FIREANT_API, headers=HEADERS)
    try:
        return res.json()[0]
    except:
        return None

def fetchFianancialInfo(symbol):
    # API
    FIREANT_API = f'https://www.fireant.vn/api/Data/Finance/LastestFinancialInfo?symbol={symbol}'
    
    # Get reponse from API
    res = requests.get(FIREANT_API, headers=HEADERS)
    try:
        return res.json()
    except:
        return None
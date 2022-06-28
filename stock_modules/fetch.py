# Import lib
from bs4 import BeautifulSoup
from datetime import datetime

import re, os, time, requests, configparser, xmltodict

import feedparser as fp
import numpy as np
import pandas as pd
import logging as logging

import stock_modules.utils as utils

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
        self.data = None
        
    def fetchPrice(self):
        loader = FetchDailyPrice(self.symbols, self.start, self.end)
        stock_data = loader.batch_download()

        self.data = stock_data
        if self.minimal:
            self.data = stock_data[['date', 'high','low','open','close', 'volume']]
            return self.data
        else:
            return self.data

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
    
def fetchStockNews(symbol, offset = 0, count=5, getComment=False):
    offset = max(offset, 0)
    
    LIMIT = count
    
    if getComment: type = 0
    else: type = 1
    
    # API
    if symbol == "ALL":
        FIREANT_API = f'https://restv2.fireant.vn/posts?type={type}&offset={offset}&limit={LIMIT}'
    else:
        FIREANT_API = f'https://restv2.fireant.vn/posts?symbol={symbol}&type={type}&offset={offset}&limit={LIMIT}'
    
    read_config = configparser.ConfigParser()
    path = os.path.join(os.path.abspath(__file__+"/../../"),"config", "config.ini")
    read_config.read(path)
    FIREANT_BEARER_KEY = read_config.get("config", "FIREANT_BEARER_KEY")
    HEADERS.update({'Authorization': f'Bearer {FIREANT_BEARER_KEY}'})
    
    # Get reponse from API
    res = requests.get(FIREANT_API, headers=HEADERS)
    try:
        return res.json()
    except:
        return None
    
def fetchINDEX(symbol = "VNINDEX"):
    today_date = utils.get_today_date()
    last_year_date = utils.get_last_year_date()
    
    # API
    FIREANT_API = f'https://restv2.fireant.vn/symbols/{symbol}/historical-quotes?startDate={last_year_date}&endDate={today_date}'
    
    read_config = configparser.ConfigParser()
    path = os.path.join(os.path.abspath(__file__+"/../../"),"config", "config.ini")
    read_config.read(path)
    FIREANT_BEARER_KEY = read_config.get("config", "FIREANT_BEARER_KEY")
    HEADERS.update({'Authorization': f'Bearer {FIREANT_BEARER_KEY}'})
    
    # Get reponse from API
    res = requests.get(FIREANT_API, headers=HEADERS)
    try:
        index = round(res.json()[0]["priceAverage"])
        change_perc = (res.json()[0]["priceAverage"] - res.json()[0]["priceBasic"]) / res.json()[0]["priceBasic"] * 100
        change_perc = utils.format_percent(change_perc)
        change_score = utils.format_value(res.json()[0]["priceAverage"] - res.json()[0]["priceBasic"], basic=False)
        base_score = float(res.json()[0]["priceBasic"])
        return [ index, change_perc, change_score, base_score ]
    except:
        return [ None, None, None ]
    
def fetchINDEXInfluences(index = "VNINDEX"):
    VNDIRECT_API = f'https://mkw-socket.vndirect.com.vn/mkwsocket/leaderlarger?index={index}'
    
    res = requests.get(VNDIRECT_API, headers=HEADERS)
    
    return res.json()["data"]

def fetchINDEXHistory(index = "VNINDEX"):    
    # API
    FIALDA_API = f'https://fwtapi2.fialda.com/api/services/app/Home/GetVNIndexChart?indexCode={index}&chartPedirod=today'
    
    # Get reponse from API
    res = requests.get(FIALDA_API, headers=HEADERS)
    return res.json()['result']

def fetchYoutubeLivestream(youtube_channel_id):
    channel_url = f"https://www.youtube.com/channel/{youtube_channel_id}/live"
    page = requests.get(channel_url, headers=HEADERS, cookies={'CONSENT': 'YES+42'})
    soup = BeautifulSoup(page.content, "html.parser")
    live = soup.find("link", {"rel": "canonical"})
    if live:
        return live["href"]
    else:
        return None
    
def fetchYoutubePlaylist(youtube_channel_id, max_results = 1):
    YOUTUBE_API = f"https://www.youtube.com/feeds/videos.xml?channel_id={youtube_channel_id}"
    rss = fp.parse(YOUTUBE_API)

    youtube_playlist = {}
    count = 0

    for entry in rss.entries:
        count += 1
        if count > max_results: break
    
        title = entry['title']
        attibute = {}
        for link in entry.links:
            attibute.update(link)
        link = attibute['href']
        
        youtube_playlist.update({title: link})

    return youtube_playlist
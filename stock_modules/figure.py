import math
import io
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from mplfinance.original_flavor import candlestick_ohlc
from matplotlib.pylab import date2num

import stock_modules.fetch as fetch
import stock_modules.utils as utils
import stock_modules.indicate as indicate

img = io.BytesIO()

def drawFigure(data, Symbol, length, drawMA=True, drawBB=True, drawVol=True, drawRSI=True, drawMACD=True):

    length = max(14, length)

    # Styling the figure with ggplot style
    mpl.style.use("ggplot")

    # SETTING UP THE PLOT
    LENGTH = -length
    SUBPLOT = 1 + int(drawVol) + int(drawRSI) + int(drawMACD)
    # print(SUBPLOT)
    PADDING = 0.02
    LEFT = 0.06
    WIDTH = 1 - 2 * LEFT
    SIZE = (1 / SUBPLOT) - PADDING * 4
    
    NBINS_X = 60
    NBINS_Y = 20

    idx = 1

    # Set date as index
    data.date = pd.to_datetime(data.date)
    data.index = data.date

    # Draw the first graph
    fig = plt.figure()
    fig.set_size_inches((10, 3 * SUBPLOT + 1))

    ax_canddle = fig.add_axes((LEFT,
                               (SUBPLOT - idx) * (SIZE + PADDING) + 0.15 / SUBPLOT, 
                               WIDTH,
                               1 - ((SUBPLOT - idx) * (SIZE + PADDING) + 0.15 / SUBPLOT)))
    
    ax_canddle.locator_params(nbins=NBINS_X, axis='x')
    ax_canddle.locator_params(nbins=NBINS_Y, axis='y')
    ax_canddle.yaxis.tick_right()
    # ax_canddle.xaxis_date()
        
    # Calculate moving average
    data["ma20"] = indicate.calcMovingAverage(data['close'], 20)
    data["ma50"] = indicate.calcMovingAverage(data['close'], 50)
    data["ma100"] = indicate.calcMovingAverage(data['close'], 100)
    
    data["BB"], data["BBUp"], data["BBDown"] = indicate.calcBollingerBand(data['close'])
    
    data["rsi"] = indicate.calcRSI(data['close'])
    
    data["macd"], data["sigal"], data["hist"] = indicate.calcMACD(data['close'])
    
    # Draw only the last LENGTH days
    # print(data[LENGTH:])
    data = data[LENGTH:]

    data_list = []
    for date, row in data[['high','low','open','close']].iterrows():
        t = date2num(date)
        high, low, open, close = row[:]
        datas = (t, open, high, low, close)
        data_list.append(datas)

    # Draw a candle chart
    weekday_candlestick(ax_canddle, data_list)

    # Draw monving average
    if drawMA == True:
        ax_canddle.plot(range(data.index.size), data.ma20, label="MA20", color="tab:red")
        ax_canddle.plot(range(data.index.size), data.ma50, label="MA50", color="tab:green")
        ax_canddle.plot(range(data.index.size), data.ma100, label="MA100", color="tab:blue")

    # Calculate Bollinger band
    if drawBB == True:        
        ax_canddle.plot(range(data.index.size), data.BBUp, label="Bollinger up", color="tab:orange", alpha=0.7)
        ax_canddle.plot(range(data.index.size), data.BBDown, label="Bollinger down", color="tab:orange", alpha=0.7)
        ax_canddle.fill_between(range(data.index.size), data.BBUp, data.BBDown, facecolor='orange', alpha=0.1)

    ax_canddle.set_ylabel(f"{Symbol} chart last {length} days")
    ax_canddle.legend()

    # Draw volume
    if drawVol == True:
        idx += 1
        ax_vol = fig.add_axes((LEFT, (SUBPLOT - idx) * (SIZE + PADDING), WIDTH, SIZE))
        ax_vol.locator_params(nbins=60, axis='x')
        ax_vol.locator_params(nbins=10, axis='y')
        ax_vol.yaxis.tick_right()
        
        # Divide volume by 100w
        ax_vol.bar(range(data.index.size), data.volume / 1000000, color=np.where(data['open'] > data['close'], 'red', 'green'))

        # Set to Millions Bit Units
        ax_vol.axes.get_xaxis().set_visible(False)
        ax_vol.yaxis.tick_right()
        ax_vol.set_ylabel("Millon")
        ax_vol.set_xlabel("Date")
        
    # Compute RSI
    if drawRSI == True:
        idx += 1        
        ax_rsi = fig.add_axes((LEFT, (SUBPLOT - idx) * (SIZE + PADDING), WIDTH, SIZE))
        ax_rsi.locator_params(nbins=30, axis='x')
        ax_rsi.locator_params(nbins=10, axis='y')
        ax_rsi.yaxis.tick_right()
        
        # Draw RSI
        ax_rsi.plot(range(data.index.size), [70] * len(data.index), label="Overbuy")
        ax_rsi.plot(range(data.index.size), [30] * len(data.index), label="Oversell")
        ax_rsi.plot(range(data.index.size), data.rsi, label="RSI")
        ax_rsi.axes.get_xaxis().set_visible(False)
        ax_rsi.set_ylabel("%")
        ax_rsi.legend()

    # Calculate MACD Indicator Data
    if drawMACD == True:
        idx += 1
        ax_macd = fig.add_axes((LEFT, (SUBPLOT - idx) * (SIZE + PADDING), WIDTH, SIZE))
        ax_macd.locator_params(nbins=60, axis='x')
        ax_macd.locator_params(nbins=10, axis='y')
        ax_macd.yaxis.tick_right()

        # Draw MACD
        ax_macd.plot(range(data.index.size), data["macd"], label="MACD")
        ax_macd.plot(range(data.index.size), data["sigal"], label="Signal")
        ax_macd.bar(range(data.index.size), data["hist"] * 2, label="Histogram", color=np.where(data['hist'] < 0, 'red', 'green'))
        ax_macd.axes.get_xaxis().set_visible(False)
        ax_macd.legend()
    fig.savefig(img,Format="png")
    plt.cla()
    plt.clf()
    plt.close('all')
    
# Custom plot figure
def weekday_candlestick(ax, ohlc_data, fmt='%b %d', freq=1, **kwargs):
    # Convert data to numpy array
    ohlc_data_arr = np.array(ohlc_data)
    ohlc_data_arr2 = np.hstack(
        [np.arange(ohlc_data_arr[:,0].size)[:,np.newaxis], ohlc_data_arr[:,1:]])
    ndays = ohlc_data_arr2[:,0]
    
    # Convert matplotlib date numbers to strings based on `fmt`
    dates = mdates.num2date(ohlc_data_arr[:,0])
    date_strings = []
    for date in dates:
        date_strings.append(date.strftime(fmt))

    # Plot candlestick chart
    candlestick_ohlc(ax, ohlc_data_arr2, colorup='g', colordown='r', width=0.8, **kwargs)

    # Format x axis
    ax.set_xticks(ndays[::freq])
    ax.set_xticklabels(date_strings[::freq], rotation=45, ha='center')

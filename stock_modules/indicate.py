import pandas as pd
import numpy as np
import logging as logging

def roundTraditional(val, digits):
   return round(val + 10**(-len(str(val)) - 1), digits)

def calcMovingAverage(df, rollingDay = 20):
    try:
        return df.rolling(rollingDay).mean().round(2).tolist()
    except Exception as err:
        logging.info('Cannot calculate moving average! Error {}'.format(err))

def calcRMA(x, n, y0):
    a = (n-1) / n
    ak = a**np.arange(len(x)-1, -1, -1)
    return np.r_[np.full(n, np.nan), y0, np.cumsum(ak * x) / ak / n + y0 * a**np.arange(1, len(x)+1)]

def calcRSI(df, periods = 14):
    try:
        dfChanges = df.diff()
        
        dfGain = dfChanges.clip(lower=0)
        dfLoss = -1 * dfChanges.clip(upper=0)
        
        dfAvgGain = calcRMA(dfGain[periods+1:].to_numpy(), periods, np.nansum(dfGain.to_numpy()[:periods+1])/periods)
        dfAvgLoss = calcRMA(dfLoss[periods+1:].to_numpy(), periods, np.nansum(dfLoss.to_numpy()[:periods+1])/periods)

        RSI = 100 - (100 / (1 + dfAvgGain / dfAvgLoss))
        return RSI.round(2)
    except Exception as err:
        logging.info('Cannot calculate RSI! Error {}'.format(err))
        
def calcBollingerBand(df, periods = 20):
    dfMA = df.rolling(periods).mean()
    dfSTD = df.rolling(periods).std()

    dfUpper = dfMA + (dfSTD * 2)
    dfLower = dfMA - (dfSTD * 2)
    
    return [dfMA.round(2), dfUpper.round(2), dfLower.round(2)]

def calcMACD(df, fastLength = 12, slowLength = 26, signal = 9):
    # Get the 26-day EMA of the closing price
    k = df.ewm(span=fastLength, min_periods=fastLength).mean()
    
    # Get the 12-day EMA of the closing price
    d = df.ewm(span=slowLength, min_periods=slowLength).mean()
    
    # Subtract the 26-day EMA from the 12-Day EMA to get the MACD
    macd = k - d
    # Get the 9-Day EMA of the MACD for the Trigger line
    macd_s = macd.ewm(span=signal, min_periods=signal).mean()
    # Calculate the difference between the MACD - Trigger for the Convergence/Divergence value
    macd_h = macd - macd_s
    
    return [macd.round(2), macd_s.round(2), macd_h.round(2)]
import talib
import numpy
import math

def RSI(close):
    rsi = talib.RSI(numpy.asarray(close), timeperiod=21)
    v1 = 0.1 * (rsi - 50)
    v2 = talib.WMA(numpy.asarray(v1), timeperiod=9)
    inv = []
    for entry in v2:
        inv.append((math.exp(2 * entry) - 1) / (math.exp(2 * entry) + 1))

    rsiSell = (inv[-2] > 0.5) and (inv[-1] <= 0.5)
    rsiBuy = (inv[-2] < -0.65) and (inv[-1] >= -0.65)

    return rsiBuy, rsiSell, round(inv[-1], 2)

def MACDEMA(close):
    MMEslowa = talib.EMA(numpy.asarray(close),timeperiod=26)
    MMEslowb = talib.EMA(MMEslowa, timeperiod=26)
    DEMAslow = ((2 * MMEslowa) - MMEslowb)

    MMEfasta = talib.EMA(numpy.asarray(close), timeperiod=12)
    MMEfastb = talib.EMA(MMEfasta, timeperiod=12)
    DEMAfast = ((2 * MMEfasta) - MMEfastb)

    LigneMACD = DEMAfast - DEMAslow

    MMEsignala = talib.EMA(LigneMACD, timeperiod=9)
    MMEsignalb = talib.EMA(MMEsignala, timeperiod=9)
    Lignesignal = ((2 * MMEsignala) - MMEsignalb)

    macdBuy = LigneMACD[-2] < Lignesignal[-2] and LigneMACD[-1] >= Lignesignal[-1]
    macdSell = LigneMACD[-2] > Lignesignal[-2] and LigneMACD[-1] <= Lignesignal[-1]
    return macdBuy,macdSell, round(LigneMACD[-1],2), round(Lignesignal[-1],2)

def cci(high, low, close):
    real = talib.CCI(numpy.asarray(high),numpy.asarray(low),numpy.asarray(close),timeperiod=13)
    v1 = 0.1*(real/4)
    v2 = talib.WMA(v1,timeperiod=9)
    INV = []
    for x in v2:
        INV.append((math.exp(2*x)-1)/(math.exp(2*x)+1))
    cciBuy = INV[-2] < -0.75 and INV[-1] >= -0.75
    cciSell = INV[-2] > -0.75 and INV[-1] <= -0.75
    return cciBuy,cciSell,INV[-1]


def stopCalculator(high,low,close):
    atr = talib.ATR(numpy.asarray(high),numpy.asarray(low),numpy.asarray(close), timeperiod=14)
    stop = close[-1]-(3*atr[-1])
    return round(stop,2)

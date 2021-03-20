import time
import config
from binance.client import Client
import numpy
import talib
import math
from binance.enums import *
from binance.websockets import BinanceSocketManager
import telebot
import Database
from threading import Thread
from multiprocessing import Process


SYMBOL = 'BTCUSDT'
BUY_SYMBOLS = []
BLACKLIST = ['DOWN','UP','TUSDUSDT','VITEUSDT','PAXGUSDT','BCCUSDT','VENUSDT','BCHABCUSDT']
TIME = "1 month ago UTC+3"

candleDataClose_4H = []
candleDataClose_1H = []

EMA_1H = []
EMA_15M = []
MACD = []

counter = 0
bot = telebot.TeleBot("1628197070:AAFLvfUgbwO8qnY4YkQJ8yLHLoube-51GKc", parse_mode="MarkdownV2")
buyerClient = Client(config.api_key, config.api_secret)
sellerClient = Client(config.api_key, config.api_secret)
stopClient = Client(config.api_key, config.api_secret)
connection = Database.create_connection("test.db")

def fillSymbols():
    BUY_SYMBOLS.clear()
    data = buyerClient.get_symbol_ticker()
    for x in data:
        if x['symbol'][-4:] == 'USDT':
            for a in BLACKLIST:
                allOf = True
                if x['symbol'].find(a)!=-1:
                    allOf=False
                    break
            if allOf:
                BUY_SYMBOLS.append(x['symbol'])

def RSI(close):
    rsi = talib.RSI(numpy.asarray(close), timeperiod=21)
    v1 = 0.1 * (rsi - 50)
    v2 = talib.WMA(numpy.asarray(v1), timeperiod=9)
    inv = []
    for entry in v2:
        inv.append((math.exp(2 * entry) - 1) / (math.exp(2 * entry) + 1))

    rsiSell = (inv[-2] > 0.5) and (inv[-1] <= 0.5)
    rsiBuy = (inv[-2] < -0.5) and (inv[-1] >= -0.5)

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



def macdAndRsiKlineBuy():
    for x in BUY_SYMBOLS:
        high =[]
        low = []
        close=[]
        klines = buyerClient.get_historical_klines(x, Client.KLINE_INTERVAL_1HOUR, TIME)
        for entry in klines:
            if entry != numpy.NaN:
                high.append(float(entry[2]))
                low.append(float(entry[3]))
                close.append(float(entry[4]))

        if len(close) > 40:
            cciBuy ,cciSell, invcci = cci(high,low,close)
            macdBuy, signalSell, macd, signal = MACDEMA(close)
            if macdBuy and cciBuy:
                if Database.count_open_orders(connection)<10 and (not Database.isExist(connection,x)):
                    stop = stopCalculator(high,low,close)
                    order =(x,klines[-1][4],klines[-1][0]/1000,stop,klines[-1][4])
                    Database.create_buy_order(connection,order)
                else:
                    break
                msg = x + "\U0001F4C8 Alış: " + str(round(float(klines[-1][4]),4)).replace(".", ",")
                bot.send_message(-1001408874432, msg)
                print(msg)

def macdAndRsiKlineSell():
    SYMBOLS = Database.getOpenOrder(connection)
    for x in SYMBOLS:
        close=[]
        klines = sellerClient.get_historical_klines(x[1], Client.KLINE_INTERVAL_1HOUR, TIME)
        if len(klines) > 26:
            for entry in klines:
                close.append(float(entry[4]))
            macdBuy, macdSell, macd, signal = MACDEMA(close)
            stop = close[-1] < x[2]
            if macdSell:
                order = (klines[-1][4],klines[-1][0],x[0])
                Database.sellOrder(connection,order)
                msg = x[1] + "\U0001F4C8 Satiş: " + str(round(float(klines[-1][4]),4)).replace(".", ",")
                bot.send_message(-1001408874432, msg)
                print(msg)
            if stop:
                order = (klines[-1][4],klines[-1][0],x[0])
                Database.sellOrder(connection,order)
                msg = x[1]+ "\U0001F534 Stop: " + str(round(float(klines[-1][4]),4)).replace(".", ",")
                bot.send_message(-1001408874432, msg)
                print(msg)

def stopsUpdate():
    SYMBOLS = Database.getOpenOrder(connection)
    for x in SYMBOLS:
        high =[]
        low = []
        close=[]
        klines = stopClient.get_historical_klines(x[1], Client.KLINE_INTERVAL_1HOUR, TIME)
        for entry in klines:
            high.append(float(entry[2]))
            low.append(float(entry[3]))
            close.append(float(entry[4]))
        
        if close[-1] > Database.getLastPrice(connection,x[0]):
            stopPrice =stopCalculator(high,low,close)
            order = (round(stopPrice,2),x[0],close[-1])
            Database.updateStopPrice(connection,order)
            print(x[1],"Stoplar Updatelendi")




def stopCalculator(high,low,close):
    atr = talib.ATR(numpy.asarray(high),numpy.asarray(low),numpy.asarray(close), timeperiod=14)
    stop = close[-1]-(3*atr[-1])
    return round(stop,2)

def seller():
    print("Seller is working...")
    while True:
        if Database.count_open_orders(connection) > 0:
            macdAndRsiKlineSell()
        else:
            time.sleep(20)


def buyer():
    print("Buyer is working...")
    while True:
        if Database.count_open_orders(connection)<10:
            macdAndRsiKlineBuy()
        else:
            time.sleep(10)

def stopTracker():
    print("Stop Tracker is working...")
    while True:
        if Database.count_open_orders(connection)>0:
            stopsUpdate()
            time.sleep(3600)
        else:
            time.sleep(30)


if __name__ == '__main__':
    fillSymbols()
    buy = Thread(target=buyer)
    sell = Thread(target=seller)
    stop = Thread(target=stopTracker)
    buy.start()
    sell.start()
    stop.start()

import numpy
import Database
from binance.client import Client
from binance.client import BinanceAPIException
import config
import time
import requests
from indicator import MACDEMA
from indicator import RSI
from indicator import stopCalculator
import setup

TIME = "2 week ago UTC+3"
BLACKLIST = ['DOWN','UP','PAXGUSDT','PAXUSDT','BCCUSDT','VENUSDT','BCHABC','TRY','PERPUSDT','BEAR','BULL']
BUY_SYMBOLS = []

connection = Database.create_connection("test.db")

def fillSymbols():
    BUY_SYMBOLS.clear()
    client1 = Client(config.api_key1, config.api_secret1)
    data = client1.get_all_tickers()
    time.sleep(0.1)
    for x in data:
        if x['symbol'][-4:].find("USDT") !=-1:
            if x['symbol'][:-4].find("USD") ==-1:
                for a in BLACKLIST:
                    allOf = True
                    if x['symbol'].find(a)!=-1:
                        allOf=False
                        break
                if allOf:
                    BUY_SYMBOLS.append(x['symbol'])

def buyer():
    client1 = Client(config.api_key1, config.api_secret1)
    print("Buyer is working...")
    fillSymbols()
    while True:
        if Database.count_open_orders(connection)<10:
            for x in BUY_SYMBOLS:
                try:
                    high =[]
                    low = []
                    close=[]
                    time.sleep(0.3)
                    klines = client1.get_historical_klines(x, Client.KLINE_INTERVAL_1HOUR, TIME)
                    for entry in klines:
                        high.append(float(entry[2]))
                        low.append(float(entry[3]))
                        close.append(float(entry[4]))
                    if len(close) > 65:
                        #cciBuy ,cciSell, invcci = cci(high,low,close)
                        rsiBuy,rsiSell, invRsi = RSI(close)
                        macdBuy, signalSell, macd, signal = MACDEMA(close)
                        if macdBuy and rsiBuy:
                            if Database.count_open_orders(connection)<10 and (not Database.isExist(connection,x)):
                                stop = stopCalculator(high,low,close)
                                order =(x,klines[-1][4],klines[-1][0]/1000,stop,klines[-1][4])
                                Database.create_buy_order(connection,order)
                            else:
                                break
                            msg = x + "\U0001F4C8\nAlış: " + str(round(float(klines[-1][4]),8)).replace(".","\\.") + "\nStop: " + str(stop).replace(".","\\.")
                            setup.bot.send_message(-1001408874432, msg)
                except BinanceAPIException as e:
                    print('Something went wrong in buyer')
                    time.sleep(60)
                    client1 = Client(config.api_key1, config.api_secret1)
                    continue
                except requests.exceptions.Timeout:
                    print("timeout")
                    continue
        else:
            time.sleep(60)
import Database
from binance.client import Client
import config
import numpy
import time
from indicator import MACDEMA
from indicator import cci
from indicator import RSI
from indicator import stopCalculator
import setup

TIME = "1 month ago UTC+3"
BLACKLIST = ['DOWN','UP','TUSDUSDT','PAXGUSDT','BCCUSDT','VENUSDT','BCHABC','TRY',]
BUY_SYMBOLS = []
client = Client(config.api_key1, config.api_secret1)
connection = Database.create_connection("test.db")


def fillSymbols():
    BUY_SYMBOLS.clear()
    data = client.get_symbol_ticker()
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

def macdAndRsiKlineBuy():
    for x in BUY_SYMBOLS:
        high =[]
        low = []
        close=[]
        klines = client.get_historical_klines(x, Client.KLINE_INTERVAL_1HOUR, TIME)
        for entry in klines:
                high.append(float(entry[2]))
                low.append(float(entry[3]))
                close.append(float(entry[4]))

        if len(close) > 60:
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
                msg = x + "\U0001F4C8 Alış: " + str(round(float(klines[-1][4]),4)).replace(".", ",")
                setup.bot.send_message(-1001408874432, msg)
                print(msg)

def buyer():
    print("Buyer is working...")
    fillSymbols()
    while True:
        if Database.count_open_orders(connection)<10:
            macdAndRsiKlineBuy()
        else:
            time.sleep(10)
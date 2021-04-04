from binance.exceptions import BinanceAPIException
import Database
import config
import time
import requests
from binance.client import Client
from indicator import stopCalculator

connection = Database.create_connection("test.db")
TIME = "2 day ago UTC+3"

def stopTracker():
    print("Stop Tracker is working...")
    client3 = Client(config.api_key3, config.api_key3)
    while True:
        if Database.count_open_orders(connection)>0:
            SYMBOLS = Database.getOpenOrder(connection)
            for x in SYMBOLS:
                try:
                    high =[]
                    low = []
                    close=[]
                    time.sleep(0.3)
                    klines = client3.get_historical_klines(x[1], Client.KLINE_INTERVAL_1HOUR, TIME)
                    for entry in klines:
                        high.append(float(entry[2]))
                        low.append(float(entry[3]))
                        close.append(float(entry[4]))
                    if close[-1] > Database.getLastPrice(connection,x[0]):
                        stopPrice =stopCalculator(high,low,close)
                        order = (stopPrice,x[0],close[-1])
                        Database.updateStopPrice(connection,order)
                except BinanceAPIException as e:
                    print('Something went wrong in stoper')
                    time.sleep(60)
                    client3 = Client(config.api_key3, config.api_secret3)
                    continue
                except:
                    print("unexpected error")
                    time.sleep(60)
                    client3 = Client(config.api_key3, config.api_secret3)
                    continue
            time.sleep(3600)
        else:
            time.sleep(60)
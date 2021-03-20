import talib
import Database
import config
import numpy
import time
from binance.client import Client
from indicator import stopCalculator

connection = Database.create_connection("test.db")
client = Client(config.api_key2, config.api_secret2)
TIME = "1 month ago UTC+3"

def stopsUpdate():
    SYMBOLS = Database.getOpenOrder(connection)
    for x in SYMBOLS:
        high =[]
        low = []
        close=[]
        klines = client.get_historical_klines(x[1], Client.KLINE_INTERVAL_1HOUR, TIME)
        for entry in klines:
            high.append(float(entry[2]))
            low.append(float(entry[3]))
            close.append(float(entry[4]))
        
        if close[-1] > Database.getLastPrice(connection,x[0]):
            stopPrice =stopCalculator(high,low,close)
            order = (round(stopPrice,2),x[0],close[-1])
            Database.updateStopPrice(connection,order)
            print(x[1],"Stoplar Updatelendi")





def stopTracker():
    print("Stop Tracker is working...")
    while True:
        if Database.count_open_orders(connection)>0:
            stopsUpdate()
            time.sleep(3600)
        else:
            time.sleep(30)
import Database
import config
import time
from binance.client import Client
from indicator import stopCalculator

connection = Database.create_connection("test.db")
client3 = Client(config.api_key3, config.api_secret3)
TIME = "1 month ago UTC+3"

def stopsUpdate():
    SYMBOLS = Database.getOpenOrder(connection)
    for x in SYMBOLS:
        high =[]
        low = []
        close=[]
        klines = client3.get_historical_klines(x[1], Client.KLINE_INTERVAL_1HOUR, TIME)
        time.sleep(0.2)
        for entry in klines:
            high.append(float(entry[2]))
            low.append(float(entry[3]))
            close.append(float(entry[4]))
        
        if close[-1] > Database.getLastPrice(connection,x[0]):
            stopPrice =stopCalculator(high,low,close)
            order = (stopPrice,x[0],close[-1])
            Database.updateStopPrice(connection,order)





def stopTracker():
    print("Stop Tracker is working...")
    while True:
        if Database.count_open_orders(connection)>0:
            stopsUpdate()
            time.sleep(3600)
        else:
            time.sleep(60)
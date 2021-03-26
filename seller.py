from binance.exceptions import BinanceAPIException
import Database
from binance.client import Client
import config
import time
from indicator import MACDEMA
import setup
import requests

connection = Database.create_connection("test.db")

TIME = "2 week ago UTC+3"

def seller():
    print("Seller is working...")
    client2 = Client(config.api_key1, config.api_secret1)
    while True:
        if Database.count_open_orders(connection) > 0:
            SYMBOLS = Database.getOpenOrder(connection)
            for x in SYMBOLS:
                try:
                    time.sleep(0.2)
                    klines = client2.get_historical_klines(x[1], Client.KLINE_INTERVAL_1HOUR, TIME)
                    if len(klines) > 26:
                        close=[]
                        for entry in klines:
                            close.append(float(entry[4]))
                        macdBuy, macdSell, macd, signal = MACDEMA(close)
                        #cciBuy, cciSell,invcci = cci(close)
                        stop = close[-1] < x[2]
                        if macdSell:
                            order = (klines[-1][4],klines[-1][0],x[0])
                            Database.sellOrder(connection,order)
                            msg = x[1] + "\U0001F4B0 Satiş: " + str(round(float(klines[-1][4]),8)).replace(".", "\\.") + Database.profitCalc(connection,x[0])
                            setup.bot.send_message(-1001408874432, msg)
                        if stop:
                            order = (klines[-1][4],klines[-1][0],x[0])
                            Database.sellOrder(connection,order)
                            msg = x[1]+ "\U0001F534 Stop: " + str(round(float(klines[-1][4]),8)).replace(".", "\\.") + Database.profitCalc(connection,x[0])
                            setup.bot.send_message(-1001408874432, msg)
                except BinanceAPIException as e:
                    print('Something went wrong')
                    time.sleep(60)
                    client2 = Client(config.api_key1, config.api_secret1)
                    continue
                except requests.exceptions.ConnectTimeout:
                    print("timeout")
                    pass
        else:
            time.sleep(20)

from binance.exceptions import BinanceAPIException
import Database
from binance.client import Client
import config
import time
from indicator import MACDEMA
import setup
import requests

intervals = (
    ('hafta', 604800),  # 60 * 60 * 24 * 7
    ('gün', 86400),    # 60 * 60 * 24
    ('saat', 3600),    # 60 * 60
    ('dakika', 60),
    )

def display_time(seconds, granularity=3):
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])


connection = Database.create_connection("test.db")

TIME = "3 week ago UTC+3"

def seller():
    print("Seller is working...")
    client2 = Client(config.api_key2, config.api_secret2)
    while True:
        if Database.count_open_orders(connection) > 0:
            SYMBOLS = Database.getOpenOrder(connection)
            for x in SYMBOLS:
                try:
                    time.sleep(0.3)
                    klines = client2.get_historical_klines(x[1], Client.KLINE_INTERVAL_4HOUR, TIME)
                    if len(klines) > 26:
                        close=[]
                        for entry in klines:
                            close.append(float(entry[4]))
                        macdBuy, macdSell, macd, signal = MACDEMA(close)
                        #cciBuy, cciSell,invcci = cci(close)
                        stop = close[-1] < x[2]
                        sell = close[-1] >= x[3]
                        if macdSell:
                            timeClose = display_time(time.time()-(x[4]/1000))
                            order = (klines[-1][4],klines[-1][0],x[0])
                            Database.sellOrder(connection,order)
                            msg = x[1] + "\U0001F4B0 Satış: " + str(round(float(klines[-1][4]),8)).replace(".", "\\.") + Database.profitCalc(connection,x[0]) + "\n" + timeClose
                            setup.bot.send_message(-1001408874432, msg)
                            continue
                        if stop:
                            timeClose = display_time(time.time()-(x[4]/1000))
                            order = (klines[-1][4],klines[-1][0],x[0])
                            Database.sellOrder(connection,order)
                            msg = x[1]+ "\U0001F534 Stop: " + str(round(float(klines[-1][4]),8)).replace(".", "\\.") + Database.profitCalc(connection,x[0]) + "\n" + timeClose
                            setup.bot.send_message(-1001408874432, msg)
                            continue
                        if sell:
                            timeClose = display_time(time.time()-(x[4]/1000))
                            order = (klines[-1][4],klines[-1][0],x[0])
                            Database.sellOrder(connection,order)
                            msg = x[1]+ "\U0001F4B8 Satış: " + str(round(float(klines[-1][4]),8)).replace(".", "\\.") + Database.profitCalc(connection,x[0]) + "\n" + timeClose
                            setup.bot.send_message(-1001408874432, msg)
                            continue

                except BinanceAPIException as e:
                    print('Something went wrong in seller')
                    time.sleep(60)
                    client2 = Client(config.api_key2, config.api_secret2)
                    continue
                #except:
                #    print("unexpected error")
                #    time.sleep(60)
                #    client2 = Client(config.api_key2, config.api_secret2)
                #    continue
        else:
            time.sleep(20)

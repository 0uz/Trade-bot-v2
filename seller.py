import Database
from binance.client import Client
import config
import time
from indicator import MACDEMA
import setup

connection = Database.create_connection("test.db")
client = Client(config.api_key2, config.api_secret2)
TIME = "1 month ago UTC+3"

def macdAndRsiKlineSell():
    SYMBOLS = Database.getOpenOrder(connection)
    for x in SYMBOLS:
        close=[]
        klines = client.get_historical_klines(x[1], Client.KLINE_INTERVAL_1HOUR, TIME)
        time.sleep(0.1)
        if len(klines) > 26:
            for entry in klines:
                close.append(float(entry[4]))
            macdBuy, macdSell, macd, signal = MACDEMA(close)
            stop = close[-1] < x[2]
            if macdSell:
                order = (klines[-1][4],klines[-1][0],x[0])
                Database.sellOrder(connection,order)
                msg = x[1] + "\U0001F4B0 Satiş: " + str(round(float(klines[-1][4]),8)).replace(".", "\\.")
                setup.bot.send_message(-1001408874432, msg)
                print(msg)
            if stop:
                order = (klines[-1][4],klines[-1][0],x[0])
                Database.sellOrder(connection,order)
                msg = x[1]+ "\U0001F534 Stop: " + str(round(float(klines[-1][4]),8)).replace(".", "\\.")
                setup.bot.send_message(-1001408874432, msg)
                print(msg)


def seller():
    print("Seller is working...")
    while True:
        if Database.count_open_orders(connection) > 0:
            macdAndRsiKlineSell()
        else:
            time.sleep(20)

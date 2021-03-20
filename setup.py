
from operator import imod
from threading import Thread
from multiprocessing import Process
import telebot
import telegram
import buyer
import seller
import stop

bot = telebot.TeleBot("1628197070:AAFLvfUgbwO8qnY4YkQJ8yLHLoube-51GKc", parse_mode="MarkdownV2")

if __name__ == '__main__':
    buy = Thread(target=buyer.buyer)
    sell = Thread(target=seller.seller)
    stops = Thread(target=stop.stopTracker)
    tele = Thread(target=telegram.pool)

    buy.start()
    sell.start()
    stops.start()
    tele.start()

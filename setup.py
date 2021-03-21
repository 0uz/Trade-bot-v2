
from operator import imod
from threading import Thread
from multiprocessing import Process
import telebot
import telegram
import buyer
import seller
import stop
import googleDrive

bot = telebot.TeleBot("1628197070:AAFLvfUgbwO8qnY4YkQJ8yLHLoube-51GKc", parse_mode="MarkdownV2")

if __name__ == '__main__':
    buy = Process(target=buyer.buyer)
    sell = Process(target=seller.seller)
    stops = Process(target=stop.stopTracker)
    tele = Process(target=telegram.pool)
    drive = Process(target=googleDrive.upload)

    buy.start()
    sell.start()
    stops.start()
    tele.start()
    drive.start()

    buy.join()
    sell.join()
    stops.join()
    tele.join()
    drive.join()
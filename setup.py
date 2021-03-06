
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
    tele = Thread(target=telegram.pool)
    drive = Process(target=googleDrive.upload)
    driveDown = Process(target=googleDrive.downloadData)

    driveDown.start()
    driveDown.join()

    drive.start()
    tele.start()
    buy.start()
    sell.start()
    stops.start()
    

    drive.join()
    buy.join()
    sell.join()
    stops.join()
    
    
 
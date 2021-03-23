import Database
import setup
from telebot import types
from telebot import util
from googleDrive import uploadFile
connection = Database.create_connection("test.db")
print("Telegram is working...")

@setup.bot.message_handler(commands=['allTrades'])
def handle_command(message):
    msg = Database.allTradeTele(connection)
    splitted_text = util.split_string(msg, 3000)
    for text in splitted_text:
        setup.bot.send_message(message.chat.id, text)

@setup.bot.message_handler(commands=['profit'])
def handle_command(message):
    msg = Database.profitTele(connection)
    setup.bot.send_message(message.chat.id, msg)

@setup.bot.message_handler(commands=['altın'])
def handle_command(message):
    setup.bot.send_message(message.chat.id,"Para altında kardeşim")


@setup.bot.message_handler(commands=['stop'])
def handle_command(message):
    markup = types.ReplyKeyboardMarkup(row_width=2,one_time_keyboard=True)
    symbols = Database.getOpenOrder(connection)
    if len(symbols) >0:
        for x in symbols:
            itembtn1 = types.KeyboardButton(str(x[1]))
            markup.add(itembtn1)
        setup.bot.send_message(message.chat.id, "Coin seç: ", reply_markup=markup)
    else:
        setup.bot.send_message(message.chat.id, "Alış gerçekleşmemiş")

@setup.bot.message_handler()
def handle_all_message(message):
    if message.text == "oguzhan-backup-db" and message.chat.id == 923698949:
        uploadFile()
        setup.bot.send_message(message.chat.id,"Backup alindi")
    else:
        setup.bot.send_message(message.chat.id,Database.stopTele(connection,message.text))

def pool():
    setup.bot.polling()


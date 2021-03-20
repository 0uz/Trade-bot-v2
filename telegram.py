import Database
from setup import bot
import telebot
from telebot import types
connection = Database.create_connection("test.db")
print("Telegram is working...")
@bot.message_handler(commands=['profit'])
def handle_command(message):
    msg = Database.profitTele(connection)
    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=['altın'])
def handle_command(message):
    bot.send_message(message.chat.id,"Para altında kardeşim")


@bot.message_handler(commands=['stop'])
def handle_command(message):
    bot.send_message(message.chat.id,"Para altında kardeşim")
    markup = types.ReplyKeyboardMarkup(row_width=2)
    symbols = Database.getOpenOrder(connection)
    for x in symbols:
        itembtn1 = types.KeyboardButton(str(x[1]))
        markup.add(itembtn1)
    bot.send_message(message.chat.id, "Coin seç: ", reply_markup=markup)

@bot.message_handler()
def handle_all_message(message):
    bot.send_message(message.chat.id,Database.stopTele(connection,message.text))

bot.polling()


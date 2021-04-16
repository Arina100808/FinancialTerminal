import telebot
from telebot import types # necessary for creating buttons

import requests # to get information from URL

api_key = '370e7c78b5584f43a1d13d578e12a619' # Twelve data API key
# use URL to avoid errors while using "import twelvedata"


bot = telebot.TeleBot("1705290711:AAElqpKI_SSAglv77PMqnT3hAL4mLEXI-Lw")

# method of getting text messages
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/start" or message.text == "Hello":

        # prepare buttons
        keyboard = types.InlineKeyboardMarkup()
        # text and next step for each function
        key_share = types.InlineKeyboardButton(text='Check share price', callback_data='Share')
        key_news = types.InlineKeyboardButton(text='Get news', callback_data='News')
        # add button to the keyboard
        keyboard.add(key_share, key_news)

        # text message + show all available functions
        bot.send_message(message.from_user.id, text='Hello! Please select your next step.', reply_markup=keyboard)

    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Write /start.")
    else:
        bot.send_message(message.from_user.id, "I don't understand you. Write /help.")

# Button click handler
@bot.callback_query_handler(func=lambda call: True)
def answer(call):
# If button "Share" was chosen
    if call.data == "Share":
        msg = "Write the ticker symbol in this chat and I will send you its current OHLC prices."
        share_reply = bot.send_message(call.message.chat.id, msg)
        bot.register_next_step_handler(share_reply, get_ticker) #next step – function get_ticker

@bot.message_handler(commands=['text'])
def get_ticker(message):

    ticker = message.text
    interval = '1day'

    api_url = 'https://api.twelvedata.com/time_series?symbol=' + ticker +\
              '&interval=' + interval + '&outputsize=12&apikey=' + api_key
    try:
        OHLC = requests.get(api_url).json()
        price_open = OHLC['values'][0]['open']
        price_high = OHLC['values'][0]['high']
        price_low = OHLC['values'][0]['low']
        price_close = OHLC['values'][0]['close']

        answer = ticker + " (" + OHLC['meta']['exchange'] + "):\n" + \
                 "Open price: $" + price_open + "\n" + \
                 "High price: $" + price_high + "\n" + \
                 "Low price: $" + price_low + "\n" + \
                 "Close price: $" + price_close
        bot.send_message(message.from_user.id, answer)
        return

    except Exception:
        answer_error = "Couldn't get ticker data from the request.\n" +\
                 "Try asking about something popular, like GOOG or AAPL."
        reply = bot.send_message(message.from_user.id, answer_error)
        bot.register_next_step_handler(reply, get_ticker)  # next step – function get_ticker

bot.polling(none_stop=True, interval=0) # keep asking the bot if it had received any new messages
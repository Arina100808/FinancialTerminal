import telebot
from telebot import types # necessary for creating buttons

import requests # to get information from URL
from datetime import datetime # to get current data (and time)

api_key_stocks = '370e7c78b5584f43a1d13d578e12a619' # Twelve data API key
# use URL to avoid errors while using "import twelvedata"

api_key_news = '175edb9abf6f4edcae41e117ee5fd86a' # Newsapi API key

bot = telebot.TeleBot("1705290711:AAElqpKI_SSAglv77PMqnT3hAL4mLEXI-Lw")

def main_menu():
    # prepare buttons
    keyboard = types.InlineKeyboardMarkup()
    # text and next step for each function
    key_stock = types.InlineKeyboardButton(text='Check stock price', callback_data='Stock price')
    key_news = types.InlineKeyboardButton(text='Get news', callback_data='News')
    # add button to the keyboard
    keyboard.add(key_stock, key_news)
    return keyboard

# method of getting text messages
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '/start' or message.text == 'Hello':

        # keyboard + text message + show all available functions
        keyboard = main_menu()
        hello = 'Hello, ' + message.from_user.first_name + '! Please select your next step.'
        bot.send_message(message.from_user.id, text=hello, reply_markup=keyboard)

    elif message.text == '/help':
        bot.send_message(message.from_user.id, 'Write /start.')
    else:
        bot.send_message(message.from_user.id, 'I don\'t understand you. Write /help.')

# Button click handler
@bot.callback_query_handler(func=lambda call: True)
def answer(call):
# If button "Stock" was chosen
    if call.data == 'Stock price':
        msg_stock = 'Write the ticker symbol in this chat and I will send you its current OHLC prices.'
        stock_reply = bot.send_message(call.message.chat.id, msg_stock)
        bot.register_next_step_handler(stock_reply, get_ticker) #next step – function get_ticker
# If button "News" was chosen
    elif call.data == 'News':
        msg_news = 'Tell me what you want to know about.'
        news_reply = bot.send_message(call.message.chat.id, msg_news)
        bot.register_next_step_handler(news_reply, get_news) #next step – function get_news
# If button "Return" was chosen
    elif call.data == 'Return':
        # keyboard + text message + show all available functions
        keyboard_return = main_menu()
        return_msg = 'Please select your next step.'
        bot.send_message(call.message.chat.id, text=return_msg, reply_markup=keyboard_return)

def return_keyb():
    # prepare buttons (return to main menu)
    keyboard_return = types.InlineKeyboardMarkup()
    # text and next step for each function
    key_return = types.InlineKeyboardButton(text='Back to main menu', callback_data='Return')
    # add button to the keyboard
    keyboard_return.add(key_return)
    # text message + show all available functions
    return keyboard_return

@bot.message_handler(commands=['text'])
def get_ticker(message):

    ticker = message.text
    interval = '1day'

    api_url_stock = 'https://api.twelvedata.com/time_series?symbol=' + ticker +\
              '&interval=' + interval + '&outputsize=12&apikey=' + api_key_stocks

    keyboard_ticker = return_keyb()
    # text and next step for each function
    key_another_stock = types.InlineKeyboardButton(text='Check another stock price', callback_data='Stock price')
    # add button to the keyboard
    keyboard_ticker.add(key_another_stock)

    try:
        OHLC = requests.get(api_url_stock).json()
        price_open = OHLC['values'][0]['open']
        price_high = OHLC['values'][0]['high']
        price_low = OHLC['values'][0]['low']
        price_close = OHLC['values'][0]['close']

        answer_stock = ticker + " (" + OHLC['meta']['exchange'] + "):\n" + \
                 'Open price: $' + price_open + '\n' + \
                 'High price: $' + price_high + '\n' + \
                 'Low price: $' + price_low + '\n' + \
                 'Close price: $' + price_close

        bot.send_message(message.from_user.id, text=answer_stock, reply_markup=keyboard_ticker)

        #bot.register_next_step_handler(next_ticker, get_ticker)

    except Exception:
        answer_error_stock = 'Couldn\'t get ticker data from the request.\n' +\
                 'Try asking about something popular, like GOOG or AAPL.'
        bot.send_message(message.from_user.id, text=answer_error_stock, reply_markup=keyboard_ticker)

@bot.message_handler(commands=['text'])
def get_news(message):

    query = message.text
    today = datetime.now().date()

    api_url_news = 'https://newsapi.org/v2/everything?q=' + query +\
              '&from=' + '2021-04-20' + '&language=en' + '&sortBy=popularity' + '&apiKey=' + api_key_news #str(today)

    keyboard_news = return_keyb()
    # text and next step for each function
    key_other_news = types.InlineKeyboardButton(text='Check other news', callback_data='News')
    # add button to the keyboard
    keyboard_news.add(key_other_news)

    try:
        NEWS = requests.get(api_url_news).json()
        articles = NEWS['articles']
        answer_news = 'Top 15 results:\n\n'

        for i in range(15):
            n = i + 1 # № of an article
            answer_news += str(n) + '. ' + '[' + articles[i]['title'] + '](' + articles[i]['url'] + ')' + "\n\n"

        next_news = bot.send_message(message.from_user.id, text=answer_news, parse_mode='Markdown',
                                     reply_markup=keyboard_news) # print 15 articles

    except Exception:
        answer_error_news = 'Couldn\'t find news about ' + query + '.\n' +\
                 'Try asking about something else.'
        bot.send_message(message.from_user.id, text=answer_error_news, reply_markup=key_other_news)

bot.polling(none_stop=True, interval=0) # keep asking the bot if it had received any new messages

import telebot
from telebot import types # necessary for creating buttons
import requests # to get information from URL
from datetime import datetime # to get current data (and time)
import sqlite3

api_key_earnings = 'EPKP2530O3QKL41J' # Alpha Vantage API key
api_key_stocks = '370e7c78b5584f43a1d13d578e12a619' # Twelve data API key
api_key_news = '175edb9abf6f4edcae41e117ee5fd86a' # Newsapi API key

bot = telebot.TeleBot("1705290711:AAElqpKI_SSAglv77PMqnT3hAL4mLEXI-Lw")

# Database for portfolio
conn = sqlite3.connect('database/datab.db', check_same_thread=False, detect_types=sqlite3.PARSE_DECLTYPES)
db = conn.cursor()

# method of getting text messages
@bot.message_handler(content_types=['text'])
def get_message(message):
    if message.text == 'Start' or message.text == 'Hello' or message.text == 'start' or message.text ==\
            'hello' or message.text == '/start' or message.text == 'Hi' or message.text == 'hi':

        # keyboard + text message + show all available functions
        keyboard = main_menu()
        hello = 'Hello, ' + message.from_user.first_name + '! Please select your next step.'
        bot.send_message(message.from_user.id, text=hello, reply_markup=keyboard)

    elif message.text == '/help':
        bot.send_message(message.from_user.id, 'Write /start.')
# Pressing button = sending text message

# If button "Back to main menu" was chosen
    elif message.text == 'Back to main menu':
    # keyboard + text message + show all available functions
        keyboard_return = main_menu()
        return_msg = 'Please select your next step.'
        bot.send_message(message.chat.id, text=return_msg, reply_markup=keyboard_return)
# If button "Stock" was chosen
    elif message.text == 'Stock price':
        msg_stock = 'Write the ticker symbol in this chat and I will send you its current OHLC prices, ' \
                    'earning per share and P/E ratio.'
        stock_reply = bot.send_message(message.chat.id, msg_stock, reply_markup=return_keyb())
        bot.register_next_step_handler(stock_reply, get_ticker) #next step – function get_ticker
# If button "News" was chosen
    elif message.text == 'Get news':
        msg_news = 'Tell me what you want to know about.'
        news_reply = bot.send_message(message.chat.id, msg_news, reply_markup=return_keyb())
        bot.register_next_step_handler(news_reply, get_news) #next step – function get_news
# If button "Exchange rate" was chosen
    elif message.text == 'Exchange rate':
        msg_exrate = 'Write the currency pair (can be either forex or cryptocurrency) using slash(/) delimiter.' \
                     'E.g. "EUR/USD".'
        exrate_reply = bot.send_message(message.chat.id, msg_exrate, reply_markup=return_keyb())
        bot.register_next_step_handler(exrate_reply, get_exrate) #next step – function get_exrate
# If button "My portfolio" was chosen
    elif message.text == 'My portfolio' or message.text == 'Update information' or message.text == 'Back':
        keyboard_portfolio = portfolio_keyb()
        msg_portfolio = get_portfolio(message)
        port_reply = bot.send_message(message.chat.id, msg_portfolio, reply_markup=keyboard_portfolio)
        bot.register_next_step_handler(port_reply, my_portfolio)
    elif message.text == 'Add stock' or message.text == 'Delete stock':
        my_portfolio(message)
    else:
        bot.send_message(message.from_user.id, 'I don\'t understand you. Write /help.')

def main_menu():
    # prepare buttons
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    # text and next step for each function
    key_stock = types.KeyboardButton(text='Stock price')
    key_news = types.KeyboardButton(text='Get news')
    key_erate = types.KeyboardButton(text='Exchange rate')
    key_portfolio = types.KeyboardButton(text='My portfolio')
    # add button to the keyboard
    keyboard.add(key_stock, key_news, key_erate, key_portfolio)
    return keyboard

def return_keyb():
    # prepare buttons (return to main menu)
    keyboard_return = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    # text and next step for each function
    key_return = types.KeyboardButton(text='Back to main menu')
    # add button to the keyboard
    keyboard_return.add(key_return)
    # text message + show all available functions
    return keyboard_return

def get_ticker(message):

    if message.text == 'Back to main menu':
        get_message(message)
        return

    ticker = message.text
    interval = '1day'

    api_url_stock = 'https://api.twelvedata.com/time_series?symbol=' + ticker + \
                    '&interval=' + interval + '&outputsize=12&apikey=' + api_key_stocks

    api_url_earning = 'https://www.alphavantage.co/query?function=EARNINGS&symbol=' +\
                      ticker + '&apikey=' + api_key_earnings

    api_url_change = 'https://api.twelvedata.com/quote?symbol=' + ticker + '&apikey=' +\
                     api_key_stocks

    try:
        OHLC = requests.get(api_url_stock).json()
        Earning = requests.get(api_url_earning).json()
        Change = requests.get(api_url_change).json()

        price_open = round(float(OHLC['values'][0]['open']), 2)
        price_high = round(float(OHLC['values'][0]['high']), 2)
        price_low = round(float(OHLC['values'][0]['low']), 2)
        price_close = float(OHLC['values'][0]['close'])
        EPS = float(Earning['annualEarnings'][0]['reportedEPS'])
        ratio = round(price_close/EPS, 2)

        str_change = str(round(float(Change['percent_change']), 2))
        if float(Change['percent_change']) > 0:
            str_change = '+' + str_change
            emoji = '⬆'
        elif float(Change['percent_change']) < 0:
            emoji = '⬇'
        else:
            emoji = ''

        answer_stock = OHLC['meta']['symbol'] + " (" + OHLC['meta']['exchange'] + "):\n" + \
                 'Open price: $' + str(price_open) + '\n' + \
                 'High price: $' + str(price_high) + '\n' + \
                 'Low price: $' + str(price_low) + '\n' + \
                 'Close price: $' + str(round(price_close, 2)) + '\n' + \
                 emoji + 'Change from the previous day: ' + str_change + '%\n' + \
                 'EPS: ' + str(round(EPS, 2)) + '\n' + \
                 'P/E: ' + str(ratio)

        next_ticker = bot.send_message(message.from_user.id, text=answer_stock)
        bot.register_next_step_handler(next_ticker, get_ticker)

    except Exception:
        answer_error_stock = 'Couldn\'t get ticker data from the request.\n' +\
                 'Try asking about something popular, like GOOG or AAPL.'
        next_ticker_2 = bot.send_message(message.from_user.id, text=answer_error_stock)
        bot.register_next_step_handler(next_ticker_2, get_ticker)

def get_news(message):

    if message.text == 'Back to main menu':
        get_message(message)
        return

    query = message.text
    today = datetime.now().date()

    api_url_news = 'https://newsapi.org/v2/everything?q=' + query +\
              '&from=' + str(today) + '&language=en' + '&sortBy=popularity' + '&apiKey=' + api_key_news

    try:
        NEWS = requests.get(api_url_news).json()
        articles = NEWS['articles']
        answer_news = 'Top 15 news about ' + query + ':\n\n'

        for i in range(15):
            n = i + 1 # № of an article
            answer_news += str(n) + '. ' + '[' + articles[i]['title'] + '](' + articles[i]['url'] + ')' + "\n\n"

        next_news = bot.send_message(message.from_user.id, text=answer_news, parse_mode='Markdown') # print 15 articles
        bot.register_next_step_handler(next_news, get_news)

    except Exception:
        answer_error_news = 'Couldn\'t find news about ' + query + '.\n' +\
                 'Try asking about something else.'
        next_news_2 = bot.send_message(message.from_user.id, text=answer_error_news)
        bot.register_next_step_handler(next_news_2, get_news)

def get_exrate(message):

    if message.text == 'Back to main menu':
        get_message(message)
        return

    pair = message.text

    api_url_exrate = 'https://api.twelvedata.com/exchange_rate?symbol=' + pair + '&precision=4&apikey=' + api_key_stocks
    api_url_change = 'https://api.twelvedata.com/quote?symbol=' + pair + '&apikey=' + \
                     api_key_stocks

    try:
        exrate = requests.get(api_url_exrate).json()
        rate = exrate['rate']
        Change = requests.get(api_url_change).json()
        str_change = str(round(float(Change['percent_change']), 2))
        if float(Change['percent_change']) > 0:
            str_change = '+' + str_change
            emoji = '⬆'
        elif float(Change['percent_change']) < 0:
            emoji = '⬇'
        answer_exrate = exrate['symbol'] + " = " + str(rate) + "\n" + \
        emoji + 'Change from the previous day: ' + str_change + '%'

        next_exrate = bot.send_message(message.from_user.id, text=answer_exrate)
        bot.register_next_step_handler(next_exrate, get_exrate)

    except Exception:
        answer_error_exrate = 'Couldn\'t get exchange rate for the currency pair.' \
                              'Check if the pair is written correctly: using slash(/) delimiter. E.g. "EUR/USD".'
        next_exrate_2 = bot.send_message(message.from_user.id, text=answer_error_exrate)
        bot.register_next_step_handler(next_exrate_2, get_exrate)

def portfolio_keyb():
    keyboard_port = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    key_return = types.KeyboardButton(text='Back to main menu')
    key_add = types.KeyboardButton(text='Add stock')
    key_delete = types.KeyboardButton(text='Delete stock')
    key_update = types.KeyboardButton(text='Update information')
    keyboard_port.add(key_return, key_update, key_add, key_delete)
    return keyboard_port

def setup():
    tblstmt = "CREATE TABLE IF NOT EXISTS Portfolio (user_id INTEGER, ticker TEXT, number_stocks INTEGER," \
              "cost FLOAT)"
    user_ididx = "CREATE INDEX IF NOT EXISTS user_idIndex ON Portfolio (user_id ASC)"
    tickeridx = "CREATE INDEX IF NOT EXISTS tickerIndex ON Portfolio (ticker ASC)"
    conn.execute(tblstmt)
    conn.execute(tickeridx)
    conn.execute(user_ididx)
    conn.commit()

def get_portfolio(message):
    setup()
    all_stocks = db.execute('SELECT * FROM Portfolio WHERE user_id IS ?', (message.from_user.id, )).fetchall()
    if len(all_stocks) == 0:
        return 'My portfolio:\n\nEmpty'
    result = 'My portfolio:\n\n'
    sum_price = 0
    sum_cost = 0
    try:
        for stock in all_stocks:
            ticker = stock[1]
            interval = '1day'
            api_url_stock = 'https://api.twelvedata.com/time_series?symbol=' + ticker + \
                            '&interval=' + interval + '&outputsize=12&apikey=' + api_key_stocks

            OHLC = requests.get(api_url_stock).json()
            price_close = float(OHLC['values'][0]['close'])
            price = stock[2] * price_close
            cost = stock[3]
            change = price - cost
            str_change = str(round(change, 3))
            if change >= 0:
                str_change = '+' + str_change
                result = result + '⬆'
                str_status = 'Gain: '
            elif change < 0:
                result = result + '⬇'
                str_status = 'Loss: '
            result = result + ticker + ':\n' + str_status + str_change + '$\n' + 'Current price: ' + str(round(price, 3)) + '$ (' +\
                    str(stock[2]) + ' units)\n\n'
            sum_price += price
            sum_cost += cost
    except Exception:
        answer_error_port = 'Something went wrong. Please try again.'
        next_post = bot.send_message(message.from_user.id, text=answer_error_port)
        bot.register_next_step_handler(next_post, ...)
    sum_change = sum_price - sum_cost
    str_sum_change = str(round(sum_change, 3))
    if sum_change >= 0:
        str_sum_change = '+' + str_sum_change
        str_total_status = 'Total gain: '
    else:
        str_total_status = 'Total loss: '
    result = result + 'Sum: ' + str(round(sum_price, 3)) + '$\n' + str_total_status + str_sum_change + '$'

    return result

def my_portfolio(message):
    if message.text == 'Back to main menu':
        get_message(message)
        return
    elif message.text == 'Update information':
        get_message(message)
        return
    elif message.text == 'Add stock':
        bot.send_message(message.from_user.id, text='Write the ticker symbol, number of bought stocks, price per unit, '
                        'commission fee in % (for example: "AAPL, 5, 125.76, 0.3").', reply_markup=
                        types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton(text='Back')))
        bot.register_next_step_handler(message, p_add_stock)
    elif message.text == 'Delete stock':
        bot.send_message(message.from_user.id, text='Write the ticker symbol, number of sold stocks, price per unit, '
                        'commission fee in % (for example: "AAPL, 3, 128.94, 0.3").', reply_markup=
                         types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton(text='Back')))
        bot.register_next_step_handler(message, p_sell_stock)
    else:
        get_message(message)

def p_add_stock(message):
    if message.text == 'Back':
        keyboard_portfolio = portfolio_keyb()
        msg_portfolio = 'Please select your next step.'
        port_reply = bot.send_message(message.chat.id, msg_portfolio, reply_markup=keyboard_portfolio)
        bot.register_next_step_handler(port_reply, my_portfolio)
        return
    user_id = message.from_user.id
    line = message.text.split(",")
    ticker = line[0]
    url_about_stock = 'https://api.twelvedata.com/stocks?symbol=' + ticker + '&exchange=NASDAQ'
    try:
        about_stock = requests.get(url_about_stock).json()
        symbol = about_stock['data'][0]['symbol']
        ticker = symbol
    except Exception:
        answer = 'Wrong ticker symbol.'
        port_reply = bot.send_message(message.chat.id, answer)
        bot.register_next_step_handler(port_reply, p_add_stock)
        return
    number = int(line[1])
    price = float(line[2])
    percent = float(line[3])
    cost = number * price * (1 + percent/100)
    db.execute('SELECT * FROM Portfolio WHERE (user_id IS ? AND ticker IS ?)', (user_id, ticker))
    if db.fetchone() == None:
        db.execute('INSERT INTO Portfolio (user_id, ticker, number_stocks, cost) VALUES (?, ?, ?, ?)',
                   (user_id, ticker, number, cost))
        conn.commit()
    else:
        row = db.execute('SELECT * FROM Portfolio WHERE (user_id IS ? AND ticker IS ?)', (user_id, ticker))
        old_number = row.fetchone()[2]
        row = db.execute('SELECT * FROM Portfolio WHERE (user_id IS ? AND ticker IS ?)', (user_id, ticker))
        old_cost = row.fetchone()[3]
        new_number = old_number + number
        new_cost = old_cost + cost
        db.execute('UPDATE Portfolio SET number_stocks = ? where (user_id = ? AND ticker IS ?)', (new_number, user_id, ticker))
        db.execute('UPDATE Portfolio SET cost = ? where (user_id = ? AND ticker IS ?)', (new_cost, user_id, ticker))
        conn.commit()
    answer = get_portfolio(message)
    next = bot.send_message(message.from_user.id, text=answer)
    bot.register_next_step_handler(next, p_add_stock)

def p_sell_stock(message):
    if message.text == 'Back':
        keyboard_portfolio = portfolio_keyb()
        msg_portfolio = 'Please select your next step.'
        port_reply = bot.send_message(message.chat.id, msg_portfolio, reply_markup=keyboard_portfolio)
        bot.register_next_step_handler(port_reply, my_portfolio)
        return
    user_id = message.from_user.id
    line = message.text.split(",")
    ticker = line[0]
    url_about_stock = 'https://api.twelvedata.com/stocks?symbol=' + ticker + '&exchange=NASDAQ'
    try:
        about_stock = requests.get(url_about_stock).json()
        symbol = about_stock['data'][0]['symbol']
        ticker = symbol
    except Exception:
        answer = 'Wrong ticker symbol.'
        port_reply = bot.send_message(message.chat.id, answer)
        bot.register_next_step_handler(port_reply, p_add_stock)
        return
    number = int(line[1])
    price = float(line[2])
    percent = float(line[3])
    revenue = number * price * (1 - percent/100)
    db.execute('SELECT * FROM Portfolio WHERE (user_id IS ? AND ticker IS ?)', (user_id, ticker))
    if db.fetchone() == None:
        answer = 'Your portfolio doesn\'t contain this stock.'
        port_reply = bot.send_message(message.chat.id, answer)
        bot.register_next_step_handler(port_reply, p_sell_stock)
        return
    else:
        row = db.execute('SELECT * FROM Portfolio WHERE (user_id IS ? AND ticker IS ?)', (user_id, ticker))
        old_number = row.fetchone()[2]
        row = db.execute('SELECT * FROM Portfolio WHERE (user_id IS ? AND ticker IS ?)', (user_id, ticker))
        old_cost = row.fetchone()[3]
        if number > old_number:
            answer = 'Not enough stocks to sell.'
            port_reply = bot.send_message(message.chat.id, answer)
            bot.register_next_step_handler(port_reply, p_sell_stock)
            return
        elif number == old_number and round(revenue, 3) == round(old_cost, 3):
            db.execute('DELETE FROM Portfolio WHERE (user_id IS ? AND ticker IS ?)', (user_id, ticker))
            conn.commit()
        else:
            new_number = old_number - number
            new_cost = old_cost - revenue
            db.execute('UPDATE Portfolio SET number_stocks = ? where (user_id = ? AND ticker IS ?)', (new_number, user_id, ticker))
            db.execute('UPDATE Portfolio SET cost = ? where (user_id = ? AND ticker IS ?)', (new_cost, user_id, ticker))
            conn.commit()

    answer = get_portfolio(message)
    next = bot.send_message(message.from_user.id, text=answer)
    bot.register_next_step_handler(next, p_sell_stock)

bot.polling(none_stop=True, interval=0) # keep asking the bot if it had received any new messages

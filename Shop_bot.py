#5698182014:AAHzfTKiXtntkvZg5OU0YLG_N76EN5NlFOg
import telebot
import requests

from bs4 import BeautifulSoup
import re
import datetime as datetime
import sqlite3
from telebot import types

name = ''
tel = ''
product = ''
conn = sqlite3.connect("shops_001.db")
cursor = conn.cursor()
#cursor.execute("""CREATE TABLE IF NOT EXISTS SHOP_001 (id INTEGER PRIMARY KEY AUTOINCREMENT,
#name TEXT, category TEXT, kol INT, price INT,sklad  INT)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS ZAKAZ_001(id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT, tel TEXT, product  INT)""")

#cursor.execute('''INSERT INTO SHOP_001 (name,category,kol,price,sklad) VALUES (?,?,?,?,?)''', ("IPhone 13 PRO Max", "phone", 13,500,2))
#cursor.execute('''INSERT INTO SHOP_001 (name,category,kol,price,sklad) VALUES (?,?,?,?,?)''', ("IPhone 12", "phone", 4,235,2))
#cursor.execute('''INSERT INTO SHOP_001 (name,category,kol,price,sklad) VALUES (?,?,?,?,?)''', ("IPhone 11", "phone", 7,200,1))
#cursor.execute('''INSERT INTO SHOP_001 (name,category,kol,price,sklad) VALUES (?,?,?,?,?)''', ("LG 55 MODE", "TV", 14,600,1))
#cursor.execute('''INSERT INTO SHOP_001 (name,category,kol,price,sklad) VALUES (?,?,?,?,?)''', ("LG 43", "TV", 14,450,2))

#cursor.execute("""CREATE TABLE IF NOT EXISTS zakaz_001 (id INTEGER PRIMARY KEY AUTOINCREMENT,
#name TEXT, tel TEXT, product  INT)""")
#cursor.execute('''INSERT INTO zakaz_001 (name,tel,product) VALUES (?,?,?)''', ("Margo", "+3753333333333",'Apple 12 PRO'))
#conn.commit()
#cursor.execute('''SELECT * FROM SHOP_001''')
#k = cursor.fetchall()
#print(k)
def get_usd():
    url = 'https://select.by/kurs/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    quotes = soup.find('span').text
    quotes = re.sub("^\s+|\n|\r|\s+$", '', quotes)
    return quotes

def get_time():
    time  = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    return time
def get_pogoda():
    url = 'https://pogoda.mail.ru/prognoz/minsk/extended/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    quotes_1 = soup.find('span',class_ = 'hdr__inner')
    quotes = soup.find_all('span',class_ = 'text text_block text_bold_medium margin_bottom_10')
    q = []
    for i in quotes:
        q.append(i.text)
    a = f'{quotes_1.text}\nУтром:{q[1]} \nДнем:{q[2]}\nВечером:{q[3]}'
    return a

def get_all(a):
    cursor = a.cursor()
    cursor.execute('''SELECT * FROM SHOP_001''')
    k = cursor.fetchall()
    return k

bot = telebot.TeleBot('5698182014:AAHzfTKiXtntkvZg5OU0YLG_N76EN5NlFOg')

@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    bot.send_message(message.chat.id,f'Привет, {name}')
    bot.send_message(message.chat.id, f'{name}, возможно ты хочешь уточнить курс(/kurs) или узнать точное время (/time)? погоду(/pogoda),'
                                      f'инфо(/info), оформить заказ (/zakaz)?')

@bot.message_handler(commands=['time'])
def time (message):
    bot.send_message(message.chat.id,f'Точное время, {get_time()}')

@bot.message_handler(commands=['kurs'])
def kurs (message):
    bot.send_message(message.chat.id,f'Курс USD на данный момент:, {get_usd()}')

@bot.message_handler(commands=['pogoda'])
def pogoda (message):
    bot.send_message(message.chat.id,f' {get_pogoda()}')


@bot.message_handler(func=lambda x:x.text == 'Как дела?')
def how_are_you(message):
    name = message.from_user.first_name
    bot.send_message(message.chat.id, f'Мои хорошо, как твои? , {name}')

@bot.message_handler(commands=['info'])
def info (message):
    keyboard = types.InlineKeyboardMarkup()
    name_btn = types.InlineKeyboardButton(text = "По имени", callback_data = 'name')
    sklad_btn = types.InlineKeyboardButton(text="По складу", callback_data='sklad')
    category_btn = types.InlineKeyboardButton(text="По категории", callback_data='category')
    all_btn = types.InlineKeyboardButton(text="Вывести все", callback_data='out_put_all')
    keyboard.add(name_btn,sklad_btn,category_btn,all_btn)
    bot.send_message(message.chat.id, 'Выберите способ сортировки ', reply_markup=keyboard)
    #sent = bot.reply_to(message, "Выберите способ сортировки (name/category/sklad/all)",reply_)
    #bot.register_next_step_handler(sent,vvod)

@bot.message_handler(commands=['zakaz'])
def zakaz (message):
    name = message.from_user.first_name
    s = bot.send_message(message.chat.id, f'Введи свой номер телефона:, {name}')
    bot.register_next_step_handler(s, vvod_tel)

@ bot.callback_query_handler(func=lambda call:True)
def call_back_worker(call):
    if call.data == 'name':
        sent = bot.send_message(call.message.chat.id, 'Сортируем по имени. Какой товар вас интересует?')
        bot.register_next_step_handler(sent,vvod_name)
    elif call.data == 'sklad':
        sent = bot.send_message(call.message.chat.id, 'Сортируем по складу. Выбираем склад(1 или 2)?')
        bot.register_next_step_handler(sent, vvod_sklad)
    elif call.data == 'category':
        sent = bot.send_message(call.message.chat.id, 'Сортируем по категории . Выбираем категорию?')
        bot.register_next_step_handler(sent, vvod_category)
    elif call.data == 'out_put_all':
        bot.send_message(call.message.chat.id, 'Наличие товара на всех складах:')
        conn = sqlite3.connect("shops_001.db")
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM SHOP_001''')
        k = cursor.fetchall()
        #bot.send_message(call.message.chat.id, f'{k}')
        obertka(call.message, k)


def vvod_name(message):
    name = message.text
    conn = sqlite3.connect("shops_001.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM SHOP_001 WHERE name = ?''',(name,))
    k = cursor.fetchall()
    #bot.send_message(message.chat.id, f'{k}')
    obertka(message, k)

def vvod_sklad(message):
    sklad = int(message.text)
    conn = sqlite3.connect("shops_001.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM SHOP_001 WHERE sklad = ?''', (sklad,))
    k = cursor.fetchall()
    #bot.send_message(message.chat.id, f'{k}')
    obertka(message, k)

def vvod_category(message):
    category = message.text
    conn = sqlite3.connect("shops_001.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM SHOP_001 WHERE category = ?''', (category,))
    k = cursor.fetchall()
    #bot.send_message(message.chat.id, f'{k}')
    obertka(message,k)


def obertka(message,a):
    for i in a:
        s = f'Имя: {i[1]},  Категория: {i[2]}, Остаток: {i[3]} шт. ,Цена: {i[4]} у.е ,Склад: {i[5]}'
        bot.send_message(message.chat.id, f'{s}')

def vvod_tel(message):
    global name
    name = message.from_user.first_name
    global tel
    tel = message.text
    sent = bot.send_message(message.chat.id, 'Введите название продукт:')
    bot.register_next_step_handler(sent, vvod_product)

def vvod_product(message):
    global product
    product = message.text
    bot.send_message(message.chat.id, f"{name}, интересующий вас товар: {product}, добавлен, после рассмотрения с вами свяжется"
                                      f" менеджер по указанному  номеру телефна:{tel}")

    conn = sqlite3.connect("shops_001.db")
    cursor = conn.cursor()

    cursor.execute('''INSERT INTO zakaz_001 (name,tel,product) VALUES (?,?,?)''',
                   (name, tel, product))
    cursor.execute('''SELECT * FROM zakaz_001''')
    k = cursor.fetchall()
    print(k)





bot.polling(non_stop=True)

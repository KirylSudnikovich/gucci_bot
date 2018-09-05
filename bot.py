# coding=utf-8
import telebot
import pyowm
import os
import requests

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from telebot import types
from flask import Flask, request

bot = telebot.TeleBot('438575528:AAFI-KOAymYqaI9MTETmb8T0x7o6yn3n3NU')
db_string = "postgres://kijpshfotqwgvt:0e75be68670312edf129a3b369449d8264db3d5d73dc6c859078df6bd16309b1@ec2-54-235" \
            "-219-113.compute-1.amazonaws.com:5432/ddeq2v86k3vqn8"

server = Flask(__name__)
server.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://poxaczynhbqhsg' \
                                           ':f30e823cc90570bbb36f05eb5224a1bb373663a27bfaa18b6473b10a78421e60@ec2-54' \
                                           '-243-39-245.compute-1.amazonaws.com:5432/dc4t2u8dg4hoee'
db = SQLAlchemy(server)


class User(db.Model):
    username = db.Column(db.String(80), unique=True)
    group = db.Column(db.Integer, primary_key=False)
    id = db.Column(db.Integer, primary_key=True)

    def __init__(self, username, group, id):
        self.username = username
        self.group = group
        self.id = id


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Hello, ' + message.from_user.first_name)
    ourUser = db.session.query(User).filter_by(username=str(message.from_user.first_name)).first()
    if ourUser:
        bot.send_message(message.chat.id, 'Вы уже зарегестрированы.')
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=1)
        markup.add(*[types.KeyboardButton(name) for name in ['Изменить номер группы', 'Вернуться в меню']])
        msg = bot.send_message(message.chat.id, 'Что делаем дальше?',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, getNewNumber)
    else:
        msg = bot.send_message(message.chat.id, 'Введи номер своей группы')
        bot.register_next_step_handler(msg, start1)


def start1(msg3):
    if len(msg3.text) > 0:
        sTemp = 'https://students.bsuir.by/api/v1/studentGroup/schedule?studentGroup='
        sTemp2 = sTemp + str(msg3.text)
        r = requests.get(sTemp2)
        try:
            bsche = r.json()
            grNum = int(msg3.text)
            mId = int(str(msg3.from_user.id))
            user = User(str(msg3.from_user.first_name), grNum, mId)
            db.session.add(user)
            db.session.commit()
            bot.send_message(msg3.chat.id, 'Вы успешно зарегистрировались')
        except:
            bot.send_message(msg3.chat.id, 'Такой группы не существует')


def getNewNumber(msg2):
    if msg2.text == 'Изменить номер группы':
        newGr = bot.send_message(msg2.chat.id, 'Введите номер группы',
                                 reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(newGr, checkSchedule)
    else:
        bot.send_message(msg2.chat.id, 'Возвращаемся в главное меню',
                         reply_markup=types.ReplyKeyboardRemove())


def checkSchedule(m1):
    sTemp = 'https://students.bsuir.by/api/v1/studentGroup/schedule?studentGroup='
    sTemp2 = sTemp + str(m1.text)
    r = requests.get(sTemp2)
    try:
        bsche = r.json()
        newGrNum = int(m1.text)
        ourUser = db.session.query(User).filter_by(username=str(m1.from_user.first_name)).first()
        ourUser.group = newGrNum
        db.session.commit()
        bot.send_message(m1.chat.id, 'Номер группы успешно изменен')
    except:
        bot.send_message(m1.chat.id, 'Такой группы не существует')


@bot.message_handler(commands=['dbcreate'])
def start(message):
    # db.create_all()
    bot.send_message(message.chat.id, 'База данных создана!')


@bot.message_handler(commands=['killme'])
def killFromDb(message):
    ourUser = db.session.query(User).filter_by(id=str(message.from_user.id)).first()
    if ourUser:
        db.session.delete(ourUser)
        db.session.commit()
        bot.send_message(message.chat.id, 'Вы успешно выпилились. Земля вам пухом')
    else:
        bot.send_message(message.chat.id, 'Тут нечего выпиливать так-то')


@bot.message_handler(commands=['rollback'])
def start(message):
    db.session.remove()
    bot.send_message(message.chat.id, 'Закончили')


@bot.message_handler(commands=['adddb'])
def start3(message):
    bot.reply_to(message, 'Hello, ' + message.from_user.first_name)
    msg = bot.send_message(message.chat.id, 'Введи номер своей группы')
    bot.register_next_step_handler(msg, start4)


def start4(msg):
    grNum = int(msg.text)
    user = User(str(msg.from_user.first_name) + 'keeek', grNum + 3)
    db.session.add(user)
    db.session.commit()
    bot.send_message(msg.chat.id, 'Вы успешно зарегистрировались')


@bot.message_handler(commands=['about'])
def about(message):
    bot.send_message(message.chat.id, '@sad_snitch\nhttps://vk.com/snitch_sad')


@bot.message_handler(commands=['friday'])
def betapyatnica(message):
    for file in os.listdir('pics/'):
        if file == 'stas.jpg':
            if file.split('.')[-1] == 'jpg':
                f = open('pics/' + file, 'rb')
                bot.send_photo(message.chat.id, "AgADAgAD9KgxGwM2IUlFUAw9VPe7p5wRMw4ABEzE89Z8cqS6-CsBAAEC",
                               caption='Пинта - +375293977895\nЯрКальян - +375291455531\nМята на Дзержинского - '
                                       '+375295362362\nМята Восток - +375447913333\nThe Office - +375299170493')


@bot.message_handler(commands=['exams'])
def GetExams(message):
    s = ""
    ourUser = db.session.query(User).filter_by(username=str(message.from_user.first_name)).first()
    if ourUser:
        numGroup = ourUser.group
        sTemp1 = 'https://students.bsuir.by/api/v1/studentGroup/schedule?studentGroup='
        sTemp2 = str(numGroup)
        sTemp3 = sTemp1 + sTemp2
        r = requests.get(sTemp3)
        bsche = r.json()
        bschedule = bsche["examSchedules"]
        if not bschedule:
            bot.send_message(message.chat.id, 'Ошибка получения расписания.')
        else:
            s = ""
            for i in bschedule:
                wDay = i["weekDay"]
                dSchedule = i['schedule'][0]
                neaud = i['schedule'][0]
                aud = neaud['auditory'][0]
                emp = dSchedule["employee"][0]
                s += '\n\n\n' + u'\U0001F4C5' + ' ' + wDay + '\n'
                s += u'\U0001F4C4' + ' ' + dSchedule['lessonType'] + '\n'
                s += u'\U0001F4D2' + ' ' + dSchedule['subject'] + '\n'
                s += u'\U0001F3E2' + ' ' + aud + '\n'
                s += u'\U0001F550' + ' ' + dSchedule['startLessonTime'] + '\n'
                s += u'\U0001F47B' + emp['lastName'] + ' ' + emp['firstName'] + ' ' + emp['middleName']
            bot.send_message(message.chat.id, s)


@bot.message_handler(commands=['bsuir'])
def getSchedule(message):
    s = ""
    ourUser = db.session.query(User).filter_by(username=str(message.from_user.first_name)).first()
    if ourUser:
        numGroup = ourUser.group
        sTemp1 = 'https://students.bsuir.by/api/v1/studentGroup/schedule?studentGroup='
        sTemp2 = str(numGroup)
        sTemp3 = sTemp1 + sTemp2
        r = requests.get(sTemp3)
        bsche = r.json()
        bschedule = bsche["todaySchedules"]
        if not bschedule:
            bot.send_message(message.chat.id, 'Сегодня нет занятий. Just chill, homie.')
        else:
            for i in bschedule:
                if i['subject'] != "ФизК" and i['subject'] != "ИКГ":
                    emp = i["employee"][0]
                s += u'\U0001F4D6' + str(i['subject']) + '\n'
                s += u'\U000023F3' + str(i['lessonTime']) + '\n'
                if i['subject'] != "ФизК":
                    s += u'\U0001F3E2' + str(i['auditory'][0]) + '\n'
                    if int(i['numSubgroup']) != 0:
                        s += u'\U0001F38E' + str(i['numSubgroup']) + ' подгруппа ' + '\n'
                if i['subject'] != "ФизК" and i['subject'] != "ИКГ":
                    s += u'\U0001F47D' + str(emp['lastName']) + ' ' + str(emp['firstName']) + ' ' + str(
                        emp['middleName']) + '\n'
                s += '\n'
        bot.send_message(message.chat.id, s)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=2)
        markup.add(*[types.KeyboardButton(name) for name in ['Завтра', 'Назад']])
        msg = bot.send_message(message.chat.id, 'Что делаем дальше?',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, Tomorrow)
    else:
        bot.send_message(message.chat.id, 'Вы не зарегистрированы. Сперва пройдите регистрацию по команде /start')


def Tomorrow(m):
    ourUser = db.session.query(User).filter_by(username=str(m.from_user.first_name)).first()
    group = ourUser.group
    if m.text == 'Завтра':
        s = ""
        sTemp1 = 'https://students.bsuir.by/api/v1/studentGroup/schedule?studentGroup='
        sTemp2 = str(group)
        sTemp3 = sTemp1 + sTemp2
        r = requests.get(sTemp3)
        bsche = r.json()
        bschedule = bsche["tomorrowSchedules"]
        if not bschedule:
            bot.send_message(m.chat.id, 'Завтра нет пар, будь спокоен, старик.',
                             reply_markup=types.ReplyKeyboardRemove())
        else:
            for i in bschedule:
                if i['subject'] != "ФизК" and i['subject'] != "ИКГ":
                    emp = i["employee"][0]
                s += u'\U0001F4D6' + str(i['subject']) + '\n'
                s += u'\U000023F3' + str(i['lessonTime']) + '\n'
                if i['subject'] != "ФизК":
                    s += u'\U0001F3E2' + str(i['auditory'][0]) + '\n'
                    if int(i['numSubgroup']) != 0:
                        s += u'\U0001F38E' + str(i['numSubgroup']) + ' подгруппа ' + '\n'
                if i['subject'] != "ФизК" and i['subject'] != "ИКГ":
                    s += u'\U0001F47D' + str(emp['lastName']) + ' ' + str(emp['firstName']) + ' ' + str(
                        emp['middleName']) + '\n\n'
        bot.send_message(m.chat.id, s, reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(m.chat.id, 'Возвращаемся в главное меню', reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['math'])
def getTicket(message):
    try:
        bot.send_message(message.chat.id, 'Некоторых билетов нет. Будьте внимательны и осторожны')
        msg = bot.send_message(message.chat.id, 'Привет. Какой билет тебе нужен?')
        bot.register_next_step_handler(msg, sendTicket)
    except:
        bot.send_message(message.chat.id, 'Ошибка выполнения.')


def sendTicket(m):
    try:
        k = int(m.text)
        if k > 72 or k < 1:
            bot.send_message(m, 'Такого билета не существует')
        else:
            s = m.text + '.pdf'
            for file in os.listdir('tickets/'):
                if file == s:
                    f = open('tickets/' + file, 'rb')
                    bot.send_document(m.chat.id, f, None)
    except:
        bot.send_message(m.chat.id, 'Ошибка выполнения.')


@bot.message_handler(commands=['schedule'])
def checkRasp(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=1)
    markup.add(*[types.KeyboardButton(name) for name in ['Академическая (в сторону Ангарской)', 'Кольцевая дорога',
                                                         'Профтехколледж',
                                                         'Дом печати (в сторону ст.м. Пушкинская)']])
    msg = bot.send_message(message.chat.id, 'Какая остановка тебе нужна?',
                           reply_markup=markup)
    bot.register_next_step_handler(msg, name1)


def name1(message):
    if message.text != 'Академическая (в сторону Ангарской)' and message.text != 'Кольцевая дорога' and \
                    message.text != 'Профтехколледж' and message.text != 'Дом печати (в сторону ст.м. Пушкинская)':
        bot.send_message(message.chat.id, 'Ебать ты долбаеб, я не могу. Название нормально введи блять.',
                         reply_markup=types.ReplyKeyboardRemove())
        return
    else:
        now = datetime.now()
        hours = int(now.hour) + 3
        minutes = int(now.minute)
        time = hours * 100 + minutes
        day = datetime.today().isoweekday()
        if time > 2400:
            time = time - 2400
        rasp1b = (20, 38, 606, 618, 628, 638, 650, 701, 712, 721, 732, 743, 752, 800,
                  808, 818, 828, 837, 846, 856, 908, 919, 930, 940, 952, 1008, 1022, 1037, 1051, 1107, 1122, 1135, 1146,
                  1200, 1215, 1228, 1243, 1258, 1313, 1326, 1340, 1355, 1411, 1425, 1440, 1455, 1509, 1519, 1530, 1541,
                  1552, 1603, 1614, 1626, 1636, 1646, 1657, 1707, 1716, 1727, 1739, 1750, 1801, 1810, 1821, 1833, 1845,
                  1859, 1914, 1932, 1952, 2011, 2031, 2051, 2111, 2131, 2151, 2212, 2232, 2252, 2314, 2336, 2358)
        rasp1v = (7, 25, 606, 629, 650, 712, 726, 740, 754, 808, 822, 836, 850, 903, 916, 929, 943, 1000, 1017, 1034,
                  1052, 1109, 127, 1145, 1203, 1220, 1237, 1254, 1311, 1328, 1344, 1400, 1416, 1433, 1450, 1506, 1523,
                  1538, 1555, 1611, 1627, 1643, 1659, 1715, 1731, 1747, 1803, 1820, 1837, 1857, 1919, 1941, 2002, 2024,
                  2044, 2106, 2126, 2146, 2207, 2226, 2246, 2306, 2327, 2347)
        rasp2b = (4, 529, 541, 551, 601, 613, 624, 634, 643, 653, 704, 712, 720, 728, 738, 748, 757, 806, 816, 828, 839,
                  850, 900, 913, 929, 943, 958, 1012, 1028, 1043, 1056, 1107, 1121, 1136, 1149, 1204, 1219, 1234, 1247,
                  1301, 1316, 1332, 1346, 1401, 1416, 1430, 1440, 1451, 1502, 1513, 1524, 1535, 1547, 1557, 1607, 1618,
                  1628, 1637, 1648, 1700, 1711, 1722, 1732, 1742, 1754, 1806, 1821, 1836, 1854, 1914, 1935, 1955, 2015,
                  2035, 2055, 2115, 2136, 2157, 2217, 2239, 2301, 2323, 2345)
        rasp2v = (531, 554, 615, 637, 650, 704, 718, 732, 746, 800, 814, 827, 840, 853, 907, 924, 941, 958, 1016, 1033,
                  1051, 1109, 1127, 1144, 1201, 1218, 1235, 1252, 1308, 1324, 1340, 1357, 1414, 1430, 1447, 1502, 1519,
                  1535, 1551, 1607, 1623, 1639, 1655, 1711, 1727, 1744, 1801, 1821, 1843, 1905, 1926, 1948, 2008, 2030,
                  2050, 2110, 2131, 2151, 2211, 2231, 2252, 2312, 2332, 2352)
        rasp3b = (0, 19, 545, 557, 607, 617, 629, 640, 750, 659, 709, 720, 729, 737, 745, 755, 805, 814, 823, 833, 845,
                  856, 907, 917, 929, 945, 959, 1014, 1028, 1044, 1059, 1112, 1123, 1137, 1152, 1205, 1220, 1235, 1250,
                  1303, 1317, 1332, 1348, 1402, 1417, 1432, 1446, 1456, 1507, 1518, 1529, 1540, 1551, 1603, 1613, 1623,
                  1634, 1644, 1653, 1704, 1716, 1727, 1738, 1748, 1758, 1810, 1822, 1837, 1852, 1910, 1930, 1951, 2010,
                  2030, 2050, 2110, 2130, 2151, 2212, 2232, 2254, 2316, 2337)
        rasp3v = (7, 546, 609, 630, 652, 705, 719, 733, 747, 801, 815, 829, 842, 855, 908, 922, 939, 956, 1013, 1031,
                  1048, 1106, 1124, 1142, 1159, 1216, 1233, 1250, 1307, 1323, 1339, 1355, 1412, 1429, 1445, 1502, 1517,
                  1534, 1550, 1606, 1622, 1638, 1654, 1710, 1726, 1742, 1759, 1816, 1836, 1858, 1920, 1941, 2003, 2023,
                  2045, 2105, 2125, 2146, 2206, 2226, 2246, 2307, 2327, 2347)
        rasp4b = (0, 21, 551, 600, 609, 618, 626, 632, 638, 644, 652, 700, 707, 714, 720, 725, 729, 734, 739, 743, 747,
                  752, 757, 801, 806, 810, 815, 820, 825, 830, 835, 840, 845, 850, 855, 901, 908, 920, 932, 944, 956,
                  1008, 1020, 1033, 1046, 1059, 1112, 1125, 1138, 1151, 1203, 1216, 1228, 1239, 1250, 1301, 1311, 1321,
                  1331, 1342, 1353, 1405, 1417, 1429, 1442, 1455, 1509, 1521, 1532, 1541, 1548, 1555, 1604, 1609, 1614,
                  1619, 1624, 1629, 1634, 1638, 1642, 1647, 1652, 1656, 1701, 1706, 1712, 1717, 1722, 1727, 1732, 1737,
                  1742, 1746, 1751, 1756, 1801, 1806, 1812, 1819, 1825, 1831, 1837, 1844, 1852, 1900, 1909, 1920, 1932,
                  1943, 1955, 2008, 2020, 2032, 2044, 2057, 2110, 2123, 2136, 2149, 2202, 2215, 2228, 2239, 2251, 2304,
                  2318, 2332, 2346)
        rasp4v = (0, 614, 628, 641, 654, 707, 718, 729, 739, 749, 759, 809, 819, 829, 839, 849, 859, 909, 920, 931, 941,
                  952, 1002, 1013, 1024, 1035, 1046, 1057, 1108, 1119, 1130, 1141, 1152, 1203, 1214, 1225, 1235, 1242,
                  1250, 1257, 1305, 1313, 1321, 1329, 1337, 1345, 1353, 1401, 1409, 1417, 1425, 1432, 1441, 1449, 1458,
                  1506, 1515, 1523, 1531, 1539, 1547, 1555, 1603, 1611, 1619, 1627, 1635, 1643, 1651, 1659, 1707, 1715,
                  1723, 1731, 1739, 1747, 1755, 1803, 1811, 1820, 1829, 1839, 1849, 1859, 1909, 1920, 1931, 1942, 1953,
                  2005, 2017, 2028, 2040, 2052, 2105, 2118, 2131, 2144, 2157, 2210, 2220, 2234, 2246, 2258, 2314, 2330,
                  2344,)
        if message.text == 'Академическая (в сторону Ангарской)':
            if day < 6:
                rasp = rasp1b
            else:
                rasp = rasp1v
            counter = 0
            for i in rasp:
                if i > time:
                    if time > 100:
                        bot.send_message(message.chat.id, u'\U0001F689' + ' Ближайший автобус будет на остановке в  ' +
                                         str(rasp[counter])[0:-2] + ':' + str(rasp[counter])[-2:] + '\n' +
                                         u'\U0001F68C' + ' Следующий приедет в ' + str(rasp[counter + 1])[0:-2] + ':' +
                                         str(rasp[counter + 1])[-2:], reply_markup=types.ReplyKeyboardRemove())
                        break
                    else:
                        if counter >= 2:
                            bot.send_message(message.chat.id,
                                             u'\U0001F689' + ' Ближайший автобус будет на остановке в  ' +
                                             str(rasp[counter])[0:-2] + ':' + str(rasp[counter])[-2:] + '\n' +
                                             u'\U0001F68C' + ' Следующий приедет в ' + str(rasp[counter + 1])[
                                                                                       0:-2] + ':' +
                                             str(rasp[counter + 1])[-2:], reply_markup=types.ReplyKeyboardRemove())
                        else:
                            bot.send_message(message.chat.id, u'\U0001F689' + 'Ближайший автобус будет на остановке в '
                                                                              '00: '
                                             + str(rasp[counter])[-2:] + '\n' +
                                             u'\U0001F68C' + ' Следующий приедет в ' + str(rasp[counter + 1])[0:-2]
                                             + ':' +
                                             str(rasp[counter + 1])[-2:], reply_markup=types.ReplyKeyboardRemove())
                        break
                counter += 1
        elif message.text == 'Кольцевая дорога':
            if day < 6:
                rasp = rasp2b
            else:
                rasp = rasp2v
            counter = 0
            for i in rasp:
                if i > time:
                    if time > 100:
                        bot.send_message(message.chat.id, u'\U0001F689' + ' Ближайший автобус будет на остановке в  ' +
                                         str(rasp[counter])[0:-2] + ':' + str(rasp[counter])[-2:] + '\n' +
                                         u'\U0001F68C' + ' Следующий приедет в ' + str(rasp[counter + 1])[0:-2] + ':' +
                                         str(rasp[counter + 1])[-2:], reply_markup=types.ReplyKeyboardRemove())
                        break
                    else:
                        if day < 6:
                            if counter >= 1:
                                bot.send_message(message.chat.id,
                                                 u'\U0001F689' + ' Ближайший автобус будет на остановке в  ' +
                                                 str(rasp[counter])[0:-2] + ':' + str(rasp[counter])[-2:] + '\n' +
                                                 u'\U0001F68C' + ' Следующий приедет в ' + str(rasp[counter + 1])[
                                                                                           0:-2] + ':' +
                                                 str(rasp[counter + 1])[-2:], reply_markup=types.ReplyKeyboardRemove())
                            else:
                                bot.send_message(message.chat.id,
                                                 u'\U0001F689' + 'Ближайший автобус будет на остановке в '
                                                                 '00: '
                                                 + str(rasp[counter])[-2:] + '\n' +
                                                 u'\U0001F68C' + ' Следующий приедет в ' + str(rasp[counter + 1])[0:-2]
                                                 + ':' +
                                                 str(rasp[counter + 1])[-2:], reply_markup=types.ReplyKeyboardRemove())
                            break
                        else:
                            bot.send_message(message.chat.id,
                                             u'\U0001F689' + ' Ближайший автобус будет на остановке в  ' +
                                             str(rasp[counter])[0:-2] + ':' + str(rasp[counter])[-2:] + '\n' +
                                             u'\U0001F68C' + ' Следующий приедет в ' + str(rasp[counter + 1])[
                                                                                       0:-2] + ':' +
                                             str(rasp[counter + 1])[-2:], reply_markup=types.ReplyKeyboardRemove())
                            break

                counter += 1
        elif message.text == 'Профтехколледж':
            if day < 6:
                rasp = rasp3b
            else:
                rasp = rasp3v
            counter = 0
            for i in rasp:
                if i > time:
                    if time > 100:
                        bot.send_message(message.chat.id, u'\U0001F689' + ' Ближайший автобус будет на остановке в  ' +
                                         str(rasp[counter])[0:-2] + ':' + str(rasp[counter])[-2:] + '\n' +
                                         u'\U0001F68C' + ' Следующий приедет в ' + str(rasp[counter + 1])[0:-2] + ':' +
                                         str(rasp[counter + 1])[-2:], reply_markup=types.ReplyKeyboardRemove())
                        break
                    else:
                        if day < 6:
                            if counter >= 3:
                                bot.send_message(message.chat.id,
                                                 u'\U0001F689' + ' Ближайший автобус будет на остановке в  ' +
                                                 str(rasp[counter])[0:-2] + ':' + str(rasp[counter])[-2:] + '\n' +
                                                 u'\U0001F68C' + ' Следующий приедет в ' + str(rasp[counter + 1])[
                                                                                           0:-2] + ':' +
                                                 str(rasp[counter + 1])[-2:], reply_markup=types.ReplyKeyboardRemove())
                            else:
                                bot.send_message(message.chat.id,
                                                 u'\U0001F689' + 'Ближайший автобус будет на остановке в '
                                                                 '00: '
                                                 + str(rasp[counter])[-2:] + '\n' +
                                                 u'\U0001F68C' + ' Следующий приедет в ' + str(rasp[counter + 1])[0:-2]
                                                 + ':' +
                                                 str(rasp[counter + 1])[-2:], reply_markup=types.ReplyKeyboardRemove())
                            break
                        else:
                            if counter >= 1:
                                bot.send_message(message.chat.id,
                                                 u'\U0001F689' + ' Ближайший автобус будет на остановке в  ' +
                                                 str(rasp[counter])[0:-2] + ':' + str(rasp[counter])[-2:] + '\n' +
                                                 u'\U0001F68C' + ' Следующий приедет в ' + str(rasp[counter + 1])[
                                                                                           0:-2] + ':' +
                                                 str(rasp[counter + 1])[-2:], reply_markup=types.ReplyKeyboardRemove())
                            else:
                                bot.send_message(message.chat.id,
                                                 u'\U0001F689' + 'Ближайший автобус будет на остановке в '
                                                                 '00: '
                                                 + str(rasp[counter])[-2:] + '\n' +
                                                 u'\U0001F68C' + ' Следующий приедет в ' + str(rasp[counter + 1])[0:-2]
                                                 + ':' +
                                                 str(rasp[counter + 1])[-2:], reply_markup=types.ReplyKeyboardRemove())
                            break
                counter += 1
        elif message.text == 'Дом печати (в сторону ст.м. Пушкинская)':
            if day < 6:
                rasp = rasp4b
            else:
                rasp = rasp4v
            counter = 0
            for i in rasp:
                if i > time:
                    if time > 100:
                        bot.send_message(message.chat.id, u'\U0001F689' + ' Ближайший автобус будет на остановке в  ' +
                                         str(rasp[counter])[0:-2] + ':' + str(rasp[counter])[-2:] + '\n' +
                                         u'\U0001F68C' + ' Следующий приедет в ' + str(rasp[counter + 1])[0:-2] + ':' +
                                         str(rasp[counter + 1])[-2:], reply_markup=types.ReplyKeyboardRemove())
                        break
                    else:
                        if day < 6:
                            if counter >= 3:
                                bot.send_message(message.chat.id,
                                                 u'\U0001F689' + ' Ближайший автобус будет на остановке в  ' +
                                                 str(rasp[counter])[0:-2] + ':' + str(rasp[counter])[-2:] + '\n' +
                                                 u'\U0001F68C' + ' Следующий приедет в ' + str(rasp[counter + 1])[
                                                                                           0:-2] + ':' +
                                                 str(rasp[counter + 1])[-2:], reply_markup=types.ReplyKeyboardRemove())
                            else:
                                bot.send_message(message.chat.id,
                                                 u'\U0001F689' + 'Ближайший автобус будет на остановке в '
                                                                 '00: '
                                                 + str(rasp[counter])[-2:] + '\n' +
                                                 u'\U0001F68C' + ' Следующий приедет в ' + str(rasp[counter + 1])[0:-2]
                                                 + ':' +
                                                 str(rasp[counter + 1])[-2:], reply_markup=types.ReplyKeyboardRemove())
                            break
                        else:
                            if counter >= 1:
                                bot.send_message(message.chat.id,
                                                 u'\U0001F689' + ' Ближайший автобус будет на остановке в  ' +
                                                 str(rasp[counter])[0:-2] + ':' + str(rasp[counter])[-2:] + '\n' +
                                                 u'\U0001F68C' + ' Следующий приедет в ' + str(rasp[counter + 1])[
                                                                                           0:-2] + ':' +
                                                 str(rasp[counter + 1])[-2:], reply_markup=types.ReplyKeyboardRemove())
                            else:
                                bot.send_message(message.chat.id,
                                                 u'\U0001F689' + 'Ближайший автобус будет на остановке в '
                                                                 '00: '
                                                 + str(rasp[counter])[-2:] + '\n' +
                                                 u'\U0001F68C' + ' Следующий приедет в ' + str(rasp[counter + 1])[0:-2]
                                                 + ':' +
                                                 str(rasp[counter + 1])[-2:], reply_markup=types.ReplyKeyboardRemove())
                            break
                counter += 1


@bot.message_handler(commands=['weather'])
def CheckWeather(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    button_exit = types.KeyboardButton(text="Вернуться в меню")
    keyboard.add(button_geo, button_exit)
    msg = bot.send_message(message.chat.id,
                           'Пришли свою геолокацию, сынок...',
                           reply_markup=keyboard)
    bot.register_next_step_handler(msg, getLocation)


def getLocation(m):
    if m.text == "Вернуться в меню":
        bot.send_message(m.chat.id, 'Возвращаемся в главное меню...', reply_markup=types.ReplyKeyboardRemove())
        return
    elif m.location:
        la = m.location.latitude
        lo = m.location.longitude
        owm = pyowm.OWM('336934fc0905e176cd4e10f04521a283', language='ru')
        # observation = owm.weather_at_place('Minsk')
        observation = owm.weather_at_coords(la, lo)
        w = observation.get_weather()
        temp_dictionary = w.get_temperature('celsius')
        temp_rain = w.get_rain()
        s = ''
        if not temp_rain:
            s = 'нет'
        else:
            for i, key in temp_rain.items():
                s += i
                s += key
        temp_snow = w.get_snow()
        s1 = ''
        if not temp_snow:
            s1 = 'нет'
        else:
            for i, key in temp_snow.items():
                s1 += i
                s1 += key

        bot.send_message(m.chat.id, u'\U0000231A' + ' Сегодня, ' + w.get_reference_time(timeformat='iso')[:10] +
                         '\n Краткая сводка : ' +
                         str(w.get_detailed_status()) + '\n\n' + u'\U0001F525' + ' Температура: ' +
                         str(int(temp_dictionary['temp'])) + '\n\n' u'\U00002601' + ' Облачность составляет ' +
                         str(w.get_clouds()) + ' %\n\n' + u'\U0001F305' + ' Время восхода: ' +
                         str(int(w.get_sunrise_time('iso')[11:13]) + 3) + ':' +
                         str(w.get_sunrise_time('iso')[14:16]) + '\n' + u'\U0001F304' + ' Время заката: ' +
                         str(int(w.get_sunset_time('iso')[11:13]) + 3) + ':' +
                         str(w.get_sunrise_time('iso')[14:16]), reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(m.chat.id, 'Опять ты за своё. Там было всего две кнопки и ты даже с ними не смог справиться',
                         reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['exchange'])
def CheckRates(message):
    resUSD = requests.get("http://www.nbrb.by/API/ExRates/Rates/USD?ParamMode=2")
    resEUR = requests.get("http://www.nbrb.by/API/ExRates/Rates/EUR?ParamMode=2")
    resRUB = requests.get("http://www.nbrb.by/API/ExRates/Rates/RUBS?ParamMode=2")
    resBit = requests.get("https://blockchain.info/ru/ticker")
    resEth = requests.get("https://api.coinmarketcap.com/v1/ticker/")
    dataUSD = resUSD.json()
    dataEUR = resEUR.json()
    dataRUB = resRUB.json()
    dataBit = resBit.json()
    dataEth = resEth.json()

    bot.send_message(message.chat.id, u'\U0001F4B5' + ' Курс доллара на сегодня - ' + str(dataUSD['Cur_OfficialRate']) +
                     '\n' + u'\U0001F4B6' + ' Курс евро на сегодня - ' + str(dataEUR['Cur_OfficialRate']) +
                     '\n' + u'\U0001F4B8' + ' Курс российского рубля на сегодня - ' + str(dataRUB['Cur_OfficialRate']) +
                     '\n\n' + u'\U0001F680' + 'Курс биткоина на сегодня - ' + str((dataBit['USD'])['sell']) + '\n' +
                     u'\U0001F4A0' + 'Курс эфира на сегодня - ' + str((dataEth[1])['price_usd']))
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*[types.InlineKeyboardButton(text=name, callback_data=name) for name in ['BYR -> USD', 'BYR -> EUR',
                                                                                          'USD -> BYR', 'EUR -> BYR',
                                                                                          'вернуться в меню']])
    msg = bot.send_message(message.chat.id, 'Что вас интересует? ', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda c: True)
def inline(c):
    if c.data == 'BYR -> USD':
        msg = bot.edit_message_text(chat_id=c.message.chat.id, message_id=c.message.message_id,
                                    text='Введите сумму в BYR:',
                                    parse_mode='Markdown')
        # msg = bot.send_message(c.message.chat.id, 'Какую сумму вы хотите перевести в USD?')
        bot.register_next_step_handler(msg, ex1)
    elif c.data == 'BYR -> EUR':
        msg = bot.edit_message_text(chat_id=c.message.chat.id, message_id=c.message.message_id,
                                    text='Введите сумму в BYR:',
                                    parse_mode='Markdown')
        bot.register_next_step_handler(msg, ex2)
    elif c.data == 'USD -> BYR':
        msg = bot.edit_message_text(chat_id=c.message.chat.id, message_id=c.message.message_id,
                                    text='Введите сумму в USD:',
                                    parse_mode='Markdown')
        bot.register_next_step_handler(msg, ex3)
    elif c.data == 'EUR -> BYR':
        msg = bot.edit_message_text(chat_id=c.message.chat.id, message_id=c.message.message_id,
                                    text='Введите сумму в EUR:',
                                    parse_mode='Markdown')
        bot.register_next_step_handler(msg, ex3)
    elif c.data == 'вернуться в меню':
        msg = bot.edit_message_text(chat_id=c.message.chat.id, message_id=c.message.message_id,
                                    text='возвращаемся назад...',
                                    parse_mode='Markdown')


def ex1(m1):
    resUSD = requests.get("http://www.nbrb.by/API/ExRates/Rates/USD?ParamMode=2")
    dataUSD = resUSD.json()
    m = int(m1.text)
    k = dataUSD['Cur_OfficialRate']
    bot.send_message(m1.chat.id, 'Эквивалентная сумма в USD будет составлять ' + str(round(m / k, 3)))


def ex2(m1):
    resEUR = requests.get("http://www.nbrb.by/API/ExRates/Rates/EUR?ParamMode=2")
    dataEUR = resEUR.json()
    m = int(m1.text)
    k = dataEUR['Cur_OfficialRate']
    bot.send_message(m1.chat.id, 'Эквивалентная сумма в EUR будет составлять ' + str(round(m / k, 3)))


def ex3(m1):
    resUSD = requests.get("http://www.nbrb.by/API/ExRates/Rates/USD?ParamMode=2")
    dataUSD = resUSD.json()
    m = int(m1.text)
    k = dataUSD['Cur_OfficialRate']
    bot.send_message(m1.chat.id, 'Эквивалентная сумма в BYR будет составлять ' + str(round(m * k, 3)))


def ex4(m1):
    resEUR = requests.get("http://www.nbrb.by/API/ExRates/Rates/EUR?ParamMode=2")
    dataEUR = resEUR.json()
    m = int(m1.text)
    k = dataEUR['Cur_OfficialRate']
    bot.send_message(m1.chat.id, 'Эквивалентная сумма в BYR будет составлять ' + str(round(m * k, 3)))


@bot.message_handler(content_types=["sticker"])
def GoAway(message):
    bot.send_message(message.chat.id, 'Ну и зачем ты мне свои стикеры отправляешь, гений?')


@bot.message_handler(content_types=["audio"])
def AwayAudio(message):
    bot.send_message(message.chat.id, 'Я не айпод. Отстань.')


@bot.message_handler(content_types=["document"])
def AwayDocument(message):
    bot.send_message(message.chat.id, 'Бот != офисный центр. Отстань.')


@bot.message_handler(content_types=["video"])
def AwayVideo(message):
    bot.send_message(message.chat.id, 'О, видос. Ну-ка.')


@bot.message_handler(content_types=["voice"])
def AwayVoice(message):
    bot.send_message(message.chat.id, 'Какой же у тебя противный голос. Уаааааа.')


@bot.message_handler(content_types=["location"])
def AwayLocation(message):
    bot.send_message(message.chat.id, 'Запускаю ракету.')


@bot.message_handler(func=lambda msg: msg.text == 'бот, ты классный' or msg.text == 'Бот, ты классный')
def coolBot(message):
    for file in os.listdir('pics/'):
        if file == 'ilya.jpg':
            if file.split('.')[-1] == 'jpg':
                bot.send_photo(message.chat.id, "AgADAgADVKgxG0hVkEhOXCI3aqZZwdjMDw4ABCGW1Ul_D23dJBQDAAEC", None,
                               caption='Кчау!')


@bot.message_handler(func=lambda msg: msg.text == 'бот, ты не классный' or msg.text == 'Бот, ты не классный')
def NoCoolBot(message):
    for file in os.listdir('pics/'):
        if file == 'serega_evil.jpg':
            bot.send_photo(message.chat.id, "AgADAgADWqgxG0hVkEh--aRmsJVMlX3PDw4ABA7xVjUWQnZY9BYDAAEC", None)
    bot.send_message(message.chat.id, 'Are you ohuel tam?')

@bot.message_handler(
    func=lambda msg: msg.text == 'бот, где можно провести каникулы?' or msg.text == 'Бот, где можно провести каникулы?')
def noCoolBot(message):
    bot.send_message(message.chat.id, 'Таким как ты только здесь.')
    bot.send_location(message.chat.id, 45.222128, 34.878809)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    bot.send_message(message.chat.id, 'Пиши разборчивее, молодой. Не ясно же ничерта.')


@server.route("/bot", methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])

    return "!", 200


@server.route("/")
def WebHook():
    bot.remove_webhook()

    bot.set_webhook(url="https://sad-snitch-bot.herokuapp.com/bot")

    return "bot started", 200


server.run(host="0.0.0.0", port=os.environ.get('PORT', 5000))

server = Flask(__name__)

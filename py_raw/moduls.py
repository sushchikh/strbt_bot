import yaml
import logging.config
import os
import pandas as pd
import telebot
import datetime
from datetime import datetime
import requests
from datetime import timedelta
from fuzzywuzzy import fuzz
import math
from time import sleep


########     ###    ########    ###
##     ##   ## ##      ##      ## ##
##     ##  ##   ##     ##     ##   ##
##     ## ##     ##    ##    ##     ##
##     ## #########    ##    #########
##     ## ##     ##    ##    ##     ##
########  ##     ##    ##    ##     ##


# --------------------------------------------------------------------------------------------
# созадет и возвращает логгер для логирования в файл
def get_logger():
    """return logger_object with parametrs from config.yaml"""
    with open('/home/sushchikh/strbt_bot/py_raw/config.yaml', 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    logger = logging.getLogger(__name__)
    return logger


# --------------------------------------------------------------------------------------------
#  определяет сегодняшнюю дату, скачивает дата-файл с сервака, кладет его в папку с данными
def data_downloader(logger):
    today = datetime.today()
    # print(today.strftime("%Y%m%d"))
    path_to_data_file_on_server = ('http://stroybatinfo.ru//import_1c/for_bot/' +
                                   str(today.strftime("%Y%m%d")) + '.csv')
    # print(path_to_data_file_on_server)
    try:
        data_file = requests.get(path_to_data_file_on_server, allow_redirects=True)
        name_of_saving_file = '/home/sushchikh/strbt_bot/data/' + str(today.strftime("%Y%m%d") + '.csv')
        with open(name_of_saving_file, 'wb') as file:
            file.write(data_file.content)
    except Exception as e:
        error_message = 'moduls/data_downloader - ' + str(e)
        logger.error(error_message)
    print('data download welldone')

# --------------------------------------------------------------------------------------------
# определяет какой из файлов в папке свежий, возвращает имя новейшего xls-файла
def get_name_of_newest_data_file(logger):
    """filter full_list of files by end ".csv", sorted by time of change and take last one:"""
    try:
        path_to_data_dir = '/home/sushchikh/strbt_bot/data'
        file_list = os.listdir(path_to_data_dir)
        full_list = [os.path.join(path_to_data_dir, i) for i in file_list]  # get full list of all files in dir
        newest_file_name = sorted(filter(lambda x: x.endswith('.csv'), full_list), key=os.path.getmtime)[-1]
        time_of_data_file = datetime.fromtimestamp(os.path.getmtime(newest_file_name)).strftime('%Y-%m-%d %H:%M:%S')
        print('время последнего файла:', time_of_data_file)
        return newest_file_name, time_of_data_file
    except FileNotFoundError as e:
        error_message = 'moduls/get_name_of_newest_data_file - ' + str(e)
        logger.error(error_message)


# --------------------------------------------------------------------------------------------
# берет свежайщий файл, считывает его в датафрейм пандасовский
def get_strbt_dataframe_from_xls_file(logger, newest_file_name):
    """read xls-file, return dataframe"""

    try:
        strbt_dataframe = pd.read_csv(newest_file_name, index_col='Код', delimiter=';', encoding='windows-1251',
                                      error_bad_lines=True)
        print('data read well done')
        return strbt_dataframe
    except ValueError as e:
        error_message = ('moduls/get_strbt_dataframe_from_xls_file - ' + str(e) +
                         ' no argument with file name, look get_name_of_newest_data_file function')
        logger.error(error_message)
    except FileNotFoundError as e:
        error_message = 'moduls/get_strbt_dataframe_from_xls_file - ' + str(e)
        logger.error(error_message)


# --------------------------------------------------------------------------------------------
#
def get_item_from_dataframe(logger, dataframe, message):
    """
    search message in dataframe, if find - return it to output_message
    """
    try:
        message = int(message)

        # item_name = dataframe.loc[[message], ['Номенклатура']].values[0][0].split(', ')
        # formated_item_name = ''
        # for i in item_name:
        #     if i == item_name[0]:
        #         formated_item_name = '*' + formated_item_name + str(i) + '*' + '\n'
        #     else:
        #         formated_item_name = formated_item_name + str(i) + '\n'

        # test ------------
        formated_item_name = dataframe.loc[[message], ['Номенклатура']].values[0][0] + '\n'
        formated_item_name = formated_item_name.replace('*', 'x')
        # test ------------


        item_measure = dataframe.loc[[message], ['Ед.изм.']].values[0][0]
        if item_measure == 'шт':
            item_pugach_value = int(dataframe.loc[[message], ['Количество Основной склад']].values[0][0])
            item_dzerj_value = int(dataframe.loc[[message], ['Количество База Дзержинского']].values[0][0])
            item_chepetsk_value = int(dataframe.loc[[message], ['Количество Чепецк']].values[0][0])
            item_siktivkar_value = int(dataframe.loc[[message], ['Количество Сыктывкар']].values[0][0])
        else:
            item_pugach_value = str(dataframe.loc[[message], ['Количество Основной склад']].values[0][0])
            item_dzerj_value = str(dataframe.loc[[message], ['Количество База Дзержинского']].values[0][0])
            item_chepetsk_value = str(dataframe.loc[[message], ['Количество Чепецк']].values[0][0])
            item_siktivkar_value = str(dataframe.loc[[message], ['Количество Сыктывкар']].values[0][0])

        item_reserve = dataframe.loc[[message], ['Резерв']].values[0][0]
        if not(str(item_reserve).isdigit()):
            item_reserve = 0

        item_price_prepayment = str(dataframe.loc[[message], ['ОптПредоплата']].values[0][0])
        item_price_retail = str(dataframe.loc[[message], ['Розница']].values[0][0])
        item_price_club = str(dataframe.loc[[message], ['Клубная']].values[0][0])
        item_price_otsrochka_2 = str(dataframe.loc[[message], ['ОптОтсрочка2']].values[0][0])
        item_price_otsrochka_1 = str(dataframe.loc[[message], ['ОптОтсрочка1']].values[0][0])
        item_bonus = (str(dataframe.loc[[message], ['Бонус']].values[0][0]))

        item_dostavka_siktivkar = str(dataframe.loc[[message], ['Доставка Сыктывкар']].values[0][0])
        if item_dostavka_siktivkar == 'nan' or item_dostavka_siktivkar == '0':
            item_dostavka_siktivkar_message = ''
        else:
            item_dostavka_siktivkar_message = f'\nдоставка до Сыктывкара:  {item_dostavka_siktivkar} р.'

        item_price_akciya_siktivkar = str(dataframe.loc[[message], ['ЦенаАкцияСыктывкар']].values[0][0])
        if item_price_akciya_siktivkar == 'nan' or item_price_akciya_siktivkar == '0':
            item_price_akciya_siktivkar_message = ''
        else:
            item_price_akciya_siktivkar_message = f'\nцена акция-Сыктывкар:  *{item_price_akciya_siktivkar}* р.'

        item_price_instrument = str(dataframe.loc[[message], ['Инструмент']].values[0][0])
        if item_price_instrument == 'nan' or item_price_instrument == '0':
            item_price_instrument_message = ''
        else:
            item_price_instrument_message = f'\nцена в Инструменте:  {item_price_instrument} р.'

        item_price_akciya = str(dataframe.loc[[message], ['ЦенаАкция']].values[0][0])
        if item_price_akciya == 'nan' or item_price_akciya == '0':
            item_price_akciya_message = ''
        else:
            item_price_akciya_message = f'\nцена-акция:  *{item_price_akciya}* p.'

        output_message = f"""    {formated_item_name}
*ОСТАТКИ:*
Пугачева:  {item_pugach_value} {item_measure}
Дзержинскго:  {item_dzerj_value} {item_measure}
Чепецк:  {item_chepetsk_value} {item_measure}
Сыктывкар:  {item_siktivkar_value} {item_measure}

резерв:  {item_reserve} {item_measure}

*ЦЕНЫ:*
розница:  *{item_price_retail}* р.
клубная:  *{item_price_club}* р.
опт-отстрочка-1:  *{item_price_otsrochka_1}* р.
предоплата:  *{item_price_prepayment}* .р {item_price_akciya_siktivkar_message}{item_price_akciya_message}

бонус:  {item_bonus}{item_dostavka_siktivkar_message}{item_price_instrument_message}"""
        # print(output_message)
        wrong_user_request = -1  # magic numbers =)
        is_item_exist = True
    except ValueError:
        output_message = 'Это не код товара, попробуй снова'
        wrong_user_request = message
        is_item_exist = False
    except KeyError:
        output_message = """Я не знаю такого кода товара.
Если ты уверен, что все правильно — напиши мне "да" и я сообщу об этом разработчику 😉"""
        wrong_user_request = message
        is_item_exist = False
    return output_message, wrong_user_request, is_item_exist


# --------------------------------------------------------------------------------------------
# обращаемся к функции, если сообщение не строго числовое, пытаемся найти его в названии товаров
def find_item_func(logger, message, dataframe):
    """
    split message by whitespace, check matches in all items_names
    """

    # list_of_words_from_user_message = message.strip().lower().split(' ')
    # # print(strbt_dataframe)
    # print('поисковое пользовательское сообщене:', *list_of_words_from_user_message)
    # # print(strbt_dataframe.iloc[1]['Номенклатура'])
    # count_of_matches = 0
    # pos_of_match_item = []
    # list_of_few_items_names = []
    # for i in range(len(dataframe)):
    #
    #     list_of_words_from_dataframe_item = str(dataframe.iloc[i]['Номенклатура']).replace('"', '').replace('(','').replace(')', '').strip().lower().split(' ')
    #
    #     # print(*list_of_words_from_dataframe_item)
    #     check = all(item in list_of_words_from_dataframe_item for item in list_of_words_from_user_message)
    #     if check:
    #         count_of_matches += 1
    #         pos_of_match_item.append(dataframe.iloc[i])
    #         list_of_few_items_names.append(str(
    #             '*' +
    #             str(dataframe.index.values[i]) +
    #             '*' + ' - ' +
    #             str(dataframe.iloc[i]['Номенклатура']).replace('"', '').replace('(', '').replace(')', '').strip()))
    # # if count_of_matches == 1:
    # #     output_message = ('Нашел одно совпадение:\n' +
    # #                       str(pos_of_match_item[0]) + ' - ')
    #     if count_of_matches > 11:
    #         break
    #
    # if count_of_matches == 0:
    #     output_message = 'не нашел ни одного совпадения, либо что-то пошло не так 😖'
    # elif count_of_matches > 10:
    #     output_message = "слишком много совпадений, попробуй уточнить запрос"
    # elif 1 <= count_of_matches <= 10:  # если совпадения есть
    #     # print(f'*нашел {count_of_matches} совпадений:*\n\n')
    #     output_message = f'*нашел {count_of_matches} совпадений:*\n\n'
    #     for i in list_of_few_items_names:
    #         output_message += (str(i) + '\n')
    # else:
    #     output_message = 'опа-опа'

    output_message = ''

    def get_sample(sample, string):
        return fuzz.token_set_ratio(sample, string)

    output_df = dataframe[dataframe['Номенклатура'].apply(get_sample, args=[message]) > 95]
    if len(output_df) == 0:
        output_message = 'не нашел ни одного совпадения, либо что-то пошло не так 😖'
    elif len(output_df) > 15:
        output_message = 'слишком много совпадений, попробуй уточнить запрос'
    else:
        output_message = f'*нашел {len(output_df)} совпадений:*\n\n'
        for i in output_df.index:
            output_message += '*' + str(i) + '* ' + str(output_df.loc[[i], ['Номенклатура']].values[0][0]).replace('*', 'x') + '\n' + '\n'
            # print(i, output_df.loc[[i], ['Номенклатура']].values[0][0])

    return output_message


   ###    ########  ########  #### ######## #### ##     ## ########  ######
  ## ##   ##     ## ##     ##  ##     ##     ##  ##     ## ##       ##    ##
 ##   ##  ##     ## ##     ##  ##     ##     ##  ##     ## ##       ##
##     ## ##     ## ##     ##  ##     ##     ##  ##     ## ######    ######
######### ##     ## ##     ##  ##     ##     ##   ##   ##  ##             ##
##     ## ##     ## ##     ##  ##     ##     ##    ## ##   ##       ##    ##
##     ## ########  ########  ####    ##    ####    ###    ########  ######

# --------------------------------------------------------------------------------------------
# получает сообщение пользователя, добавляет его в файл с указанием точного времени
def save_user_message(user_message):
    """
    Get user message, push it into file with current date and time
    """
    now_date_time_on_server = datetime.now() + timedelta(hours=3)
    formated_date_time = now_date_time_on_server.strftime('%d.%m.%y, %H:%M:%S') + ' - '
    # print(now_date_time)
    output_line = '\n' + formated_date_time + user_message
    with open('/home/sushchikh/strbt_bot/logs/users_message.txt', 'a') as f:
        f.write(output_line)

def save_stange_user_requests(user_request):
    """
    Get user message, push it into file with current date and time
    """
    now_date_time_on_server = datetime.now() + timedelta(hours=3)
    formated_date_time = now_date_time_on_server.strftime('%d.%m.%y, %H:%M:%S') + ' - '
    # print(now_date_time)
    output_line = '\n' + formated_date_time + str(user_request)
    with open('/home/sushchikh/strbt_bot/logs/users_strange_requests.txt', 'a') as f:
        f.write(output_line)


# --------------------------------------------------------------------------------------------
# проверяет является ли сообщение числовым, возвращает тру или фолсе
def is_message_digit(message):
    try:
        int(message)  # i know about isdigit() func
        # print('сообщение пользователя цифровое')
        return True
    except ValueError:
        return False


# --------------------------------------------------------------------------------------------
#
def get_picture_of_item(logger, message):
    try:
        url = 'http://stroybatinfo.ru/imgs_for_bot/' + str(int(message)) + '.jpg'
        r = requests.get(url)
        if r.status_code == 404:
            item_img_name = 'К этой позиции я не нашел картинки, прости 😥'
            return False, item_img_name
        open('/home/sushchikh/strbt_bot/img/' + str(message) + '.jpg', 'wb').write(r.content)
        item_img_name = '/home/sushchikh/strbt_bot/img/' + str(message) + '.jpg'
        return True, item_img_name  # if file exist
    except (FileNotFoundError, FileExistsError) as e:
        error_message = 'moduls/get_picture_of_item - ' + str(e)
        logger.error(error_message)
        item_img_name = 'No such image =('
        return False, item_img_name  # if file not exist


# --------------------------------------------------------------------------------------------
#
def get_dict_phones_from_file_by_letter():
    with open('/home/sushchikh/strbt_bot/phones/phones.yaml', 'r') as f:
        dict_of_phone_numbers = yaml.safe_load(f.read())
        # output_message = dict_of_phone_numbers[letter]
        # print(output_message)
    return dict_of_phone_numbers

########   #######  ########
##     ## ##     ##    ##
##     ## ##     ##    ##
########  ##     ##    ##
##     ## ##     ##    ##
##     ## ##     ##    ##
########   #######     ##


def get_bot_token_from_yaml(logger):
    try:
        with open('/home/sushchikh/strbt_bot/py_raw/lpt.yaml', 'r') as f:
            lpt = yaml.safe_load(f.read())
            token = lpt['token']
        return token
    except FileNotFoundError as e:
        error_message = ('moduls/get_token_from_yaml - ' + str(e) + ' no token-file')
        logger.error(error_message)


def bot_runner(logger, token, dataframe, time_of_data_file, dict_of_phones):
    bot = telebot.TeleBot(token)  # create bot
    markdown = """
    *bold text*
    _italic text_
    [text](URL)
    """
    @bot.message_handler(commands=['start'])  # реагируем на надпись сатрт
    def start_message(message):
        bot.send_message(message.chat.id, 'Привет, присылай мне код товара - я расскажу тебе о нем подробнее')

    @bot.message_handler(content_types=['text'])
    def send_text(message):
        user = (str(message.from_user.last_name) + ' ' +
                str(message.from_user.first_name) + ' ' +
                str(message.from_user.username))
        user_message = user + ' - ' + message.text
        save_user_message(user_message)

        # клавиатура:
        keyboard1 = telebot.types.ReplyKeyboardMarkup(True)
        keyboard1.row('Сотовые номера сотрудников', 'Внутренние номера')  #, 'Реквизиты фирм')

        letters = ['А','Б','В','Г','Д','Е','Ж','З','И','К','Л','М','Н','О','П','Р','С','Т','У','Ф','Х','Ч','Ш','Э','Я']

        keyboard2 = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        btn_1 = telebot.types.KeyboardButton('А')
        btn_2 = telebot.types.KeyboardButton('Б')
        btn_3 = telebot.types.KeyboardButton('В')
        btn_4 = telebot.types.KeyboardButton('Г')
        btn_5 = telebot.types.KeyboardButton('Д')
        btn_6 = telebot.types.KeyboardButton('Е')
        btn_7 = telebot.types.KeyboardButton('Ж')
        btn_8 = telebot.types.KeyboardButton('З')
        btn_25 = telebot.types.KeyboardButton('И')
        btn_9 = telebot.types.KeyboardButton('К')
        btn_10 = telebot.types.KeyboardButton('Л')
        btn_11 = telebot.types.KeyboardButton('М')
        btn_12 = telebot.types.KeyboardButton('Н')
        btn_13 = telebot.types.KeyboardButton('О')
        btn_14 = telebot.types.KeyboardButton('П')
        btn_15 = telebot.types.KeyboardButton('Р')
        btn_16 = telebot.types.KeyboardButton('С')
        btn_17 = telebot.types.KeyboardButton('Т')
        btn_18 = telebot.types.KeyboardButton('У')
        btn_19 = telebot.types.KeyboardButton('Ф')
        btn_20 = telebot.types.KeyboardButton('Х')
        btn_21 = telebot.types.KeyboardButton('Ч')
        btn_22 = telebot.types.KeyboardButton('Ш')
        btn_23 = telebot.types.KeyboardButton('Э')
        btn_24 = telebot.types.KeyboardButton('Я')

        btn_return = telebot.types.KeyboardButton('Вернутся в главное меню')

        keyboard2.row(btn_1, btn_2, btn_3, btn_4, btn_5)
        keyboard2.row(btn_6, btn_7, btn_8, btn_9, btn_25)
        keyboard2.row(btn_10, btn_11, btn_12, btn_13, btn_14)
        keyboard2.row(btn_15, btn_16, btn_17, btn_18, btn_19)
        keyboard2.row(btn_20, btn_21, btn_22, btn_23, btn_24)
        keyboard2.row(btn_return)






        # обработчик сообщения пользователя:
        if is_message_digit(message.text):
            # description of item:
            output_message, wrong_user_request, is_item_exist = get_item_from_dataframe(logger, dataframe, message.text)
            print(output_message)
            print(wrong_user_request)
            print(is_item_exist)
            bot.send_message(message.chat.id, output_message, parse_mode="Markdown", reply_markup=keyboard1)
            # download and send photo
            is_image_exist, item_img_name = get_picture_of_item(logger, message.text)
            if is_image_exist and is_item_exist:
                photo = open(item_img_name, 'rb')
                # bot.send_photo(message.chat.id, photo, caption=str(message.text))
                bot.send_document(message.chat.id, photo, caption=str(message.text))
                photo.close()
            elif is_item_exist and not(is_image_exist):
                bot.send_message(message.chat.id, item_img_name)  # if no image send message
            elif not(is_item_exist) and not(is_image_exist):
                print('вот тут то *опа и закралась')

            if wrong_user_request != -1:
                wrong_user_request = str(wrong_user_request) + ' - ' + user
                save_stange_user_requests(wrong_user_request)
        else:
            if message.text == 'Сотовые номера сотрудников':
                output_message = 'Выберите букву с которой начинается фамилия'
                bot.send_message(message.chat.id, output_message, parse_mode="Markdown", reply_markup=keyboard2)
            elif message.text == 'Вернутся в главное меню':
                output_message = 'Введите код товара или название'
                bot.send_message(message.chat.id, output_message, parse_mode="Markdown", reply_markup=keyboard1)
            elif message.text == 'Реквизиты фирм':
                output_message = 'Здесь будет запрос на выбор реквизитов с выбором фирм'
                bot.send_message(message.chat.id, output_message, parse_mode="Markdown", reply_markup=keyboard1)
            elif (message.text.lower() == 'телефоны') or (message.text == 'Внутренние номера') or (message.text.lower() == 'номер') or (message.text.lower() == 'телефоны'):
                output_message = """
*ДИРЕКЦИЯ:*
    Усцов А.В.  -  115
    Малыгин М.Я.  -  302
    Колобов Е.Е.  -  114
    Панкратов А.С.  -  110
                        
*ОТДЕЛ ОПТОВЫХ ПРОДАЖ:*
    Стариков А.С.  -  211
    Чирков М.С  -  235
    Ситников М.В.   -  252
    Страхов Д.М.  -  116
    Ивлев В.В.  -  201

*ОТДЕЛ ПРЯМЫХ ПРОДАЖ:*    
    Анисимов С.Ю.  -  122
    Городчиков В.Н.  -  222
    Деветьяров Р.И.  -  244
    Делог К.Н.  -  103
    Ефимов С.Б.  -  230
    Загоскин В.В.  -  224
    Костров И.Е.  -  255
    Кузнецов А.В.  -  221
    Кукреш П.А.  -  125
    Новоселов Е.А.  -  220
    Пичугин Д.Ю.  -  261
    Бузмаков А.П.  -  128
    Помыткин Д.О.  -  259
    Петрушин П.А.  -  130
    Рубцов А.А.  -  237
    Поглазова М.Н.  -  104
    Садовников И.С.  -  131
    Спиридонов Ю.В.  -  108
    Ускова Я.О.  -  245
    Шустова О.А.  -  234

*ОТДЕЛ СНАБЖЕНИЯ:*
    Смотрин Д.В.  -  112
    Зубарев М.А.  -  240
    Девятериков И.В.  -  233
    Ляпина Е.В.  -  129
    Широкова А.С.  -  218
    Вахрушев П.Ю.  -  133

*ОТДЕЛ МАРКЕТИНГА:*
    Сущих Н.С.  -  251
    Маргиева И.А.  -  121
    Пантюхина Я.Л.  -  260

*КАССЫ + РЕСЕПШН:*
    Ресепшен Пугачева  -  101, 102, 229 (факс)
    Кассы Пугачева  -  231
    Кассы Чепецк  -  75-15-10 или 83361-2-25-25
    Кассы Дзержинского  -  304
    Кассы Сыктывкар  -  400

*БУХГАЛТЕРИЯ:*
    Шемаева А.В.  -  117
    Сидина Н.Р.  -  118
    Сметанина И.В.  -  119
    Широкова И.Н.  -  243

*ОФИСНЫЕ СОТРУНИКИ:*
    Крекнин Д.Г.  -  227
    Кашина Ю.А.  -  124
    Шалагинов А.Н.  -  232
    Овечкин А.А.  -  258
    Пантелеева О.Ю.  -  256
    Сущих А.В.  -  109

*СКЛАД ПУГАЧЕВА:*
    Маргиев С.Н.  -  226
    Утешева С.С.  -  225
    Алексеева Л.П.  -  257
    Ходырев В.Ю.  -  238
    Армяков А.В.  -  223

*СЕРВИСНЫЙ ЦЕНТР:*
    Скопин С.В.  -  250
    Мастерская 2 эатж  -  249
    Приемка  -  246, 247, 126
    Офис  -  202
    Бухгалтер  -  253
    Якурнова М.А.  -  248

*МАГАЗИН СЫКТЫВКАР*
    Магазин  -  (8212) 400-456, 8922-598-59-72
    Кузнецов С.А.  -  403
    Ходченко Д.В.  -  404
    Батманов А.Г.  -  401
    Туров Е.А.  -  402

*МАГАЗИН ДЗЕРЖИНСКОГО*
    Касса  -  304
    Токарев И.С.  -  305
    Охрана  -  306
    Перминов А.С.  -  307
    Копосов В.Н.  -  311
    Эсаулов К.И.  -  313
    Андреев К.В.  -  312
    Шихов С.Б.  -  303

*МАГАЗИН ПУГАЧЕВА:*
    Верещагин Д.Н.  -  106
    Токмаков И.Н.  -  132
    Маренин А.А.  -  242
    Торговый зал  -  107, 123
    Крепёж  -  228
    Решетняк А.К.  -  254
    Тетенькин В.А.  -  105


    
    
"""
                bot.send_message(message.chat.id, output_message, parse_mode="Markdown", reply_markup=keyboard1)

            elif len(message.text) > 2:
                output_message = find_item_func(logger, message.text, dataframe)
                bot.send_message(message.chat.id, output_message, parse_mode="Markdown")
            elif message.text.lower() == 'да':
                bot.send_message(message.chat.id, 'Хорошо, я написал разработчику, спасибо! 🚀')
            elif message.text.lower() == 'up':
                output_message = 'время обновления файла с данным: ' + str(time_of_data_file) + '(время серверное -3)'
                bot.send_message(message.chat.id, output_message)
            elif message.text in letters:
                output_message = dict_of_phones[message.text]
                bot.send_message(message.chat.id, output_message, parse_mode="Markdown", reply_markup=keyboard1)


    bot.polling()

    # while True:
    #     try:
    #         bot.polling()
    #     except Exception as e:
    #         print(e)
    #         sleep(15)


def test_func(logger):
    # logger.error('some error')
    pass


if __name__ == '__main__':
    logger = 'some_thing_for_test'
    get_picture_of_item(logger, '884')


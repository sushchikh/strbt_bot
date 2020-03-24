import yaml
import logging.config
import os
import pandas as pd
import telebot
import datetime
import requests
from datetime import timedelta
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
    with open('./config.yaml', 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    logger = logging.getLogger(__name__)
    return logger


# --------------------------------------------------------------------------------------------
# определяет какой из файлов в папке свежий, возвращает имя новейшего xls-файла
def get_name_of_newest_data_file(logger):
    """filter full_list of files by end ".xls", sorted by time of change and take last one:"""
    try:
        path_to_data_dir = '../data'
        file_list = os.listdir(path_to_data_dir)
        full_list = [os.path.join(path_to_data_dir, i) for i in file_list]  # get full list of all files in dir
        newest_file_name = sorted(filter(lambda x: x.endswith('.xls'), full_list), key=os.path.getmtime)[-1]
        return newest_file_name
    except FileNotFoundError as e:
        error_message = 'moduls/get_name_of_newest_data_file - ' + str(e)
        logger.error(error_message)


# --------------------------------------------------------------------------------------------
# берет свежайщий файл, считывает его в датафрейм пандасовский
def get_strbt_dataframe_from_xls_file(logger, newest_file_name):
    """read xls-file, return dataframe"""

    try:
        strbt_dataframe = pd.read_excel(newest_file_name, engine='xlrd', index_col='id')
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
        item_name = dataframe.loc[[message], ['Номенклатура']].values[0][0]
        item_measure = dataframe.loc[[message], ['Ед.изм.']].values[0][0]
        if item_measure == 'шт':
            item_value = int(dataframe.loc[[message], ['Количество']].values[0][0])
        else:
            item_value = str(dataframe.loc[[message], ['Количество']].values[0][0])
        item_reserve = dataframe.loc[[message], ['Резерв']].values[0][0]
        if not(str(item_reserve).isdigit()):
            item_reserve = 0
        # item_price_prepayment = dataframe.loc[[message], ['ОптПредоплата']].values[0][0]
        # item_price_retail = dataframe.loc[[message], ['Розница']].values[0][0]
        item_price_prepayment = str('{0:,}'.format(dataframe.loc[[message], ['ОптПредоплата']].values[0][0])).replace(',', ' ')
        item_price_retail = str('{0:,}'.format(dataframe.loc[[message], ['Розница']].values[0][0])).replace(',', ' ')


        output_message = f"""    {item_name}

остаток:  {item_value} {item_measure}
резерв:  {item_reserve} {item_measure}

розница:  {item_price_retail} р.
опт-предоплата:  {item_price_prepayment} р."""
        # print(output_message)
        wrong_user_request = -1  # magic numbers =)
        is_item_exist = True
    except ValueError:
        output_message = 'Это не код товара, попробуй снова'
        wrong_user_request = message
        is_item_exist = False
    except KeyError:
        output_message = """Я не знаю такого кода товара.
Если ты уверен, что все правильно — напиши мне "да" и я сообщу об этом разработчику =)"""
        wrong_user_request = message
        is_item_exist = False

    return output_message, wrong_user_request, is_item_exist
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
    now_date_time_on_server = datetime.datetime.now() + timedelta(hours=3)
    formated_date_time = now_date_time_on_server.strftime('%d.%m.%y, %H:%M:%S') + ' - '
    # print(now_date_time)
    output_line = '\n' + formated_date_time + user_message
    with open('./../logs/users_message.txt', 'a') as f:
        f.write(output_line)

def save_stange_user_requests(user_request):
    """
    Get user message, push it into file with current date and time
    """
    now_date_time_on_server = datetime.datetime.now() + timedelta(hours=3)
    formated_date_time = now_date_time_on_server.strftime('%d.%m.%y, %H:%M:%S') + ' - '
    # print(now_date_time)
    output_line = '\n' + formated_date_time + str(user_request)
    with open('./../logs/users_strange_requests.txt', 'a') as f:
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
        url = 'http://stroybatinfo.ru/test/' + str(int(message)) + '.jpg'
        r = requests.get(url)
        print('status_code:', r.status_code)
        if r.status_code == 404:
            item_img_name = 'No such image =('
            return False, item_img_name
        open('./../img/' + str(message) + '.jpg', 'wb').write(r.content)
        item_img_name = './../img/' + str(message) + '.jpg'
        return True, item_img_name  # if file exist
    except (FileNotFoundError, FileExistsError) as e:
        error_message = 'moduls/get_picture_of_item - ' + str(e)
        logger.error(error_message)
        item_img_name = 'No such image =('
        return False, item_img_name  # if file not exist


########   #######  ########
##     ## ##     ##    ##
##     ## ##     ##    ##
########  ##     ##    ##
##     ## ##     ##    ##
##     ## ##     ##    ##
########   #######     ##


def get_bot_token_from_yaml(logger):
    try:
        with open('./../data/lpt.yaml', 'r') as f:
            lpt = yaml.safe_load(f.read())
            token = lpt['token']
        return token
    except FileNotFoundError as e:
        error_message = ('moduls/get_token_from_yaml - ' + str(e) + ' no token-file')
        logger.error(error_message)


def bot_runner(logger, token, dataframe):
    bot = telebot.TeleBot(token)  # create bot

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

        # обработчик сообщения пользователя:
        if is_message_digit(message.text):
            # description of item:
            output_message, wrong_user_request, is_item_exist = get_item_from_dataframe(logger, dataframe, message.text)
            bot.send_message(message.chat.id, output_message)
            # download and send photo
            is_image_exist, item_img_name = get_picture_of_item(logger, message.text)
            if is_image_exist and is_item_exist:
                photo = open(item_img_name, 'rb')
                bot.send_photo(message.chat.id, photo)
                photo.close()
            elif is_item_exist and not(is_image_exist):
                bot.send_message(message.chat.id, item_img_name)  # if no image send message
            elif not(is_item_exist) and not(is_image_exist):
                pass

            if wrong_user_request != -1:
                wrong_user_request = str(wrong_user_request) + ' - ' + user
                save_stange_user_requests(wrong_user_request)
        else:
            if 'привет' in message.text.lower():
                bot.send_message(message.chat.id, 'И тебе привет')
            elif message.text == 'Пока':
                bot.send_message(message.chat.id, 'Пока')
            elif message.text.lower() == 'да':
                bot.send_message(message.chat.id, 'Хорошо, я написал разработчику, спасибо!')




    while True:
        try:
            bot.polling()
        except Exception as e:
            print(e)
            sleep(15)


def test_func(logger):
    # logger.error('some error')
    pass


if __name__ == '__main__':
    logger = 'some_thing_for_test'
    get_picture_of_item(logger, '884')


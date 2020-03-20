import yaml
import logging.config
import os
import pandas as pd
import telebot
import datetime
import random
from datetime import timedelta



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


def bot_runner(logger, token):
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

        if 'привет' in message.text.lower():
            bot.send_message(message.chat.id, 'И тебе привет')
        elif message.text == 'Пока':
            bot.send_message(message.chat.id, 'Пока')

    bot.polling()


def test_func(logger):
    # logger.error('some error')
    pass



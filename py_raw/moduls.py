import yaml
import logging.config
import os
import pandas as pd
import telebot
import datetime
from datetime import datetime
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
        return newest_file_name
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
        item_name = dataframe.loc[[message], ['Номенклатура']].values[0][0].split(', ')
        formated_item_name = ''
        for i in item_name:
            if i == item_name[0]:
                formated_item_name = '*' + formated_item_name + str(i) + '*' + '\n'
            else:
                formated_item_name = formated_item_name + str(i) + '\n'
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
        # item_price_prepayment = dataframe.loc[[message], ['ОптПредоплата']].values[0][0]
        # item_price_retail = dataframe.loc[[message], ['Розница']].values[0][0]
        item_price_prepayment = str(dataframe.loc[[message], ['ОптПредоплата']].values[0][0])
        item_price_retail = str(dataframe.loc[[message], ['Розница']].values[0][0])
        item_bonus = (str(dataframe.loc[[message], ['Бонус']].values[0][0]))

        output_message = f"""    {formated_item_name}
*ОСТАТКИ:*
Пугачева:  {item_pugach_value} {item_measure}
Дзержинскго:  {item_dzerj_value} {item_measure}
Чепецк:  {item_chepetsk_value} {item_measure}
Сыктывкар:  {item_siktivkar_value} {item_measure}

резерв:  {item_reserve} {item_measure}

розница:  *{item_price_retail}* р.
опт-предоплата:  *{item_price_prepayment}* р.
бонус:  {item_bonus}"""
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

    list_of_words_from_user_message = message.strip().lower().split(' ')
    # print(strbt_dataframe)
    print('поисковое пользовательское сообщене:', *list_of_words_from_user_message)
    # print(strbt_dataframe.iloc[1]['Номенклатура'])
    count_of_matches = 0
    pos_of_match_item = []
    list_of_few_items_names = []
    for i in range(len(dataframe)):

        list_of_words_from_dataframe_item = str(dataframe.iloc[i]['Номенклатура']).replace('"', '').replace('(','').replace(')', '').strip().lower().split(' ')

        # print(*list_of_words_from_dataframe_item)
        check = all(item in list_of_words_from_dataframe_item for item in list_of_words_from_user_message)
        if check:
            count_of_matches += 1
            pos_of_match_item.append(dataframe.iloc[i])
            list_of_few_items_names.append(str(
                '*' +
                str(dataframe.index.values[i]) +
                '*' + ' - ' +
                str(dataframe.iloc[i]['Номенклатура']).replace('"', '').replace('(', '').replace(')', '').strip()))
    # if count_of_matches == 1:
    #     output_message = ('Нашел одно совпадение:\n' +
    #                       str(pos_of_match_item[0]) + ' - ')
        if count_of_matches > 11:
            break

    if count_of_matches == 0:
        output_message = 'не нашел ни одного совпадения, либо что-то пошло не так 😖'
    elif count_of_matches > 10:
        output_message = "слишком много совпадений, попробуй уточнить запрос"
    elif 1 <= count_of_matches <= 10:  # если совпадения есть
        # print(f'*нашел {count_of_matches} совпадений:*\n\n')
        output_message = f'*нашел {count_of_matches} совпадений:*\n\n'
        for i in list_of_few_items_names:
            output_message += (str(i) + '\n')
    else:
        output_message = 'опа-опа'

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


def bot_runner(logger, token, dataframe):
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

        # обработчик сообщения пользователя:
        if is_message_digit(message.text):
            # description of item:
            output_message, wrong_user_request, is_item_exist = get_item_from_dataframe(logger, dataframe, message.text)
            bot.send_message(message.chat.id, output_message, parse_mode="Markdown")
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
                pass

            if wrong_user_request != -1:
                wrong_user_request = str(wrong_user_request) + ' - ' + user
                save_stange_user_requests(wrong_user_request)
        else:
            if len(message.text) > 2:
                output_message = find_item_func(logger, message.text, dataframe)
                bot.send_message(message.chat.id, output_message, parse_mode="Markdown")
            elif 'привет' in message.text.lower():
                bot.send_message(message.chat.id, 'И тебе привет')
            elif message.text == 'Пока':
                bot.send_message(message.chat.id, 'Пока')
            elif message.text.lower() == 'да':
                bot.send_message(message.chat.id, 'Хорошо, я написал разработчику, спасибо! 🚀')

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


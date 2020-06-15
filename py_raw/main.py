from moduls import get_logger
from moduls import test_func
from moduls import get_name_of_newest_data_file
from moduls import get_strbt_dataframe_from_xls_file
from moduls import get_bot_token_from_yaml
from moduls import bot_runner
from moduls import save_user_message
from moduls import get_item_from_dataframe
from moduls import data_downloader
from moduls import get_dict_phones_from_file_by_letter

from time import sleep


if __name__ == "__main__":
    print()
    logger = get_logger()
    data_downloader(logger)
    test_func(logger)
    dict_of_phones = get_dict_phones_from_file_by_letter()
    newest_data_file, time_of_data_file = get_name_of_newest_data_file(logger)
    strbt_dataframe = get_strbt_dataframe_from_xls_file(logger, newest_data_file)
    # TODO добавить считывание свежего датафрема по таймеру, скажем каждые два часа
    # print(strbt_dataframe)
    print('sleep 3 sec for data download well')
    sleep(3)
    token = get_bot_token_from_yaml(logger)
    print('token get well done')
    bot_runner(logger, token, strbt_dataframe, time_of_data_file, dict_of_phones)



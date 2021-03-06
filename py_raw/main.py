from moduls import get_logger
# from moduls import get_name_of_newest_data_file  # deprecated
from moduls import get_strbt_dataframe_from_xls_file
from moduls import get_bot_token_from_yaml
from moduls import bot_runner
# from moduls import save_user_message  # deprecated
# from moduls import get_item_from_dataframe  # deprecated
# from moduls import data_downloader  # deprecated
from moduls import get_dict_phones_from_file_by_letter
from moduls import get_dict_of_inside_phone_numbers
from moduls import get_today_data_file_name

from time import sleep


if __name__ == "__main__":
    print()
    logger = get_logger()
    # data_downloader(logger)
    dict_of_phones = get_dict_phones_from_file_by_letter()
    dict_of_inside_phone_numbers = get_dict_of_inside_phone_numbers()
    # newest_data_file, time_of_data_file = get_name_of_newest_data_file(logger)
    today_data_file, yesterday_data_file = get_today_data_file_name()
    strbt_dataframe = get_strbt_dataframe_from_xls_file(logger, today_data_file, yesterday_data_file)
    print('sleep 3 sec for data download well')
    sleep(3)
    token = get_bot_token_from_yaml(logger)
    print('token get well done')
    bot_runner(logger, token, strbt_dataframe, dict_of_phones, dict_of_inside_phone_numbers)



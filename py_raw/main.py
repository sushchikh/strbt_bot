from moduls import get_logger
from moduls import test_func
from moduls import get_name_of_newest_data_file
from moduls import get_strbt_dataframe_from_xls_file
from moduls import get_bot_token_from_yaml
from moduls import bot_runner
from moduls import save_user_message

if __name__ == "__main__":
    logger = get_logger()
    test_func(logger)
    newest_data_file = get_name_of_newest_data_file(logger)
    strbt_dataframe = get_strbt_dataframe_from_xls_file(logger, newest_data_file)

    token = get_bot_token_from_yaml(logger)
    # bot_runner(logger, token)

    user_message = 'some string'
    save_user_message(user_message)

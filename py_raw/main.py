from moduls import get_logger
from moduls import test_func
from moduls import get_name_of_newest_data_file
from moduls import get_strbt_dataframe_from_xls_file

if __name__ == "__main__":
    logger = get_logger()
    print(logger)
    test_func(logger)
    newest_data_file = get_name_of_newest_data_file(logger)
    strbt_dataframe = get_strbt_dataframe_from_xls_file(logger, newest_data_file)
    print(strbt_dataframe)

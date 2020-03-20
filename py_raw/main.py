from moduls import get_logger
from moduls import test_func
from moduls import get_name_of_newest_data_file

if __name__ == "__main__":
    logger = get_logger()
    test_func(logger)
    newest_data_file = get_name_of_newest_data_file(logger)
    print(newest_data_file)

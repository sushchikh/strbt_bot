import yaml
import logging.config
import os
import pandas as pd

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
#
def get_strbt_dataframe_from_xls_file(logger, newest_file_name):
    """read xls-file, return dataframe"""
    try:
        strbt_dataframe = pd.read_excel(newest_file_name, engine='xlrd', index_col='id')
        return strbt_dataframe
    except ValueError as e:
        error_message = 'moduls/get_strbt_dataframe_from_xls_file - ' + str(e) + ' no argument with file name, look get_name_of_newest_data_file function'
        logger.error(error_message)
    except FileNotFoundError as e:
        error_message = 'moduls/get_strbt_dataframe_from_xls_file - ' + str(e)
        logger.error(error_message)

def test_func(logger):
    # logger.error('some error')
    pass



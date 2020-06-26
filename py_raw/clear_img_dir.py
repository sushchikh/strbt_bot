import os
import datetime
from datetime import datetime


def remove_imgs():
    path_to_data_dir = '/home/sushchikh/strbt_bot/img/'
    file_list = os.listdir(path_to_data_dir)
    full_list = [os.path.join(path_to_data_dir, i) for i in file_list]
    # print('количество файлов:', len(full_list))
    # print(full_list)
    for item in full_list:
        os.remove(item)


def get_name_of_newest_data_file():
    """filter full_list of files by end ".csv", sorted by time of change and take last one:"""
    try:
        path_to_data_dir = '/home/sushchikh/strbt_bot/data'
        file_list = os.listdir(path_to_data_dir)
        today = datetime.today()
        today_data_file = str(today.strftime("%Y%m%d")) + '.csv'
        if today_data_file in file_list:
            print()
            print('Списко всех файлов в папке:', file_list)
            file_list_for_remove = file_list[0:file_list.index(today_data_file)] + file_list[(file_list.index(today_data_file)+1):]
            for item in file_list_for_remove:
                item_for_remove = '/home/sushchikh/strbt_bot/data/' + str(item)
                os.remove(item_for_remove)
            print('Список файлов после удаления', os.listdir(path_to_data_dir))
        else:
            pass

    except Exception as e:
        error_message = 'moduls/get_name_of_newest_data_file - ' + str(e)
        print(error_message)


if __name__ == "__main__":
    remove_imgs()
    get_name_of_newest_data_file()

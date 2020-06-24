from datetime import datetime
import requests


def data_downloader():
    today = datetime.today()
    # print(today.strftime("%Y%m%d"))
    path_to_data_file_on_server = ('http://stroybatinfo.ru/import_1c/for_bot/' + str(today.strftime("%Y%m%d")) + '.csv')
    # print(path_to_data_file_on_server)
    try:
        data_file = requests.get(path_to_data_file_on_server, allow_redirects=True)
        name_of_saving_file = '/home/sushchikh/strbt_bot/data/' + str(today.strftime("%Y%m%d") + '.csv')
        with open(name_of_saving_file, 'wb') as file:
            file.write(data_file.content)
    except Exception as e:
        print('не нашел свежего датника!')
    print('data download well done')


if __name__ == '__main__':
    data_downloader()

import requests
import pandas as pd
from datetime import datetime



def data_downloader(logger):
    today = datetime.today()
    # print(today.strftime("%Y%m%d"))
    path_to_data_file_on_server = ('http://stroybatinfo.ru//import_1c/for_bot/' +
                                   str(today.strftime("%Y%m%d")) + '.csv')
    print(path_to_data_file_on_server)

    data_file = requests.get(path_to_data_file_on_server, allow_redirects=True)
    name_of_saving_file = './../data/' + str(today.strftime("%Y%m%d"))
    with open(name_of_saving_file, 'wb') as file:
        file.write(data_file.content)


logger = 'logger'
# data_downloader(logger)


def read_from_data_file(logger):
    strbt_dataframe = pd.read_csv('./../data/20200326.csv', index_col='Код', delimiter=';', encoding='windows-1251', error_bad_lines=False)

    return strbt_dataframe

strbt_df = read_from_data_file(logger)
for col in strbt_df.columns:
    print(col)
print(strbt_df.head(5))
print(strbt_df)
print(strbt_df.loc[[15929], ['Номенклатура']].values[0][0])
item_pugach_value = int(strbt_df.loc[[15929], ['Количество Основной склад']].values[0][0])
item_dzerj_value = int(strbt_df.loc[[15929], ['Количество База Дзержинского']].values[0][0])
item_chepetsk_value = int(strbt_df.loc[[15929], ['Количество Чепецк']].values[0][0])
item_siktivkar_value = int(strbt_df.loc[[15929], ['Количество Сыктывкар']].values[0][0])
item_measure = strbt_df.loc[[15929], ['Ед.изм.']].values[0][0]
item_reserve = strbt_df.loc[[15929], ['Резерв']].values[0][0]
item_price_prepayment = str(strbt_df.loc[[15929], ['ОптПредоплата']].values[0][0])
item_price_retail = str(strbt_df.loc[[33905], ['Розница']].values[0][0])
item_bonus = (str(strbt_df.loc[[33905], ['Бонус']].values[0][0]))

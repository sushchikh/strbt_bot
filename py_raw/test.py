import pandas as pd


logger = 'logger'
message = 'пила дисковая Metabo'


strbt_dataframe = pd.read_csv("./../data/20200326.csv", index_col='Код', delimiter=';', encoding='windows-1251',
                                      error_bad_lines=True)


def find_item_func(logger, message, dataframe):
    """
    split message by whitespace, check matches in all items_names
    """
    list_of_words_from_user_message = message.strip().lower().split(' ')
    # print(strbt_dataframe)
    # print('разделеное пользовательское сообщене:', *list_of_words_from_user_message)
    # print(strbt_dataframe.iloc[1]['Номенклатура'])
    count_of_matches = 0
    pos_of_match_item = []
    list_of_few_items = []
    for i in range(len(dataframe)):
        list_of_words_from_dataframe_item = str(dataframe.iloc[i]['Номенклатура']).replace('"', ' ').replace('(', '').replace(')', '').strip().lower().split(' ')
        # print(*list_of_words_from_dataframe_item)
        check = all(item in list_of_words_from_dataframe_item for item in list_of_words_from_user_message)
        if check:
            count_of_matches += 1
            pos_of_match_item.append(dataframe.iloc[i])
            print(str(dataframe.index.values[i]))
            print(str(dataframe.iloc[i]['Номенклатура']).replace('"', ' ').strip().lower())

    if count_of_matches == 1:
        print('Нашел одно совпадение:\n', pos_of_match_item[0])
    elif count_of_matches == 0:
        print('не нашел ни одного совпадения, либо что-то пошло не так ❌')
    else:
        print(f'нашел {count_of_matches} совпадений\n')
        # print(strbt_dataframe.iloc[i]['Номенклатура'])


find_item_func(logger, message, strbt_dataframe)

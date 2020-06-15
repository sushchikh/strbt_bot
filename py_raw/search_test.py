import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import time





df = pd.read_csv('./../data/20200514.csv', encoding='windows-1251', index_col='Код',
                 error_bad_lines=True, delimiter=';')

# print(df.head())

# start = time.monotonic()
# for i in range(len(df['Номенклатура'])):
#     if fuzz.token_set_ratio('Бензопила ms-180', df.iloc[i]['Номенклатура']) >= 95:
#         print(df.iloc[i]['Номенклатура'])
# print('время варианта 1:', time.monotonic() - start)


start = time.monotonic()
def get_sample(sample, string):
    return fuzz.token_set_ratio(sample, string)
    # return fuzz.WRatio(sample, string)


output_message = ''
search_message = 'Перфоратор gbh 2-26'

output_df = df[df['Номенклатура'].apply(get_sample, args=[search_message]) > 95]
for i in output_df.index:
    # print(i, output_df.loc[[i], ['Номенклатура']].values[0][0])
    output_message += '*' + str(i) + '* ' + str(output_df.loc[[i], ['Номенклатура']].values[0][0]) + '\n'
print(output_message)

nomenklatura_list = df['Номенклатура'].tolist()
print(f'метод extract:, {process.extract(search_message, nomenklatura_list, limit=3)}')
print(f'метод extractOne:, {process.extractOne(search_message, df["Номенклатура"])}')
print(f'метод extractBest:, {process.extractBests(search_message, df["Номенклатура"])}')




print('\nвремя варианта 2:', time.monotonic() - start)


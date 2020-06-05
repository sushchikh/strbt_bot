import pandas as pd
from fuzzywuzzy import fuzz
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
output_message = ''
search_message = 'Перфоратор gbh 2-26'
# print(df[df['Номенклатура'].apply(get_sample, args=[search_message]) > 95]['Номенклатура'])
output_df = df[df['Номенклатура'].apply(get_sample, args=[search_message]) > 95]
for i in output_df.index:
    # print(i, output_df.loc[[i], ['Номенклатура']].values[0][0])
    output_message += '*' + str(i) + '* ' + str(output_df.loc[[i], ['Номенклатура']].values[0][0]) + '\n'
print(output_message)
# print(output_df.index)
# print(output_df)
# for i in output_df:
#     print(i)
print('\nвремя варианта 2:', time.monotonic() - start)


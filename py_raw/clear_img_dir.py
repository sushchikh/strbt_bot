import os
from time import sleep
path_to_data_dir = '/home/sushchikh/strbt_bot/img/'
file_list = os.listdir(path_to_data_dir)
full_list = [os.path.join(path_to_data_dir, i) for i in file_list]
print('количество файлов:', len(full_list))
print(full_list)
for item in full_list:
    os.remove(item)


sleep(10)
path_to_data_dir = '/home/sushchikh/strbt_bot/data/'
file_list = os.listdir(path_to_data_dir)
full_list = [os.path.join(path_to_data_dir, i) for i in file_list]
print('количество файлов:', len(full_list))
print(full_list)
for item in full_list:
    os.remove(item)


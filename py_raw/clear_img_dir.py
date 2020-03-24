import os
from time import sleep
path_to_data_dir = './../img'
file_list = os.listdir(path_to_data_dir)
full_list = [os.path.join(path_to_data_dir, i) for i in file_list]
print('количество файлов:', len(full_list))
print(full_list)
for item in full_list:
    os.remove(item)
# sleep(10)
file_list = os.listdir(path_to_data_dir)
print('количество файлов:', len(full_list))

import unittest
from moduls import get_logger
from moduls import get_name_of_newest_data_file

# класс наследующий свойства от юниттест-кейса
class NamesTestCase(unittest.TestCase):

# будут запущены функции, начинающиеся или заканчивающиеся со слова test
#     def test_first_last_names(self):
#         result = get_full_name('petr', 'ivanov')  # в переменную результат работы функции с задаными параметрами
#         self.assertEqual(result, 'Petr Ivanov')  # выкинем ассерт, если результат теста не равен вышезаданному
#
#     def test_first_last_second_names(self):
#         result = get_full_name('petr', 'ivanov', 'sergeevich')
#         self.assertEqual(result, 'Petr Sergeevich Ivanov')

    def test_logger_function(self):
        result = get_logger()
        self.assertTrue(result,'no logger found')


if __name__ == '__main__':
    unittest.main()

import yaml
import logging.config


# --------------------------------------------------------------------------------------------
# созадет и возвращает логгер для логирования в файл
def get_logger():
    with open('./config.yaml', 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    logger = logging.getLogger(__name__)
    return logger


def test_func(logger):
    logger.error('some error')

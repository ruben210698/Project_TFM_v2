########################################################################################################################
########################################################################################################################
import logging
import os

def create_logger():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler('logs_1.log')
    file_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(message)-70s  --> (((%(asctime)s-%(name)s-%(levelname)s-(%(filename)s-%(funcName)s:::%(lineno)d)))))'
    )
    console_handler.setFormatter(formatter)

    if (root_logger.hasHandlers()):
        root_logger.handlers.clear()

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    logging.getLogger('matplotlib.font_manager').setLevel(logging.INFO)
    logging.getLogger('matplotlib.pyplot').setLevel(logging.INFO)

########################################################################################################################
########################################################################################################################

FORMAT_1 = '%(message)-70s  --> (((%(asctime)s-%(name)s-%(levelname)s-(%(filename)s-%(funcName)s:::%(lineno)d)))))'
def get_format():
    formatter = logging.Formatter(
        '%(message)-70s  --> (((%(asctime)s-%(name)s-%(levelname)s-(%(filename)s-%(funcName)s:::%(lineno)d)))))'
    )
    return formatter

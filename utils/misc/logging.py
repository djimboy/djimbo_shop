# - *- coding: utf- 8 - *-
import logging


def get_info(text):
    logging.basicConfig(
        level=logging.INFO,
        filename="logs.log",
        format=u'[%(levelname)s] [%(asctime)s] | [%(filename)s LINE:%(lineno)d] | %(message)s',
        datefmt="%d-%b-%y %H:%M:%S"
    )
    logging.info(text)


def get_error(text):
    logging.basicConfig(
        level=logging.ERROR,
        filename="logs.log",
        format=u'[%(levelname)s] [%(asctime)s] | [%(filename)s LINE:%(lineno)d] | %(message)s',
        datefmt="%d-%m-%y %H:%M:%S"
    )
    logging.error(text)

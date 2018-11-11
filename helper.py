import csv
from typing import List
import requests
from bs4 import BeautifulSoup


def get_articles_with_grade(grade='C') -> List:
    URLS = {
        'C': 'https://tools.wmflabs.org/enwp10/cgi-bin/list2.fcgi?run=yes&projecta=Computing&namespace=&pagename=&quality=C-Class&importance=&score=&limit=1000&offset=1&sorta=Importance&sortb=Quality'
    }

    r = requests.get(URLS.get(grade))
    html = r.content
    root = BeautifulSoup(html)
    tbl = root.find(class_='wikitable')

    l1 = tbl.find_all(class_='list-odd')
    l2 = tbl.find_all(class_='list-even')

    raise NotImplementedError()
    return []


def read_csv(csv_path: str, handler, contains_header=True):
    """

    :param csv_path:
    :param handler: A function that takes a row-array as input
    :param contains_header:
    :return:
    """
    start_row = 1 if contains_header else 0
    with open(csv_path) as csvfile:
        rows = list(csv.reader(csvfile))
        ret = []
        for row in rows[start_row:]:
            ret.append(handler(row))
        return ret


def calc_freq(arr: list):
    raise NotImplementedError()
    return 0


def is_bot_user(username, userid):
    # fixme
    return 'bot' in str.lower(username)

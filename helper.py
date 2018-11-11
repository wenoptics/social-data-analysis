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


get_articles_with_grade()

import requests
from bs4 import BeautifulSoup, Tag


class Article:

    def __init__(self, id_, grade=''):
        self.__grade = grade
        self.id_ = id_

    @property
    def grade(self):
        return self.__grade.upper()


class WikiAPI:
    __base_url = "https://en.wikipedia.org/w/"

    @staticmethod
    def get(url: str, params=None):
        if params is None:
            params = {}
        if 'format' not in params:
            params['format'] = 'json'
        if url.startswith('api.php'):
            url = WikiAPI.__base_url + url

        print('[i] requesting "{}" with param {}'.format(url, params))
        req = requests.get(url, params=params)
        return req.json()


class WikiBrowser:
    __url_article_main = 'https://en.wikipedia.org/wiki/{id_}'
    __url_article_talk = 'https://en.wikipedia.org/wiki/Talk:{id_}'

    @staticmethod
    def get_talk_page(article_id: str) -> Tag:
        resp = requests.get(WikiBrowser.__url_article_talk.format(id_=article_id))
        return BeautifulSoup(resp.content, 'html.parser')

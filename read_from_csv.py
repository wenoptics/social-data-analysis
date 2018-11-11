import csv
import requests
from bs4 import BeautifulSoup, Tag

from WikiComponents import Article


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


def get_first_query_page(resp: dict) -> dict:
    pg = resp['query']['pages']
    if len(pg) != 1:
        print("[W] len(pg) != 1")
    k = list(pg.keys())[0]
    return pg[k]


def get_contributors(article_id):
    # todo Use combined query makes more efficient.
    _url = "api.php?action=query&titles={article_id}&prop=contributors"
    resp = WikiAPI.get(_url.format(article_id=article_id))
    first = get_first_query_page(resp)
    n_contributers_a = first['anoncontributors']
    n_contributers = len(first['contributors'])
    return {'anoncontributors': n_contributers_a, 'contributors': n_contributers}


def get_revision(article_id):
    _url = 'api.php?action=query&prop=revisions&titles={article_id}' \
           '&rvprop=timestamp|user|userid&rvlimit=max'
    u = _url.format(article_id=article_id)

    revs = {}

    def proc(resp: dict):
        """
        "revisions": [
        {
            "user": "74.96.187.144",
            "anon": "",
            "userid": 0,
            "timestamp": "2009-11-22T17:04:09Z"
        },
        {
            "user": "Miym",
            "userid": 8436643,
            "timestamp": "2009-07-30T15:35:49Z"
        }
        """
        first = get_first_query_page(resp)
        for rv in first['revisions']:
            uid = rv['userid']
            if uid in revs:
                revs[uid].append(rv)
            else:
                revs[uid] = [rv]

    resp = WikiAPI.get(u)
    proc(resp)

    while resp.get('continue') and resp['continue'].get('rvcontinue'):
        resp = WikiAPI.get(u, {'rvcontinue': resp['continue']['rvcontinue']})
        proc(resp)

    return revs


def analysis_revision_info(dict_rev_info: dict):
    # Number of edits per editors
    pass

    # Frequency of edits (time between edits)
    freq_overall = 0
    for uid, revisions in dict_rev_info.items():
        pass


def count_talk_posts(article_id):
    html_root = WikiBrowser.get_talk_page(article_id)
    return len(html_root.find('div', id='bodyContent').find_all('h2'))


def num_editor_talk(article_id):
    # Use an API provided by XTools Wiki-Project
    _url = 'https://xtools.wmflabs.org/api/page/articleinfo/en.wikipedia.org/Talk:{article_id}'
    resp = requests.get(_url.format(article_id=article_id)).json()
    return resp['editors']


def process_article(article: Article):
    print('\n', '-' * 6)
    print('processing "{}"'.format(article.id_))

    # get unique contributor
    uniq_con = get_contributors(article.id_)
    print('unique contributor:', uniq_con)

    # get user revisions
    rvs = get_revision(article.id_)
    analysis_revision_info(rvs)
    print()

    # talk-page posts
    ctp = count_talk_posts(article.id_)
    print('talk-page posts n=', ctp)

    # Number of editors posting on talk-pages
    etp = num_editor_talk(article.id_)
    print('talk-page editor n=', etp)


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


if __name__ == '__main__':
    article_list = read_csv("data/articles.csv",
                            lambda row: Article(id_=row[1], grade=row[2]))

    # Group those `good` and `not-so-good` articles
    groupGood = list(filter(lambda i: i.grade in ['A', 'FA', 'GA'], article_list))
    groupNSGood = list(filter(lambda i: i.grade in ['C', 'Start'], article_list))

    print('groupGood: n =', len(groupGood))
    print('groupNSGood: n =', len(groupNSGood))

    [process_article(i) for i in groupGood]
    [process_article(i) for i in groupNSGood]

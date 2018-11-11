import csv
import requests

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
        first = get_first_query_page(resp)
        for rv in first['revisions']:
            uid = rv['userid']
            if uid in revs:
                revs[uid].append(rv)
            else:
                revs[uid] = [rv]
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

    resp = WikiAPI.get(u)
    proc(resp)

    while resp.get('continue') and resp['continue'].get('rvcontinue'):
        resp = WikiAPI.get(u, {'rvcontinue': resp['continue']['rvcontinue']})
        proc(resp)

    return revs


def process_article(article: Article):
    print('\n', '-' * 6)
    print('processing "{}"'.format(article.id_))

    # get unique contributor
    uniq_con = get_contributors(article.id_)
    print(uniq_con)

    # get user revisions
    rvs = get_revision(article.id_)
    print()




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

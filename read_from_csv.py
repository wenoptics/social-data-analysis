import csv
import requests

from WikiComponents import Article

base_url = "https://en.wikipedia.org/w/"


def get_contributors(article_id):
    # todo Use combined query makes more efficient.
    _url = "api.php?action=query&titles={article_id}&prop=contributors&format=json"
    u = (base_url + _url).format(article_id=article_id)
    req = requests.get(u)
    req = req.json()
    pg = req['query']['pages']
    if len(pg) != 1:
        print("[W] len(pg) != 1")
    first = list(pg.keys())[0]
    first = pg[first]
    n_contributers_a = first['anoncontributors']
    n_contributers = len(first['contributors'])
    return {'anoncontributors': n_contributers_a, 'contributors': n_contributers}


def process_article(article_id: str):
    # get unique contributor
    get_contributors(article_id)


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

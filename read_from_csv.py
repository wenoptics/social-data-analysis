import csv
import requests

base_url = "https://en.wikipedia.org/w/"


def get_contributors(article_id):
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


with open("data/articles.csv") as csvfile:
    sr = csv.reader(csvfile)
    # r2 = list(sr)[2]
    # print(r2)
    sr = list(sr)
    for row in sr[1:]:
        article_id = row[1]
        article_quality = row[2]
        print('[{}] Article: {}'.format(article_quality, article_id))
        c = get_contributors(article_id)
        print(c)
        print('')


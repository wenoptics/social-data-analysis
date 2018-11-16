import json

from dateutil.parser import parse as dtparse
import requests

from WikiComponents import Article, WikiAPI, WikiBrowser
from helper import read_csv, calc_freq, is_bot_user, get_first_query_page


def get_contributors(article_id):
    # todo Use combined query makes more efficient.
    _url = "api.php?action=query&titles={article_id}&prop=contributors"
    resp = WikiAPI.get(_url.format(article_id=article_id))
    first = get_first_query_page(resp)
    n_contributers_a = first.get('anoncontributors')
    n_contributers = len(first['contributors'])
    return {'anoncontributors': n_contributers_a, 'contributors': first['contributors']}


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
            uid = rv.get('userid')
            if not uid:
                continue
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
    overall_edit_timestamp = []
    overall_edit_nonbot_timestamp = []
    for editor in dict_rev_info.values():
        is_bot = is_bot_user(editor[0]['user'], editor[0].get('userid'))
        for rv in editor:
            ts = rv.get('timestamp')
            ts = dtparse(ts).timestamp()
            rv['timestamp_parsed'] = ts
            overall_edit_timestamp.append(ts)
            if not is_bot:
                overall_edit_nonbot_timestamp.append(ts)

    freq_overall = calc_freq(overall_edit_timestamp)

    freq_per_editor = {}
    # edit freq per editor
    for uid, revisions in dict_rev_info.items():
        freq_per_editor[uid] = calc_freq([rv['timestamp_parsed'] for rv in revisions])


def count_talk_posts(article_id):
    html_root = WikiBrowser.get_talk_page(article_id)
    return len(html_root.find('div', id='bodyContent').find_all('h2'))


def num_editor_talk(article_id):
    # Use an API provided by XTools Wiki-Project
    _url = 'https://xtools.wmflabs.org/api/page/articleinfo/en.wikipedia.org/Talk:{article_id}'
    resp = requests.get(_url.format(article_id=article_id)).json()
    return resp['editors']


dataset = {}


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

    # persistent the data
    current_data = {
        'article_id': article.id_,
        'grade': article.grade,
        'unique_contributors': uniq_con,
        'revision_info': rvs,
        'n_talk_post': ctp,
        'n_editor_post': etp
    }
    dataset[article.id_] = current_data

    if len(dataset) % 10 == 0:
        save_data()


def save_data():
    save_file = 'data/saved_dataset.json'
    with open(save_file, 'w') as wfile:
        wfile.write(json.dumps(dataset))
    print('file saved to', save_file)


if __name__ == '__main__':
    article_list = read_csv("data/articles.csv",
                            lambda row: Article(id_=row[1], grade=row[2]))

    # Group those `good` and `not-so-good` articles
    groupGood = list(filter(lambda i: i.grade in ['A', 'FA', 'GA'], article_list))
    groupNSGood = list(filter(lambda i: i.grade in ['C', 'Start'], article_list))

    print('groupGood: n =', len(groupGood))
    print('groupNSGood: n =', len(groupNSGood))

    for i in groupGood:  # groupNSGood:
        try:
            process_article(i)
        except Exception as e:
            print('[E]', str(e))
    save_data()


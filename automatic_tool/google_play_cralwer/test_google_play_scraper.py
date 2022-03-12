import ssl
import sys
import traceback
from time import sleep

from google_play_scraper import Sort, reviews
from google_play_scraper import app
from google_play_scraper.exceptions import *
from pymongo import MongoClient

from pool import CountingProcessPool

ssl._create_default_https_context = ssl._create_unverified_context

client = MongoClient(host='localhost', port=27017)
db = client['GooglePlayReview']

app_col = db['app_info']
rev_col = db['app_review']


def insert_with_update(col, key, doc):
    col.update_one(key, {'$set': doc}, upsert=True)


def insert_app(col, app_doc):
    key = {'appId': app_doc['appId']}
    insert_with_update(col, key, app_doc)


def insert_rev(col, rev_doc):
    key = {'reviewId': rev_doc['reviewId']}
    insert_with_update(col, key, rev_doc)


def get_reviews(pkg='wsj.reader_sp', ct=None):
    info = app(
        pkg,
        lang='en',  # defaults to 'en'
        country='us'  # defaults to 'us'
    )

    review_list, continuation_token = reviews(
        pkg,
        lang='en',  # defaults to 'en'
        country='us',  # defaults to 'us'
        sort=Sort.MOST_RELEVANT,  # defaults to Sort.MOST_RELEVANT
        count=1000,  # defaults to 100
        # filter_score_with=5,  # defaults to None(means all score)
        continuation_token=ct
    )

    # If you pass `continuation_token` as an argument to the reviews function at this point,
    # it will crawl the items after 3 review items.

    # review_list, _ = reviews(
    #     'com.fantome.penguinisle',
    #     continuation_token=continuation_token # defaults to None(load from the beginning)
    # )

    return info, review_list, continuation_token


def crawl_app(package):

    doc = rev_col.find_one({
        'score': {"$ne": 5},
        'appId': package
    })
    if doc is not None:
        return

    print("crawling reviews of {}...".format(package))

    info, review_list, _ = get_reviews(package)

    insert_app(app_col, info)
    for rev in review_list:
        rev['appId'] = info['appId']
        insert_rev(rev_col, rev)


def crawl_app_with_catch(package):
    for i in range(5):
        try:
            print("{} {} try".format(package, i + 1))
            crawl_app(package)
            break
        except IndexError:
            sys.stderr.write('index error\n')
            break
        except NotFoundError:
            sys.stderr.write('not found\n')
            break
        except Exception as ex:
            exc_type, exc_value, exc_traceback_obj = sys.exc_info()
            traceback.print_tb(exc_traceback_obj)
            print("wrong!!", ex)
            sleep(60)


def main():
    f = open('./app_list.txt')
    # for line in f:
    #     crawl_app_with_catch(line[:-5])

    with CountingProcessPool(8) as pool:
        rs = [pool.apply_async(crawl_app_with_catch, (line[:-5],)) for line in f]
        pool.execute()

    f.close()


if __name__ == '__main__':
    main()

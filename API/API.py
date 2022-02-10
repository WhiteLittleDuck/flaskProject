from flask import Flask, redirect, url_for, send_file, send_from_directory, make_response
from flask import request
import os
from flask import render_template
import json
from pymongo import MongoClient
from operator import itemgetter

client = MongoClient(
    'mongodb://hyr-user:0380fade-e2c4-4966-bcbd-aa0021e93e06@10.20.38.233:27072/?authSource=hyr-project&readPreference=primary&appname=MongoDB%20Compass&ssl=false')
db = client['hyr-project']

# working
app_col = db['app_info_all']
rev_col = db['app_review_keyword_filtered']


# sub_method
def app_rank_info(order, page):
    sort_rule = ""
    # count
    if order == 0:
        sort_rule = "ui_cnt"
    # positive rate
    elif order == 1:
        sort_rule = "ui_pos_rate"
    # negative rate
    elif order == 2:
        sort_rule = "ui_neg_rate"
    # UI rate
    elif order == 3:
        sort_rule = "ui_rate"

    page_start = 10 * page - 9
    page_end = page * 10
    counter = 0
    app_list = []
    pointer = 0

    for c in app_col.find().sort(sort_rule, -1):
        counter += 1
        if counter < page_start or counter > page_end:
            continue
        app_list.append(dict())
        app_list[pointer]['name'] = c['title']
        app_list[pointer]['total'] = c['installs']
        app_list[pointer]['positive'] = c['ui_pos_cnt']
        app_list[pointer]['negative'] = c['ui_neg_cnt']
        app_list[pointer]['rate'] = str(round(c['ui_pos_rate'] * 100, 2))
        app_list[pointer]['UIrate'] = str(round(c['ui_rate'] * 100, 2))
        app_list[pointer]['id'] = c['appId']
        app_list[pointer]['rank'] = pointer
        pointer += 1
    return app_list


def keyword_rank_info(order, page):
    sort_rule = ""
    # count
    if order == 0:
        sort_rule = "cnt"
    # positive rate
    elif order == 1:
        sort_rule = "pos_rate"
    # negative rate
    elif order == 2:
        sort_rule = "neg_rate"
    # UI rate
    elif order == 3:
        sort_rule = "ui_rate"

    with open('API/keywords_info.json') as f:
        keyword_json = json.loads(f.read())
    sorted_keywords = sorted(keyword_json, key=itemgetter(sort_rule), reverse=True)

    keyword_list = []
    page_start = 10 * page - 9
    page_end = page * 10
    pointer = 0
    counter = 0

    for c in sorted_keywords:
        counter += 1
        if counter < page_start or counter > page_end:
            continue
        keyword_list.append(dict())
        keyword_list[pointer]['name'] = c['word']
        keyword_list[pointer]['total'] = c['all_cnt']
        keyword_list[pointer]['positive'] = c['pos_cnt']
        keyword_list[pointer]['negative'] = c['neg_cnt']
        keyword_list[pointer]['rate'] = str(round(c['pos_rate'] * 100, 2))
        keyword_list[pointer]['UIrate'] = str(round(c['ui_rate'] * 100, 2))
        keyword_list[pointer]['id'] = c['id']
        keyword_list[pointer]['rank'] = pointer
        pointer += 1
    return keyword_list


# 1.2.1
def rank_info(order, page):
    json_data_app = app_rank_info(order, page)
    json_data_keyword = keyword_rank_info(order, page)
    json_data = dict()
    json_data['app'] = json_data_app
    json_data['key'] = json_data_keyword

    json_meta = dict()
    json_meta['msg'] = 'success'
    json_meta['status'] = 200
    dict_json = dict()
    dict_json['data'] = json_data
    dict_json['meta'] = json_meta
    return dict_json
    # file = open("example.json", 'w')
    # file.write(json.dumps(dict_json))


# if __name__ == '__main__':
#     request = [1, 2]
#     order = request[0]
#     page = request[1]
#     rank_info(order, page)

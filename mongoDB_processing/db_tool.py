import pymongo
import json
import random
import operator
from bson.objectid import ObjectId

class DBTool():
    def __init__(self, addr):
        # brew service start mongodb-community
        self.client = pymongo.MongoClient(host='localhost', port=27017)
        self.db = self.client['review-analysis']
        # 0: app_info_all, 1: keyword_info_all
        self.collections=[self.db['app_info_all'], self.db['keyword_info_all'],self.db['app_review_keyword_filtered']]
        self.index_list = ['ui_cnt', 'ui_pos_rate', 'ui_neg_rate', 'ui_rate']

        self.app_rank_info=[[]for i in range(len(self.index_list))]
        self.key_rank_info = [[] for i in range(len(self.index_list))]
        for i in range(len(self.index_list)):
            with open(addr+'app_rank_' + self.index_list[i], 'r', encoding='utf-8') as fin:
                self.app_rank_info[i]=json.load(fin)
            with open(addr+'key_rank_' + self.index_list[i], 'r', encoding='utf-8') as fin:
                self.key_rank_info[i]=json.load(fin)

    # user use getRankList() method to get sorted app and sorted keyword list with attribute 'rank'
    def sort_to_rank(self, index, type=0):
        rank_list = []
        cnt = 0
        extract_index = ['appId', 'ui_cnt', 'ui_pos_cnt', 'ui_neg_cnt', 'ui_pos_rate', 'ui_rate']
        for app in self.collections[type].find().sort(index, pymongo.DESCENDING):
            cnt += 1
            extracted_app = {}
            for index in extract_index:
                extracted_app[index] = app[index]
            extracted_app['rank'] = cnt
            rank_list.append(extracted_app)
        return rank_list

    # write the sorted rank into current_data record
    def write_rank_record_after_sort(self):
        for index in self.index_list:
            with open('current_data/app_rank_' + index, 'w', encoding='utf-8') as fout:
                json.dump(self.sort_to_rank(index, 0), fout)
            with open('current_data/key_rank_' + index, 'w', encoding='utf-8') as fout:
                json.dump(self.sort_to_rank(index, 1), fout)

    # read out api request for dashboard app/keyword rank
    def read_rank_record(self,page=1,order=0):
        # get app list
        if page * 10 - 1 < len(self.app_rank_info[order]):
            app_list = self.app_rank_info[order][(page - 1) * 10:page * 10]
        else:
            app_list = self.app_rank_info[order][(page - 1) * 10:]

        # get key list
        if page * 10 - 1 < len(self.app_rank_info[order]):
            key_list = self.key_rank_info[order][(page - 1) * 10:page * 10]
        else:
            key_list = self.key_rank_info[order][(page - 1) * 10:]
        datalist = {'app': app_list, 'key': key_list}
        return {'data': datalist, 'meta': {'msg': "success", 'status': 200}}

    # find app with appId and extract info
    def find_app_info(self, appId):
        app=self.collections[0].find_one({'appId': appId})
        if app == None:
            return {"data": {}, "meta": { "msg": "NOT FOUND", "status": 404}}
        extract_index = ['appId', 'ui_cnt', 'ui_pos_cnt', 'ui_neg_cnt', 'reviews',
                         'descriptionHTML', 'score', 'ui_pos_rate', 'ui_rate', 'url', 'icon', 'version_pos_rate']
        info={}
        for index in extract_index:
            # print(index)
            info[index]=app[index]
        info['name']=appId.split('.')[-1]
        version_pos_rate=app['version_pos_rate']
        version_cnt=app['version_cnt']
        version_pos_cnt=app['version_pos_cnt']
        version_neg_cnt=app['version_neg_cnt']

        return {'data': {'info': info,
                         'version_pos_rate':version_pos_rate,
                         'version_cnt': version_cnt,
                         'version_pos_cnt': version_pos_cnt,
                         'version_neg_cnt': version_neg_cnt
                         }, "meta": {"msg": "success","status": 200}}

    #find keyword with keyword name(appId) return info
    def find_keyword_info(self, keyid):
        keyword=self.collections[1].find_one({'appId': keyid})
        if keyword == None:
            return {"data": {}, "meta": { "msg": "NOT FOUND", "status": 404}}
        extract_index=['ui_cnt', 'ui_pos_cnt', 'ui_neg_cnt', 'ui_pos_rate']
        info={'keyid': keyword['appId']}
        for index in extract_index:
            info[index]=keyword[index]
        return {'data':{'info':info},"meta": {"msg": "success","status": 200}}


    # pick an app example of review
    def get_app_example(self, appId, sentiment):
        condition =  {'sentiment': sentiment, 'appId': appId}
        count = self.collections[2].count_documents(condition)
        if count == 0:
            return {"data": {},"meta": {"msg": "NOT FOUND","status": 404}}
        review = self.collections[2].find(condition)[random.randint(0,count-1)]

        data={}
        data['content']=review['content']
        data['version']=review['reviewCreatedVersion']
        data['score']=review['score']
        return {'data':data,"meta": {"msg": "success","status": 200}}

    def get_keyword_example(self, keyid, type):
        keyword = self.collections[1].find_one({'appId': keyid})
        if type == 1:
            sentiment = 'posExample'
        else:
            sentiment = 'negExample'
        count = len(keyword[sentiment])
        if count == 0:
            return {"data": {},"meta": {"msg": "NOT FOUND","status": 404}}
        data = keyword[sentiment][random.randint(0,count-1)]
        return {'data':data,"meta": {"msg": "success","status": 200}}

    # get an app's keyword rank
    def get_app_keyword_rank(self, appId, order):
        orderList=['cnt','pos_cnt', 'neg_cnt', 'pos_rate', 'neg_rate']
        app=self.collections[0].find_one({'appId': appId})
        sortedList=sorted(app['keyword_info'],key=operator.itemgetter(orderList[order]), reverse=True)
        info=[]
        for i in range(min(7,len(sortedList))):
            sortedList[i]['rank']=i+1
            info.append(sortedList[i])
        return {'data':{'info':info}, "meta": {"msg": "success", "status": 200}}

    # get a keyword's app rank
    def get_keyword_app_rank(self, keyid, order):
        orderList = ['app_rank_cnt', 'app_rank_pos_cnt', 'app_rank_neg_cnt', 'app_rank_pos_rate', 'app_rank_neg_rate']
        keyword = self.collections[1].find_one({'appId': keyid})
        if keyword == None:
            return {"data": {},"meta": {"msg": "NOT FOUND","status": 404}}
        return {'data':{'info':keyword[orderList[order]]},"meta": {"msg": "success","status": 200}}
# appsort=AppSort()
# for app in appsort.getRankList('ui_cnt'):
#     print(app)

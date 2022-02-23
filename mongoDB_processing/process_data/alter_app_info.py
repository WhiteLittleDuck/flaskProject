import pymongo
import operator

# connect db
client = pymongo.MongoClient(host='localhost', port=27017)
db = client['review-analysis']
app_info = db['app_info_all']
app_review = db['app_review_all']


# sort version number from low to high version:
def sort_versions():
    for app in app_info.find():
        app['version_pos_rate']=sorted(app['version_pos_rate'], key=operator.itemgetter(0))
        app['version_cnt']=sorted(app['version_cnt'], key=operator.itemgetter(0))
        app['version_pos_cnt']=sorted(app['version_pos_cnt'], key=operator.itemgetter(0))
        app['version_neg_cnt']=sorted(app['version_neg_cnt'], key=operator.itemgetter(0))
        result = app_info.update_one({'appId': app['appId']},{'$set':app})

# turn the attribute keyword_info in app_info_all (keyword_info{alignment:{},clarity:{}})in to list of dictionary
def turn_key_info_attr_from_dic_to_list():
    for app in app_info.find():
        keyword_info = app['keyword_info']
        list = []
        for key in keyword_info:
            dic = keyword_info[key]
            dic['name']=key
            if dic['cnt']>0:
                list.append(dic)
            app['keyword_info'] = list
        app_info.update_one({'appId': app['appId']},{'$set': app})
        # list=sorted(list,key=operator.itemgetter('cnt'), reverse=True)
if __name__ == '__main__':
    # sort_versions()
    turn_key_info_attr_from_dic_to_list()
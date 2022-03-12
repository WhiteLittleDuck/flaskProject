import pymongo
import operator
import re


# connect db
client = pymongo.MongoClient(host='localhost', port=27017)
db = client['review-analysis']
app_info = db['app_info_all']
app_review = db['app_review_all']
keyword_info = db['keyword_info_all']
filtered_review = db['app_review_keyword_filtered']


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

# add review content that contain keyword as a list in keyword_info_all collection
def add_review_example_in_keyword_info():
    for k in keyword_info.find():
        pos_reviews = filtered_review.find({'content': {'$regex': '.*' + k['appId'] + '.*'}, 'sentiment': 1})
        neg_reviews = filtered_review.find({'content': {'$regex': '.*' + k['appId'] + '.*'}, 'sentiment': -1})
        k['posExample']=[]
        k['negExample']=[]
        cnt = 0
        for r in pos_reviews:
            if cnt>=20:
                break
            words = re.split('[^a-zA-Z]', r['content'])
            if k['appId'] in words or k['appId'].capitalize() in words:
                content=r['content'].replace(k['appId'], '<span style="font-weight:bold;font-style: italic; text-decoration: underline">'+k['appId']+'</span>')
                k['posExample'].append({'content':content, 'score':r['score'], 'appId': r['appId']})
                cnt+=1
        cnt = 0
        for r in neg_reviews:
            if cnt>=20:
                break
            words = re.split('[^a-zA-Z]', r['content'])
            if k['appId'] in words or k['appId'].capitalize() in words:
                content=r['content'].replace(k['appId'], '<span style="font-weight:bold; font-style: italic; text-decoration: underline">'+k['appId']+'</span>')
                k['negExample'].append({'content':content, 'score':r['score'], 'appId': r['appId']})
                cnt+=1
        keyword_info.update_one({'appId': k['appId']},{'$set': k})

def calculate_ui_ineach_app(): # todo 可以写一个O(1)的算法
    keyword_list=[]
    with open('keyword.txt','r',encoding='utf-8') as f:
        line = f.readline()
        while line:
            keyword_list.append(line.strip())
            # print(line.strip())
            line=f.readline()
    i = 0
    app_dic = {}
    for review in filtered_review.find():
        appId = review['appId']
        if appId not in app_dic:
            app_dic[appId] = {}
        words = re.split('[^a-zA-Z]', review['content'])
        for keyword in keyword_list:
            if keyword in words or keyword.capitalize() in words:
                if keyword not in app_dic[appId]:
                    app_dic[appId][keyword]={'name': keyword, 'cnt': 0, 'pos_cnt': 0, 'neg_cnt': 0, 'pos_rate': 0, 'neg_rate': 0}
                app_dic[appId][keyword]['cnt']+=1
                if review['sentiment'] == 1:
                    app_dic[appId][keyword]['pos_cnt']+=1
                if review['sentiment'] == -1:
                    app_dic[appId][keyword]['neg_cnt']+=1
        i+=1
        print(i)
    for appId in app_dic:
        for keyword in app_dic[appId]:
            app_dic[appId][keyword]['pos_rate']=app_dic[appId][keyword]['pos_cnt']/app_dic[appId][keyword]['cnt']
            app_dic[appId][keyword]['neg_rate']=app_dic[appId][keyword]['neg_cnt']/app_dic[appId][keyword]['cnt']

    for app in app_info.find():
        if app['appId'] not in app_dic:
            continue
        app['keyword_info']=app_dic[app['appId']]
        app_info.update_one({'appId': app['appId']}, {'$set': app})


def add_rank(list):
    r =1
    for dic in list:
        dic["rank"]=r
        r+=1
    return list
# write rank of App in keyword_info_all
def add_app_rank_list_in_keyword_info():
    key_dic={}
    for app in app_info.find():
        for k in app['keyword_info']:
            app['keyword_info'][k]['appId']=app['appId']
            if k not in key_dic:
                key_dic[k]=[]
            key_dic[k].append(app['keyword_info'][k])
    for key in key_dic:
        keyword_item = keyword_info.find_one({'appId':key})
        # print(key)
        # print(keyword_item['appId'])
        keyword_item['app_rank_cnt']=add_rank(sorted(key_dic[key], key=operator.itemgetter('cnt'),reverse=True)[:7])
        keyword_item['app_rank_pos_cnt'] = add_rank(sorted(key_dic[key], key=operator.itemgetter('pos_cnt'), reverse=True)[:7])
        keyword_item['app_rank_neg_cnt'] = add_rank(sorted(key_dic[key], key=operator.itemgetter('neg_cnt'), reverse=True)[:7])
        keyword_item['app_rank_pos_rate'] = add_rank(sorted(key_dic[key], key=operator.itemgetter('pos_rate'), reverse=True)[:7])
        keyword_item['app_rank_neg_rate'] = add_rank(sorted(key_dic[key], key=operator.itemgetter('neg_rate'), reverse=True)[:7])
        keyword_info.update_one({'appId': keyword_item['appId']},{'$set': keyword_item})

        # print('wireframe:')
        # if key == 'wireframe':
        #     for item in keyword_item['app_rank_cnt']:
        #         print(item)

    # only keyword 'wireframe not include!'
    k=keyword_info.find_one({'appId': 'wireframe'})
    k['app_rank_cnt']=[]
    k['app_rank_pos_cnt']=[]
    k['app_rank_neg_cnt']=[]
    k['app_rank_pos_rate']=[]
    k['app_rank_neg_rate']=[]
    keyword_info.update_one({'appId':'wireframe'},{'$set':k})
    for keyword in keyword_info.find({'app_rank_cnt': {'$exists': False}}):
        print(keyword['appId']+' not exist!')


if __name__ == '__main__':
    # sort_versions()
    # turn_key_info_attr_from_dic_to_list()
    add_review_example_in_keyword_info()
    # calculate_ui_ineach_app()
    # add_app_rank_list_in_keyword_info()
    print('done')

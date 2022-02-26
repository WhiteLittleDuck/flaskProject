import pymongo
import operator

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
            content=r['content'].replace(k['appId'], '<span style="font-weight:bold">'+k['appId']+'</span>')
            k['posExample'].append({'content':content, 'score':r['score'], 'appId': r['appId']})
            cnt+=1
        cnt = 0
        for r in neg_reviews:
            if cnt>=20:
                break
            content=r['content'].replace(k['appId'], '<span style="font-weight:bold">'+k['appId']+'</span>')

            k['negExample'].append({'content':content, 'score':r['score'], 'appId': r['appId']})
            cnt+=1
        keyword_info.update_one({'appId': k['appId']},{'$set': k})

def calculate_ui_ineach_app():
    keyword_list=[]
    with open('keyword.txt','r',encoding='utf-8') as f:
        line = f.readline()
        while line:
            keyword_list.append(line.strip())
            # print(line.strip())
            line=f.readline()
    i = 0
    for app in app_info.find():
        app_keyword_info=[]
        for keyword in keyword_list:
            cnt=filtered_review.count_documents({'appId': app['appId'], 'content': {'$regex': '.*'+keyword+'.*'}})
            pos_cnt=filtered_review.count_documents({'appId': app['appId'], 'sentiment':1,'content': {'$regex': '.*'+keyword+'.*'}})
            neg_cnt=filtered_review.count_documents({'appId': app['appId'], 'sentiment':-1,'content': {'$regex': '.*'+keyword+'.*'}})
            if cnt == 0:
                continue
            else:
                pos_rate=pos_cnt/cnt
                neg_rate=neg_cnt/cnt
            app_keyword_info.append(
                {'name': keyword, 'cnt': cnt, 'pos_cnt': pos_cnt, 'neg_cnt': neg_cnt, 'pos_rate': pos_rate, 'neg_rate': neg_rate})
        app['keyword_info']=app_keyword_info
        app_info.update_one({'appId': app['appId']},{'$set': app})
        i+=1
        print(str(i)+'/2941')

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
            k['appId']=app['appId']
            if k['name'] not in key_dic:
                key_dic[k['name']]=[]
            key_dic[k['name']].append(k)
    for key in key_dic:
        keyword_item = keyword_info.find_one({'appId':key})
        # print(key)
        # print(keyword_item['appId'])
        keyword_item['app_rank_cnt']=add_rank(sorted(key_dic[key], key=operator.itemgetter('cnt'),reverse=True))[:7]
        keyword_item['app_rank_pos_cnt'] = add_rank(sorted(key_dic[key], key=operator.itemgetter('pos_cnt'), reverse=True))[:7]
        keyword_item['app_rank_neg_cnt'] = add_rank(sorted(key_dic[key], key=operator.itemgetter('neg_cnt'), reverse=True))[:7]
        keyword_item['app_rank_pos_rate'] = add_rank(sorted(key_dic[key], key=operator.itemgetter('pos_rate'), reverse=True))[:7]
        keyword_item['app_rank_neg_rate'] = add_rank(sorted(key_dic[key], key=operator.itemgetter('neg_rate'), reverse=True))[:7]
        # keyword_info.update_one({'appId': keyword_item['appId']},{'$set': keyword_item})

        print('design:')
        for item in keyword_item['app_rank_pos_rate']:
            print(item)

    # only keyword 'wireframe not include!'
    k=keyword_info.find_one({'appId': 'wireframe'})
    k['app_rank_cnt']=[]
    k['app_rank_pos_cnt']=[]
    k['app_rank_neg_cnt']=[]
    k['app_rank_pos_rate']=[]
    k['app_rank_neg_rate']=[]
    keyword_info.update_one({'appId':'wireframe'},{'$set':k})


if __name__ == '__main__':
    # sort_versions()
    # turn_key_info_attr_from_dic_to_list()
    # add_review_example_in_keyword_info()
    calculate_ui_ineach_app()
    # add_app_rank_list_in_keyword_info()
    print('done')

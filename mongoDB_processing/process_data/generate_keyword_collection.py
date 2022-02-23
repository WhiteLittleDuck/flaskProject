import json
import pymongo
# name(appId), ui_cnt, ui_pos_cnt, ui_neg_cnt, ui_pos_rate, ui_neg_rate， pos_example, neg_example

keyword=[]
with open('keyword.txt', 'r', encoding='utf-8') as f_key:
    line = f_key.readline()
    while line:
        keyword.append({'appId':line.strip()})
        line=f_key.readline()

client = pymongo.MongoClient(host='localhost', port=27017)
db = client['review-analysis']
filtered_review_col = db['app_review_keyword_filtered']


# there are 210304 reviews containing UI keywords,
# 101738 UI related reviews filtered out by bert,
# from 3404600 reviews in total
for k in keyword:
    key_name=k['appId'] # name
    k['ui_cnt']=filtered_review_col.count_documents({'content': {'$regex': '.*'+key_name+'.*'}})

    k['ui_pos_cnt']=filtered_review_col.count_documents({'content': {'$regex': '.*'+key_name+'.*'},'sentiment':1})
    pos_review = filtered_review_col.find({'content': {'$regex': '.*'+key_name+'.*'},'sentiment':1})
    k['pos_example_comment']=[]
    k['pos_example_appId']=[]
    k['pos_example_score']=[]
    for r in pos_review.limit(5):
        k['pos_example_comment'].append(r['content'])
        k['pos_example_appId'].append(r['appId'])
        k['pos_example_score'].append(r['score'])

    k['ui_neg_cnt']=filtered_review_col.count_documents({'content': {'$regex': '.*'+key_name+'.*'},'sentiment':-1})
    neg_review = filtered_review_col.find({'content': {'$regex': '.*'+key_name+'.*'},'sentiment':-1})
    k['neg_example_comment']=[]
    k['neg_example_appId']=[]
    k['neg_example_score']=[]
    for r in neg_review.limit(5):
        k['neg_example_comment'].append(r['content'])
        k['neg_example_appId'].append(r['appId'])
        k['neg_example_score'].append(r['score'])

    if k['ui_cnt']==0:
        k['ui_pos_rate'] = 0
        k['ui_neg_rate'] = 0
        print('keyword:'+k['appId']+' has no review in it')
    else:
        k['ui_pos_rate']=k['ui_pos_cnt']/k['ui_cnt']
        k['ui_neg_rate']=1-k['ui_pos_rate']
    k['ui_rate']=1

# print(type(keyword))
# for k in keyword:
#     print(k)
# print(type(keyword[0]))
with open('keyword_info_all.json','w',encoding='utf-8') as fout:
    json.dump(keyword,fout)

from pymongo import MongoClient

client = MongoClient('mongodb://10.20.16.3:27017')
db = client['GooglePlayReview']

rev_col = db['app_review']
for review in rev_col.find({"content": {"$regex": "button"}}):
    print(review['content'])

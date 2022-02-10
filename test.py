# import os
# print(type(os.getcwd()))
dic = {}
import json
with open('C:/Users/WhiteLittleDuck/Documents/WeChat Files/wxid_y2wm6lokgmf622/FileStorage/File/2021-05/app_info_all_512backup.json','r',encoding='utf-8') as f:
    content = f.read()
    list = json.loads(content)
    for e in list:
        name = e["title"]
        if name not in dic:
            dic[name]=1
        else :
            dic[name]+=1
for d in dic:
    if dic[d]>1:
        print(d+":"+str(dic[d]))
        # if '_' in e["title"]:
        #     print('!!!!!!!!!!!!!!!!!!!!!!!!!!')
        # print(e["title"])
    # print(list[0]["title"])

    # print(type())
from flask import Flask, redirect, url_for, send_from_directory, make_response
from flask import request
import os
from flask import render_template
from mongoDB_processing.db_tool import DBTool
import json
# TODO
# 1. 改 app / keyword rank 3个 rank pos/neg rate 排序权重
# 2. keyword: sentiment 逐句分析，keyword +-，app: 整个分析
# 3. app example 设定某一版本的查询
# 4. automatic tool
# 5. 整理download 文档
# 6. 答辩的时候专注于 "这个对人有什么帮助"， 下载button好评率最低的app截图证明数据准确性
app = Flask(__name__)
# 0: count 1: pos rank 2: neg rate 3: UI rate
db_tool=DBTool()

@app.route('/')
def hello_world():
    return 'Hello World!'


# Dashboard(Rank): get app and key dashboard rank info
@app.route('/api/rank')
def getRankInfo():
    print("/api/app:" + str(request.args))
    order = int(request.args.get("order"))
    page = int(request.args.get("page"))
    return db_tool.get_rank(page,order)


@app.route('/api/app')
def getAppInfo():
    print("/api/app:" + str(request.args))
    return db_tool.get_app_info(request.args.get("id"))


@app.route("/api/keyword")
def getKeywordInfo():
    print("/api/keywords:" + str(request.args))
    return db_tool.get_keyword_info(request.args.get("id"))


@app.route("/api/app/switch")
def getAppSwitch():
    print("/api/app/switch" + str(request.args))
    return db_tool.get_app_example(request.args.get('id'), int(request.args.get('type')))


@app.route("/api/keyword/switch")
def getKeywordSwitch():
    print("/api/app/switch" + str(request.args))
    return db_tool.get_keyword_example(request.args.get('id'),int(request.args.get('type')))


@app.route('/api/app/rank')
def getAppKeywordRank():
    print("/api/app/rank:" + str(request.args))
    return db_tool.get_app_keyword_rank(request.args.get("id"), int(request.args.get("order")))


@app.route("/api/keyword/rank")
def getKeywordAppRank():
    print("/api/keyword/rank:" + str(request.args))
    return db_tool.get_keyword_app_rank(request.args.get("id"), int(request.args.get("order")))


@app.route("/api/download")
def downloadFile():
    print("/api/download/app:" + str(request.args))
    filename = 'appReviewsFile.txt'
    directory = os.getcwd()  # current path
    # print(directory)
    response = make_response(send_from_directory(directory + '/response_test', filename, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(filename.encode().decode('latin-1'))
    return response


@app.route("/api/app/id", methods=['POST'])
def getAppID():
    name = str(request.get_data()).strip('b').strip("\'")
    print(name)
    if name == "aaa":  # length==0 没搜到
        filename = 'response_test/error.txt'
    elif name == 'bbb':  # length==1 exact match
        filename = 'response_test/app2.txt'
    else:  # lentgh>1 搜到好几个
        filename = 'response_test/AppID.txt'
    with open(filename) as f:
        content = f.read()
    return content


@app.route("/api/keyword/id", methods=['POST'])
def getKeyID():
    text = str(request.get_data()).strip('b').strip("\'")
    print(text)
    if text == "aaa":  # length==0 没搜到
        filename = 'response_test/error.txt'
    else:  # lentgh>1 搜到好几个
        filename = 'response_test/KeywordID.txt'
    with open(filename) as f:
        content = f.read()
    return content


@app.route("/api/new")
def newTask():
    id = request.args.get('id')
    email = request.args.get('email')
    print('/api/new:' + str(request.args))
    if id == "aaa":  # length==0 没搜到
        filename = 'response_test/newSuccess.txt'
    elif id == 'bbb':  # length==1 exact match
        filename = 'response_test/newExist.txt'
    else:  # lentgh>1 搜到好几个
        filename = 'response_test/newInvalid.txt'
    with open(filename) as f:
        content = f.read()
    return content


@app.route('/api/test', methods=['POST', 'GET'])
def test():
    if request.method == 'POST':
        print("POST")
    # print(request.form)
    # print(request.args)
    print(str(request.get_data()).strip('b').strip("\'"))
    # user = request.form['nm']
    return "great"
    # else:
    # get function: http://127.0.0.1:5000/login?nm=duck
    # user = request.args.get('nm')
    # return redirect(url_for('success',name = user))


# int para
@app.route('/blog/<int:postID>')
def show_blog(postID):
    return 'Blog Number %d' % postID


# float para
@app.route('/rev/<float:revNo>')
def revision(revNo):
    return 'Revision NUmber %f' % revNo


# redirect
@app.route('/admin')
def hello_admin():
    return 'Hello Admin'


@app.route('/guest/<guest>')
def hello_guest(guest):
    return 'Hello %s as Guest' % guest


@app.route('/user/<name>')
def hello_user(name):
    if name == 'admin':
        return redirect(url_for('hello_admin'))
    else:
        return redirect(url_for('hello_guest', guest=name))


# http function
# request: form 字典对象，单参数的值和对儿/ args ?后面的参数/cookies cookie的名字和字典对象/files 上传数据/method 当前请求的方法
@app.route('/success/<name>')
def success(name):
    return 'welcome %s' % name


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['nm']
        return redirect(url_for('success', name=user))
    else:
        # get function: http://127.0.0.1:5000/login?nm=duck
        user = request.args.get('nm')
        return redirect(url_for('success', name=user))


# flask model & connect to js
# @app.route('/render',methods=['POST'])
@app.route('/render')
def index():
    description = "White little duck's first model! "
    age = 21
    code = [5, 2, 0]
    info = {
        'name': 'Olivia',
        'age': 18
    }
    return render_template('hello.html',
                           my_str=description,
                           my_int=age,
                           # my_int= request.form['age'], #age,
                           my_arr=code,
                           my_dic=info
                           )


if __name__ == '__main__':
    app.debug = True
    app.run()
    app.run(debug=True)


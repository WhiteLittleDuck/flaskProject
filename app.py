from flask import Flask, redirect, url_for
from flask import request
from flask import render_template
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'
# string para
@app.route('/nice/<name>')
def nice(name):
    return 'Good Job %s!' % name
# int para
@app.route('/blog/<int:postID>')
def show_blog(postID):
    return 'Blog Number %d'% postID
# float para
@app.route('/rev/<float:revNo>')
def revision(revNo):
    return 'Revision NUmber %f' %  revNo

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
        return redirect(url_for('hello_guest',guest=name))

# http function
# request: form 字典对象，单参数的值和对儿/ args ?后面的参数/cookies cookie的名字和字典对象/files 上传数据/method 当前请求的方法
@app.route('/success/<name>')
def success(name):
    return 'welcome %s' % name
@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        user = request.form['nm']
        return redirect(url_for('success', name=user))
    else:
        # get function: http://127.0.0.1:5000/login?nm=duck
        user = request.args.get('nm')
        return redirect(url_for('success',name = user))


# flask model & connect to js
# @app.route('/render',methods=['POST'])
@app.route('/render')
def index():
    description = "White little duck's first model! "
    age = 21
    code = [5,2,0]
    info = {
        'name':'Olivia',
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
    app.add_url_rule('/','nice',nice)
    app.debug = True
    app.run()
    app.run(debug = True)

# -*- coding: utf-8 -*-
from flask import Flask, request, render_template
from flask import g, redirect, url_for, session
import pymongo
import datetime
from bson.objectid import ObjectId
from functools import wraps


app = Flask(__name__)

app.debug = True
app.secret_key = 'some_secret_yiyu'
app.config['USERNAME'] = 'admin'
app.config['PASSWORD'] = '123456'


#在请求前获得mongodb链接 g.db
@app.before_request
def get_connect_db():
    g.db = pymongo.Connection().yiyu


#需要登录请求函数
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

#使用g.user
@app.before_request
def get_current_user():
    g.user = None
    if app.config['USERNAME'] in session:
        g.user = {}
        g.user[app.config['USERNAME']] = app.config['USERNAME']


#主页
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        start = request.args.get('start', '1')
        start = int(start)
        k = g.db.yiyu.find()
        count = k.count()/10
        if k.count()/10.0 != count:
            count += 1
        yiyus = k.sort("post_time", -1).limit(10).skip((start-1)*10)
        return render_template('view.html',yiyus=yiyus,
                count=count,start=start)


#长文预览
@app.route('/xianyan', methods=['GET', 'POST'])
def xianyan():
    if request.method == 'GET':
        start = request.args.get('start', '1')
        start = int(start)
        k = g.db.yiyu.find({"title" :{"$ne": ""}})
        count = k.count()/10
        if k.count()/10.0 != count:
            count += 1
            yus = k.sort("post_time", -1).limit(10).skip((start-1)*10)
        return render_template('xianyan.html',yiyus=yus,
                count=count,start=start)

#端言预览
@app.route('/suiyu', methods=['GET', 'POST'])
def suiyu():
    if request.method == 'GET':
        start = request.args.get('start', '1')
        start = int(start)
        k = g.db.yiyu.find({"title":""})
        count = k.count()/10
        if k.count()/10.0 != count:
            count += 1
        yiyus = k.sort("post_time", -1).limit(10).skip((start-1)*10)
        return render_template('suiyu.html',yiyus=yiyus,
                count=count,start=start)

#管理
@app.route('/manage', methods=['GET', 'POST'])
@login_required
def manage():
    if request.method == 'GET':
        start = request.args.get('start', '1')
        start = int(start)
        k = g.db.yiyu.find()
        count = k.count()/10
        yiyus = k.sort("post_time", -1).limit(10).skip((start-1)*10)
        count += 1
        return render_template('manage.html',yiyus=yiyus,
                count=count,start=start)


#发布长文
@app.route('/yanxian', methods=['GET', 'POST'])
@login_required
def yanxian():
    if request.method == 'GET':
        return render_template('yanxian.html')
    if request.method == 'POST':
        yiyu = g.db.yiyu
        title = request.form.get('title','')
        content = request.form.get('editorValue','')
        text = request.form.get('text','')
        one_yanxian = [{"title": "%s" % title,
                     "post_time": datetime.datetime.utcnow(),
                     "content": content,
                     "text": text, }]
        yiyu.insert(one_yanxian)
        return redirect(url_for('index'))

#发布短文
@app.route('/yusui', methods=['GET', 'POST'])
@login_required
def yusui():
    if request.method == 'GET':
        return render_template('yusui.html')
    if request.method == 'POST':
        yiyu = g.db.yiyu
        title = ''
        content = request.form.get('content','')
        text = content
        one_yusui = [{"title": "%s" % title,
            "post_time": datetime.datetime.utcnow(),
            "content": content,
            "text": text, }]
        yiyu.insert(one_yusui)
        return redirect(url_for('index'))

#删除
@app.route('/delete/<_id>', methods=['GET', 'POST'])
@login_required
def delete(_id):
    if request.method == 'GET':
        g.db.yiyu.remove({"_id": ObjectId(_id)})
        return redirect("/")


#编辑
@app.route('/edit/<_id>', methods=['GET', 'POST'])
@login_required
def edit(_id):
    yiyu = g.db.yiyu
    if request.method == 'GET':
        one_yiyu = yiyu.find_one({"_id": ObjectId(_id)})
        return render_template("edit.html", one_yiyu=one_yiyu, _id=_id)
    if request.method == 'POST':
        title = request.form.get('title','')
        content = request.form.get('editorValue','')
        text = request.form.get('text','')
        yiyu.update({"_id": ObjectId(_id)},
                    {"$set": {"title": title,
                              "content": content,
                              "text": text }})
        return redirect('/show/%s' % _id)


#长文全文
@app.route('/show/<_id>')
def show(_id):
    one_yiyu = g.db.yiyu.find_one({"_id": ObjectId(_id)})
    return render_template("show.html", one_yiyu=one_yiyu)


#登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    next_url = request.args.get('next')
    if request.method == 'POST':
        if request.form['name'] != app.config['USERNAME']:
            error = u'用户名不正确！'
        elif request.form['pwd'] != app.config['PASSWORD']:
            error = u'密码不正确！'
        else:
            session[app.config['USERNAME']] = app.config['USERNAME']
            if next_url is None or next_url == 'None':
                return redirect('/')
            return redirect(next_url)
    return render_template('login.html', error=error, next_url=next_url)


#注销
@app.route('/logout')
def logout():
    session.pop(app.config['USERNAME'], None)
    return redirect('/')


#后院
@app.route('/backyard')
def backyard():
    return render_template("backyard.html")


#友链
@app.route('/friend-links')
def friend_links():
    return render_template("friend-links.html")


if __name__ == '__main__':
    app.run()

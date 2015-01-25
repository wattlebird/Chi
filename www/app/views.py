# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.cors import cross_origin
from app import app, db
from util import validateform
from data import qualified, similarlist, getsim

db.create_all()

@app.route('/')
def index():
    return render_template("index.html");

@app.route('/about/')
def about():
    return render_template("about.html")

@app.route('/similarity/', methods=['POST', 'GET'])
def similarity():
    if request.method=='POST':
        username = request.form.get('username')
        candidate = request.form.get('candidate')
        if not validateform(username):
            return render_template('similarity.html', error=u'请输入正确的用户名或时光机 URL！')
        
        username = validateform(username)
        if not candidate:
            return redirect(url_for('user', username=username))
        elif not validateform(candidate):
            return render_template('similarity.html', username=username, error=u'请输入正确的用户名或时光机 URL！')
        else:
            return redirect(url_for('user', username=username, candidate=validateform(candidate)))
    else:
        error=session.get("error")
        if error:
            session.pop("error")
        return render_template('similarity.html',error=error)




@app.route('/similarity/<username>')
@cross_origin()
def user(username):
    if not request.args.get('candidate'):
        if qualified(db, username)==1:
            simlist = similarlist(db, username);
            return render_template('single.html',username=username, simlist=simlist)
        elif qualified(db, username)==-1:
            session["error"]=u"啊，非常抱歉，我们找不到您的记录。有可能是由于我们数据库未及时更新或者您未注册 Bangumi。"
            return redirect(url_for('similarity'))
        else:
            return render_template('plz_favorite_request.html')
    else:
        candidate = request.args['candidate']
        if qualified(db, candidate)==1:
            sim = getsim(db, username, candidate)
            return render_template('couple.html',username=username, candidate=candidate, similarity=sim)
        elif qualified(db, candidate)==0:
            return render_template('couple.html',username=username, candidate=candidate, similarity=0)
        else:
            session["error"]=u"啊，非常抱歉，我们找不到您基(姬)友的记录。有可能是由于我们数据库未及时更新或者您未注册 Bangumi。"
            return redirect(url_for('similarity'))
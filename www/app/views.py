# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.cors import cross_origin
from app import app, cors
from util import validateform, getnickname
from connector import Controller

c=Controller()

@app.route('/')
def index():
    return render_template("index.html");

@app.route('/about/')
def about():
    return render_template("about.html")

@app.route('/similarity/', methods=['POST', 'GET'])
def similarity():
    if request.method=='POST':
        username = request.form.get('username').strip()
        candidate = request.form.get('candidate').strip()
        if not validateform(username):
            return render_template('similarity.html', error=u'请输入正确的用户名或时光机 URL！')
        
        username = validateform(username)
        if not candidate:
            if c.UserExist(username):
                return redirect(url_for('user', username=username))
            else
                return render_template('similarity.html', error=u'啊，非常抱歉，我们找不到您的记录。有可能是由于我们数据库未及时更新或者您未注册 Bangumi。')
        elif not validateform(candidate):
            return render_template('similarity.html', username=username, error=u'请输入正确的用户名或时光机 URL！')
        else:
            if c.UserExist(username) and c.UserExist(validateform(candidate)):
                return redirect(url_for('user', username=username, candidate=validateform(candidate)))
            else:
                return render_template('similarity.html', error=u'啊，非常抱歉，我们找不到您的记录。有可能是由于我们数据库未及时更新或者您未注册 Bangumi。')
    else:
        error=session.get("error")
        if error:
            session.pop("error")
        return render_template('similarity.html',error=error)




@app.route('/similarity/<username>')
@cross_origin()
def user(username):
    if not request.args.get('candidate'):
        if c.UserRecords(username):
            typ = request.args.get('type')
            if typ is None or not typ in ['anime','book','music','game','real']:
                typ='all'
            acl = request.args.get('activelevel')
            if acl is None or not acl in ['1','2','3']:
                acl='0'
            acl=int(acl)

            lst = c.GetTopRank(username, typ, acl)
            render_template('single.html',username=username, simlist=lst)
        else:
            render_template("single.html",username=username, simlist=[])

    else:
        candidate = request.args['candidate']
        if c.UserRecords(username) and c.UserRecords(candidate):
            typ = request.args.get('type')
            if typ is None or not typ in ['anime','book','music','game','real']:
                typ='all'

            ntotal = c.GetCount(typ)
            (nu,nc,sim,ru,rc) = c.GetCouple(username, candidate, typ)
            if sim==0:
                return render_template('couple.html',username=username, \
                candidate=candidate, \
                usernickname=nu, \
                couplenickname=nc, \
                similarity=sim, \
                rank=ru, rankpercent=round(ru*100./ntotal,2), \
                inverserank=rc, inverserankpercent=round(rc*100./ntotal,2))
            else:
                if sim>0:
                    feedbacklst = c.GetFeedback(username, candidate, typ)
                else:
                    feedbacklst = c.GetNegFeedback(username, candidate, typ)
                return render_template('couple.html',username=username, \
                candidate=candidate, \
                usernickname=nu, \
                couplenickname=nc, \
                similarity=sim, \
                rank=ru, rankpercent=round(ru*100./ntotal,2), \
                inverserank=rc, inverserankpercent=round(rc*100./ntotal,2), \
                feedbacklst=feedbacklst)




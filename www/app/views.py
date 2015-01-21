from flask import render_template, flash, redirect, session, url_for, request, g
from app import app, db
from util import validateform
from data import qualified, similarlist, getsim

db.create_all()
g['db']=db

@app.route('/chi')
def index():
    return render_template("index.html");

@app.route('/chi/about')
def about():
    return render_template("about.html")

@app.route('/chi/similarity', methods=['POST', 'GET'])
def similarity():
    if request.method=='POST':
        username = request.form.get('username')
        candidate = request.form.get('candidate')
        if not validateform(username):
            flash("You should specify your user name or url properly.")
            return render_template('similarity.html')
        
        username = validateform(username)
        if not candidate:
            redirect(url_for(user, username=username))
        elif not validateform(candidate):
            flash("You should specify the candidate user name or url properly.")
            return render_template('similarity.html', username=username)
        else:
            redirect(url_for(user, username=username, candidate=validateform(candidate)))
    else:
        return render_template('similarity.html')




@app.route('/chi/similarity/<username>')
def user(username):
    if not request.args.get('candidate'):
        if qualified(g['db'], username):
            simlist = similarlist(g['db'], username);
            return render_template('single.html',username=username, simlist=simlist)
        else:
            return render_template('unqualified.html', username=username)
    else:
        candidate = request.args['candidate']
        if qualified(candidate):
            sim = getsim(g['db'], username, candidate)
            return render_template('couple.html',username=username, candidate=candidate, similarity=sim)
        else:
            return render_template('couple.html',username=username, candidate=candidate, similarity=0)
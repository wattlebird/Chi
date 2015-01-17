from flask import render_template, flash, redirect, session, url_for, request, g
from app import app, db

@app.route('/chi')
def index():
    return render_template("index.html");

@app.route('/chi/about')
def about():
    return render_template("about.html")

@app.route('/chi/similarity', methods=['POST', 'GET'])
def similarity():
    return
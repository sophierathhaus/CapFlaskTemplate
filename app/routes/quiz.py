# These routes are an example of how to use data, forms and routes to create
# a forum where a posts and comments on those posts can be
# Created, Read, Updated or Deleted (CRUD)

#from django.shortcuts import render
from app import app, login
import mongoengine.errors
from flask import render_template, flash, redirect, url_for
from flask_login import current_user
from app.classes.data import Post, Comment
from app.classes.forms import PostForm, CommentForm
from flask_login import login_required
import datetime as dt

@app.route("/quiz")
def quiz():
    return render_template('quiz.html')

@app.route("/happy")
def happy():
    return render_template('happy.html')

@app.route("/sad")
def sad():
    return render_template('sad.html')


@app.route("/mad")
def mad():
    return render_template('mad.html')

@app.route("/tired")
def tired():
    return render_template('tired.html')

@app.route("/annoyed")
def annoyed():
    return render_template('annoyed.html')


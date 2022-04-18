from app import app
from flask import render_template

# This is for rendering the home page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/posts')
def posts():
    return render_template('posts.html')
@app.route('/game')
def game():
    return render_template('game.html')

@app.route('/aboutsite')
def aboutsite():
    return render_template('aboutsite.html')

from email import contentmanager
from multiprocessing import AuthenticationError
from turtle import title
from app import app, login
import mongoengine.errors
from flask import render_template, flash, redirect, url_for
from flask_login import current_user
from app.classes.data import StoryPage
from app.classes.forms import StoryPageForm
from flask_login import login_required
import datetime as dt

def getPages():
    pages=StoryPage.objects()
    pageChoices = []
    for page in pages:
        pageChoices.append((page.id,page.title))
    return pageChoices

@app.route('/page/new', methods=['GET','POST'])
@login_required
def pageNew():
    form = StoryPageForm()

    if form.validate_on_submit():
        print(form.title.data)
        newPage = StoryPage(
            author = current_user.id,
            title = form.title.data,
            content = form.content.data,
            c1 = form.c1.data,
            c2 = form.c2.data
        )
        newPage.save()
        newPage.reload()
        if form.image.data:
            newPage.image.put(form.image.data, content_type = 'image/jpeg')
            # This saves all the updates
            newPage.save()

        return redirect(url_for('page', pageID = newPage.id))

    pageChoices = getPages()
    form.c1.choices = pageChoices
    form.c2.choices = pageChoices
    return render_template('pageform.html', form=form)
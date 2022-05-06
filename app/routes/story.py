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
from bson.objectid import ObjectId
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
    return render_template('pageform.html', form=form, page=None)

@app.route('/page/edit/<pageID>', methods=['GET','POST'])
@login_required
def pageEdit(pageID):
    form = StoryPageForm()
    editPage = StoryPage.objects.get(pk=pageID)

    if form.validate_on_submit():
        editPage.update(
            title = form.title.data,
            content = form.content.data,
            c1 = ObjectId(form.c1.data),
            c2 = ObjectId(form.c2.data)
        )
        if form.image.data:
            if editPage.image:
                editPage.image.delete()
            editPage.image.put(form.image.data, content_type = 'image/jpeg')
            editPage.save()

        return redirect(url_for('page', pageID = editPage.id))

    pageChoices = getPages()
    form.c1.choices = pageChoices
    form.c2.choices = pageChoices
    form.c1.default = editPage.c1.id
    form.c2.default = editPage.c2.id
    form.process()
    form.title.data = editPage.title
    form.content.data = editPage.content
    
    return render_template('pageform.html', form=form, page = editPage)


@app.route('/page/<pageID>')
def page(pageID):
    thisPage = StoryPage.objects.get(pk=pageID)
    return render_template('page.html',page=thisPage)

@app.route('/pages')
def pages():
    pages=StoryPage.objects()
    return render_template('pages.html',pages=pages)

@app.route('/page/start')
def startPage():
    thisPage = StoryPage.objects.get(pk='6269746f15559196d7dc660d')
    return render_template('page.html',page=thisPage)


@app.route('/page/delete/<pageID>')
def pageDelete(pageID):
    deletePage = StoryPage.objects.get(pk=pageID)
    deletePage.delete()
    flash('Page was deleted')
    return redirect(url_for('pages'))
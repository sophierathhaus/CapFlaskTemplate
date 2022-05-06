# These routes are an example of how to use data, forms and routes to create
# a forum where a posts and comments on those posts can be
# Created, Read, Updated or Deleted (CRUD)

from app import app, login
import mongoengine.errors
from flask import render_template, flash, redirect, url_for
from flask_login import current_user
from app.classes.data import Post, Comment
from app.classes.forms import PostForm, CommentForm
from flask_login import login_required
import datetime as dt

# This is the route to list all posts
@app.route('/journalpost/list')
# This means the user must be logged in to see this page
@login_required
def journalpostList():
    # This retrieves all of the 'posts' that are stored in MongoDB and places them in a
    # mongoengine object as a list of dictionaries name 'posts'.
    journalposts = Post.objects()
    # This renders (shows to the user) the posts.html template. it also sends the posts object 
    # to the template as a variable named posts.  The template uses a for loop to display
    # each post.
    return render_template('journalposts.html',journalposts=journalposts)

# This route will get one specific post and any comments associated with that post.  
# The postID is a variable that must be passsed as a parameter to the function and 
# can then be used in the query to retrieve that post from the database. This route 
# is called when the user clicks a link on postlist.html template.
# The angle brackets (<>) indicate a variable. 
@app.route('/journalpost/<journalpostID>')
# This route will only run if the user is logged in.
@login_required
def journalpost(journalpostID):
    # retrieve the post using the postID
    thisjournalPost = Post.objects.get(id=journalpostID)
    # If there are no comments the 'comments' object will have the value 'None'. Comments are 
    # related to posts meaning that every comment contains a reference to a post. In this case
    # there is a field on the comment collection called 'post' that is a reference the Post
    # document it is related to.  You can use the postID to get the post and then you can use
    # the post object (thisPost in this case) to get all the comments.
    thesejournalComments = Comment.objects(journalpost=thisjournalPost)
    # Send the post object and the comments object to the 'post.html' template.
    return render_template('journalpost.html',journalpost=thisjournalPost,journalcomments=thesejournalComments)

# This route will delete a specific post.  You can only delete the post if you are the author.
# <postID> is a variable sent to this route by the user who clicked on the trash can in the 
# template 'post.html'. 
# TODO add the ability for an administrator to delete posts. 
@app.route('/journalpost/delete/<journalpostID>')
# Only run this route if th euser is logged in.
@login_required
def journalpostDelete(journalpostID):
    # retrieve the post to be deleted using the postID
    deletejournalPost = Post.objects.get(id=journalpostID)
    # check to see if the user that is making this request is the author of the post.
    # current_user is a variable provided by the 'flask_login' library.
    if current_user == deletejournalPost.author:
        # delete the post using the delete() method from Mongoengine
        deletejournalPost.delete()
        # send a message to the user that the post was deleted.
        flash('The Journal Post was deleted.')
    else:
        # if the user is not the author tell them they were denied.
        flash("You can't delete a journal post you don't own.")
    # Retrieve all of the remaining posts so that they can be listed.
    journalposts = Post.objects()  
    # Send the user to the list of remaining posts.
    return render_template('journalposts.html',journalposts=journalposts)


# This route actually does two things depending on the state of the if statement 
# 'if form.validate_on_submit()'. When the route is first called, the form has not 
# been submitted yet so the if statement is False and the route renders the form.
# If the user has filled out and succesfully submited the form then the if statement
# is True and this route creates the new post based on what the user put in the form.
# Because this route includes a form that both gets and posts data it needs the 'methods'
# in the route decorator.
@app.route('/journalpost/new', methods=['GET', 'POST'])
# This means the user must be logged in to see this page
@login_required
# This is a function that is run when the user requests this route.
def journalpostNew():
    # This gets the form object from the form.py classes that can be displayed on the template.
    journalform = PostForm()

    # This is a conditional that evaluates to 'True' if the user submitted the form successfully.
    # validate_on_submit() is a method of the form object. 
    if journalform.validate_on_submit():

        # This stores all the values that the user entered into the new post form. 
        # Post() is a mongoengine method for creating a new post. 'newPost' is the variable 
        # that stores the object that is the result of the Post() method.  
        newjournalPost = Post(
            # the left side is the name of the field from the data table
            # the right side is the data the user entered which is held in the form object.
            journalsubject = journalform.subject.data,
            journalcontent = journalform.content.data,
            author = current_user.id,
            # This sets the modifydate to the current datetime.
            modifydate = dt.datetime.utcnow
        )
        # This is a method that saves the data to the mongoDB database.
        newjournalPost.save()

        # Once the new post is saved, this sends the user to that post using redirect.
        # and url_for. Redirect is used to redirect a user to different route so that 
        # routes code can be run. In this case the user just created a post so we want 
        # to send them to that post. url_for takes as its argument the function name
        # for that route (the part after the def key word). You also need to send any
        # other values that are needed by the route you are redirecting to.
        return redirect(url_for('journalpost',journalpostID=newjournalPost.id))

    # if form.validate_on_submit() is false then the user either has not yet filled out
    # the form or the form had an error and the user is sent to a blank form. Form errors are 
    # stored in the form object and are displayed on the form. take a look at postform.html to 
    # see how that works.
    return render_template('journalpostform.html',journalform=journalform)


# This route enables a user to edit a post.  This functions very similar to creating a new 
# post except you don't give the user a blank form.  You have to present the user with a form
# that includes all the values of the original post. Read and understand the new post route 
# before this one. 
@app.route('/journalpost/edit/<journalpostID>', methods=['GET', 'POST'])
@login_required
def journalpostEdit(journalpostID):
    editjournalPost = Post.objects.get(id=journalpostID)
    # if the user that requested to edit this post is not the author then deny them and
    # send them back to the post. If True, this will exit the route completely and none
    # of the rest of the route will be run.
    if current_user != editjournalPost.author:
        flash("You can't edit a journal post you don't own.")
        return redirect(url_for('journalpost',journalpostID=journalpostID))
    # get the form object
    journalform = PostForm()
    # If the user has submitted the form then update the post.
    if journalform.validate_on_submit():
        # update() is mongoengine method for updating an existing document with new data.
        editjournalPost.update(
            journalsubject = journalform.subject.data,
            journalcontent = journalform.content.data,
            modifydate = dt.datetime.utcnow
        )
        # After updating the document, send the user to the updated post using a redirect.
        return redirect(url_for('journalpost',journalpostID=journalpostID))

    # if the form has NOT been submitted then take the data from the editPost object
    # and place it in the form object so it will be displayed to the user on the template.
    journalform.subject.data = editjournalPost.subject
    journalform.content.data = editjournalPost.content

    # Send the user to the post form that is now filled out with the current information
    # from the form.
    return render_template('journalpostform.html',journalform=journalform)

#####
# the routes below are the CRUD for the comments that are related to the posts. This
# process is exactly the same as for posts with one addition. Each comment is related to
# a specific post via a field on the comment called 'post'.  the 'post' field contains a 
# reference to the Post document. See the @app.route('/post/<postID>') above for more details
# about how comments are related to posts.  Additionally, take a look at data.py to see how the
# relationship is defined in the Post and the Comment collections.

@app.route('/journalcomment/new/<journalpostID>', methods=['GET', 'POST'])
@login_required
def journalcommentNew(journalpostID):
    journalpost = Post.objects.get(id=journalpostID)
    journalform = CommentForm()
    if journalform.validate_on_submit():
        newjournalComment = Comment(
            author = current_user.id,
            journalpost = journalpostID,
            content = journalform.content.data
        )
        newjournalComment.save()
        return redirect(url_for('journalpost',journalpostID=journalpostID))
    return render_template('journalcommentform.html',journalform=journalform,journalpost=journalpost)

@app.route('/journalcomment/edit/<journalcommentID>', methods=['GET', 'POST'])
@login_required
def journalcommentEdit(journalcommentID):
    editjournalComment = Comment.objects.get(id=journalcommentID)
    if current_user != editjournalComment.author:
        flash("You can't edit a comment you didn't write.")
        return redirect(url_for('post',journalpostID=editjournalComment.journalpost.id))
    journalpost = Post.objects.get(id=editjournalComment.post.id)
    journalform = CommentForm()
    if journalform.validate_on_submit():
        editjournalComment.update(
            journalcontent = journalform.content.data,
            modifydate = dt.datetime.utcnow
        )
        return redirect(url_for('journalpost',journalpostID=editjournalComment.post.id))

    journalform.content.data = editjournalComment.content

    return render_template('journalcommentform.html',journalform=journalform,journalpost=journalpost)   

@app.route('/journalcomment/delete/<journalcommentID>')
@login_required
def journalcommentDelete(journalcommentID): 
    deletejournalComment = Comment.objects.get(id=journalcommentID)
    deletejournalComment.delete()
    flash('The comments was deleted.')
    return redirect(url_for('journalpost',journalpostID=deletejournalComment.post.id)) 

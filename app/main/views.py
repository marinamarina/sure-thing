from datetime import datetime
from flask import render_template, redirect, url_for, session, flash, current_app, request
from flask_login import login_required, current_user
from . import main
from .forms import BlogPostForm, CommentPostForm
from .. import db
from ..models import User, Permission, Team, Match #Post, Comment
from ..email import send_email
from ..decorators_me import permission_required, templated
from flask import abort
from ..football_data.football_api_parser import FootballAPIWrapper

@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission, pokus='keek')

#route decorators
@main.route('/', methods=['POST', 'GET'])
@main.route('/index', methods=['POST', 'GET'])
@templated()
def index():
    show_followed=False

    if current_user.is_authenticated():
        #we get the value of the show_followed cookie from the request cookie dictionary
        #and convert it to boolean
        show_followed = bool(request.cookies.get('show_followed', ''))

    '''if show_followed:
        my_query = current_user.followed_posts
    else:
        my_query = Post.query'''

    Match.insert_all_matches()

    #display only played matches
    matches = Match.query.filter_by(played=False).all()

    # define the form
    '''form = BlogPostForm()
    if (current_user.can(Permission.WRITE_ARTICLES)):
        if form.is_submitted():
            print "submitted"
        if form.validate():
            print "valid"
            print form.errors
        if form.validate_on_submit():
            # redirect loop
            post = Post(body_html=form.body_html.data, title=form.title.data, author_id=current_user.id)
            try:
                #add new post
                db.session.add(post)
                return redirect(url_for('.index'))
            except Exception:
                db.session.flush()
            finally:
                flash ("You have now been authorized!" + str(current_user.role))

    posts = my_query.order_by(Post.timestamp.desc()).all()'''

    return dict(  user=current_user, matches=matches) #posts=posts, form=form,

#route decorators
@main.route('/dashboard', methods=['POST', 'GET'])
@templated()
@login_required
def dashboard():
    show_followed=False

    if current_user.is_authenticated():
        #we get the value of the show_followed cookie from the request cookie dictionary
        #and convert it to boolean
        show_followed = bool(request.cookies.get('show_followed', ''))

    '''if show_followed:
        my_query = current_user.followed_posts
    else:
        my_query = Post.query'''

    # define the form
    '''form = BlogPostForm()
    if (current_user.can(Permission.WRITE_ARTICLES)):
        if form.is_submitted():
            print "submitted"
        if form.validate():
            print "valid"
            print form.errors
        if form.validate_on_submit():
            # redirect loop
            post = Post(body_html=form.body_html.data, title=form.title.data, author_id=current_user.id)
            try:
                #add new post
                db.session.add(post)
                return redirect(url_for('.index'))
            except Exception:
                db.session.flush()
            finally:
                flash ("You have now been authorized!" + str(current_user.role))

    posts = my_query.order_by(Post.timestamp.desc()).all()'''

    return dict(  user=current_user) #posts=posts, form=form,

'''
@main.route('/show_all_posts')
@login_required
def show_all_posts():
    redirect_to_index = redirect(url_for('.index'))
    response = current_app.make_response(redirect_to_index)
    response.set_cookie('show_followed',value='')
    return response

@main.route('/show_followed_users_posts')
@login_required
def show_followed_users_posts():
    redirect_to_index = redirect(url_for('.index'))
    response = current_app.make_response(redirect_to_index)
    response.set_cookie('show_followed',value='1')
    return response
'''

@main.route('/leagueTable')
@templated()
def leagueTable():
    table = dict()
    # example usage
    wrap = FootballAPIWrapper()
    # set the api key
    wrap.api_key = '2890be06-81bd-b6d7-1dcb4b5983a0'
    league_table = wrap.league_table

    my_team_id = '9427'
    try:
        for key, value in league_table.items():
            print value.position
            return dict(league_table=wrap.league_table)

    except Exception:
        return redirect(url_for('main.index'))


@main.route('/admin', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMINISTER)
@templated()
def admin():
    pass


# user profile to view by other users
@main.route('/user/<username>')
@templated()
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    #posts = Post.query.filter_by(author=user).order_by(Post.timestamp.desc()).all()

    return dict(user=user) #posts=posts

'''
# a unique url to each blogpost
@main.route('/post/<int:id>', methods=['GET', 'POST'])
#@templated
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentPostForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body_html.data,
                          post=post,
                          author=current_user._get_current_object())
        try:
            #add new comment
            db.session.add(comment)
            return redirect(url_for('.post', id=post.id))
        except Exception:
            db.session.flush()
        finally:
            flash('Your comment has been published!')

    comments = post.comments.order_by(Comment.timestamp.asc()).all()

    return render_template('main/post.html', comments=comments, posts=[post], form=form)

# a unique url to the editor for a blogpost
@main.route('/post_editor/<int:id>', methods=['POST', 'GET'])
@login_required
def post_editor(id):

    form = BlogPostForm()
    post = Post.query.get_or_404(id)

    if current_user.id != post.author_id and not current_user.can(Permission.ADMINISTER):
        abort(403)
    else:
        if form.validate_on_submit():
            post.body_html=form.body_html.data
            post.title=form.title.data
            post.edited=True
            try:
                #add new post
                db.session.add(post)
                return redirect(url_for('.index'))
            except Exception:
                db.session.flush()
            finally:
                flash('You have edited your blogpost, congratulations!')

    return render_template( 'main/post_editor.html', form=form, posts=[post])
'''

@main.route('/follow/<username>')
@login_required
def follow(username):
    me = current_user
    other_user = User.query.filter_by(username=username).first()

    if other_user is None:
        flash("User doesnt exist")

    if me.is_following(other_user):
        flash("You are already following this user")
        return redirect(url_for('.user', username=username))

    me.follow(other_user)
    flash("Congratulations, you are now following " + username)
    return redirect(url_for('main.user', username=username))

@main.route('/unfollow/<username>')
@login_required
def unfollow(username):
    me = current_user
    other_user = User.query.filter_by(username=username).first()

    if other_user is None:
        flash("User doesnt exist")

    if not me.is_following(other_user):
        flash("You are not following this user")
        return redirect(url_for('.user', username=username))

    me.unfollow(other_user)
    flash("Congratulations, you are now not following " + username)
    return redirect(url_for('main.user', username=username))

#a route to show the users following our selected user
@main.route('/show_followers/<username>')
@login_required
def show_followers(username):
    followed_user = User.query.filter_by(username=username).first()
    if followed_user is None:
        flash("User doesnt exist!")
        return redirect(url_for('.index'))

    # my own code, generator (as opposed to list from a book with added condition to exclude the user himself)
    follows = ({'user': item.follower, 'timestamp': item.timestamp} for item in followed_user.followers if item.follower!=followed_user)

    from pprint import pprint
    pprint(follows)

    return render_template('main/followers.html', user=followed_user, title=str(username) + "'s followers", follows=follows)

#a route to show the users followed by our selected user
@main.route('/show_followed_users/<username>')
@login_required
def show_followed_users(username):
    # this is our selected user
    following_user = User.query.filter_by(username=username).first()
    if following_user is None:
        flash("User doesnt exist!")
        return redirect(url_for('.index'))

    # my own code, generator (as opposed to list from a book with added condition to exclude the user himself)
    followed = ({'user': item.followed, 'timestamp': item.timestamp} for item in following_user.followed if item.followed!=following_user)
    return render_template('main/followed.html', user=following_user, title=str(username) + "'s followers", follows=followed)

'''
@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    comments = Comment.query.order_by(Comment.timestamp.desc())
    return render_template('main/moderate.html', comments=comments)

@main.route('/moderate_enable/<int:id>')
@login_required
#@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate'))

@main.route('/moderate_disable/<int:id>')
@login_required
#@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate'))'''
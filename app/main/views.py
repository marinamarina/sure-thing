from datetime import datetime
from flask import render_template, redirect, url_for, abort, flash, \
    session, current_app, request
from flask_login import login_required, current_user
from . import main
from .forms import BlogPostForm, CommentPostForm, UserBettingDefaultSettings
from .. import db
from ..models import User, Permission, Team, \
    Match, SavedForLater, PredictionModule, \
    ModuleUserSettings, ModuleUserSettingsSet
from ..email import send_email
from ..decorators_me import permission_required, templated
from ..football_data.football_api_wrapper import FootballAPIWrapper
from .. import socketio
from threading import Thread, Event
from ..threads.data_handle_threads import RandomThread, DataUpdateThread
from collections import namedtuple

# random number Generator Thread
thread = Thread()
thread_stop_event = Event()

@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission, pokus='keek')


#route decorators
@main.route('/', methods=['POST', 'GET'])
@main.route('/index', methods=['POST', 'GET'])
@templated()
def index():
    show_played_matches = False
    Match.update_all_matches()

    #we get the value of the show_followed cookie from the request cookie dictionary
    #and convert it to boolean
    show_played_matches = bool(request.cookies.get('show_played_matches', ''))

    if show_played_matches:
        my_query = Match.query.filter_by(played=True).order_by(Match.date_stamp.desc(), Match.time_stamp.asc())
    else:
        my_query = Match.query.filter_by(played=False).order_by(Match.date_stamp.asc(), Match.time_stamp.asc())


    #switch between displaying past and future matches
    #order matches first by the date and then by the time
    matches = my_query.all()

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

    return dict(user=current_user, matches=matches)  #posts=posts, form=form,


@main.route('/show_unplayed')
def show_unplayed():
    redirect_to_index = redirect(url_for('.index'))
    response = current_app.make_response(redirect_to_index)
    response.set_cookie('show_played_matches', value='')
    return response


@main.route('/show_played')
def show_played():
    redirect_to_index = redirect(url_for('.index'))
    response = current_app.make_response(redirect_to_index)
    response.set_cookie('show_played_matches', value='1')
    return response


@main.route('/save_match/<int:match_id>')
@login_required
def save_match(match_id):
    me = current_user
    match = Match.query.filter_by(id=match_id).first()

    if me.is_match_saved(match):
        flash("You have already saved this match to  your dashboard.")
        return redirect(url_for('.index'))

    me.save_match(match)
    flash("Congratulations, you have saved a match to your dashboard!")
    return redirect(url_for('.index'))


@main.route('/view_match/<int:match_id>')
def view_match(match_id):
    me = current_user
    match = Match.query.filter_by(id=match_id).first()

    return render_template('main/view_match.html', match=match, user=current_user)


@main.route('/dashboard')
@login_required
def dashboard():
    savedmatches = current_user.saved_matches

    #post = Post.query.get_or_404(id)

    #if current_user.id != post.author_id and not current_user.can(Permission.ADMINISTER):
    # abort(403)


    # if user has already saved these settings at least once, any module number is good
    '''
        s = ModuleUserSettings.query.filter_by(user_id=me.id, module_id=1).first()
        if s is not None:
            s = ModuleUserSettings.query.filter_by(user_id=me.id, module_id=1).first().weight = form.league_position_weight
            ModuleUserSettings.query.filter_by(user_id=me.id, module_id=2).first().weight = form.form_weight
            ModuleUserSettings.query.filter_by(user_id=me.id, module_id=3).first().weight = form.home_away_weight
        else:
            data = {"user_id": 2, 1: 0.2, 2: 0.4, 3: 0.4}
            s = ModuleUserSettingsSet(user_id=data.pop('user_id'))
            s.weights = data

        try:
            #save new settings
            db.session.add(s)
            return redirect(url_for('.dashboard'))
        except Exception:
            db.session.flush()
        finally:
            flash('You have saved your default prediction settings, congratulations!')

     #db.session.commit()'''


    return render_template('main/dashboard.html', savedmatches=savedmatches, user=current_user, title='Dashboard')

# a unique url to the editor for a blogpost
@main.route('/prediction_settings', methods=['GET','POST'])
@login_required
def prediction_settings():
    me = current_user
    form = UserBettingDefaultSettings()
    current_weights = ModuleUserSettings.query.filter_by(user_id=me.id).all()


    if form.validate_on_submit():


        if ModuleUserSettings.query.filter_by(user_id=me.id).first() is not None:
            for pm in PredictionModule.query.all():
                ModuleUserSettings.query.filter_by(user_id=me.id, module_id=pm.id).first().weight = form[pm.name + '_weight'].data


            for i in range(1,3):
                try:
                    db.session.add(ModuleUserSettings.query.filter_by(user_id=me.id, module_id=i).first())
                    return redirect(url_for('.prediction_settings'))
                except Exception:
                    db.session.flush()
                finally:
                    flash('You have saved your default prediction settings, congratulations!')
        else:
            data = {1: form.league_position_weight.data, 2: form.form_weight.data, 3: form.home_away_weight.data}
            s = ModuleUserSettingsSet(user_id=me.id)
            s.weights = data
            db.session.add(s)
        db.session.commit()

        #updated_data = {1:}

    return render_template( 'main/prediction_settings.html', user=me, form=form, current_weights=current_weights)#, posts=[post])

@main.route('/view_match_dashboard/<int:match_id>')
@login_required
def view_match_dashboard(match_id):
    me = current_user
    savedmatch = SavedForLater.query.filter_by(match_id=match_id).first()

    winner = Match.predicted_winner(savedmatch.match, user=me)


    return render_template('main/view_match_dashboard.html', savedmatch=savedmatch,  user=current_user, team_winner=winner[0],
                           probability = winner[1]
                           )


@main.route('/commit_match/<int:match_id>')
@login_required
def commit_match(match_id):
    me = current_user
    saved_matches = current_user.saved_matches
    match = Match.query.filter_by(id=match_id).first()

    predicted_winner=Match.predicted_winner(match, user=me)
    #saved
    # match-->committed
    # adding a listener watching when this match becomes played, record winnings for the user

    flash("Congratulations, you have commited your bet! Match id: " + str(match_id) + "Predicted winner: " + str(predicted_winner))

    return redirect(url_for('.dashboard', matches=saved_matches))

'''@socketio.on('matchCommited', namespace='/test')
def matchCommited(msg):
    print ()'''



@main.route('/remove_match/<int:match_id>')
@login_required
def remove_match(match_id):
    me = current_user
    match = Match.query.filter_by(id=match_id).first()

    me.remove_match(match)
    flash("Congratulations, you have removed this match from your dashboard!")
    saved_matches = me.saved_matches

    return redirect(url_for('.dashboard', matches=saved_matches))


@main.route('/keek')
@login_required
def keek():
    return redirect(url_for('.index'))


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

    return dict(user=user)  #posts=posts


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
    follows = ({'user': item.follower, 'timestamp': item.timestamp} for item in followed_user.followers if
               item.follower != followed_user)

    from pprint import pprint

    pprint(follows)

    return render_template('main/followers.html', user=followed_user, title=str(username) + "'s followers",
                           follows=follows)


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
    followed = ({'user': item.followed, 'timestamp': item.timestamp} for item in following_user.followed if
                item.followed != following_user)
    return render_template('main/followed.html', user=following_user, title=str(username) + "'s followers",
                           follows=followed)


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

'''@threads.on('my event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': message['data'], 'count': session['receive_count']})


@threads.on('my broadcast event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)

@threads.on('join', namespace='/test')
def join(message):
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': 'In rooms: ' + ', '.join(request.namespace.rooms),
          'count': session['receive_count']})


@threads.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})


@threads.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')'''


@socketio.on('connect', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')

    #Start the random number generator thread only if the thread has not been started before.
    if not thread.isAlive():
        print "Starting Thread"
        thread = DataUpdateThread()
        thread.start()


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')
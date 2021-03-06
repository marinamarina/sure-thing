from flask import render_template, redirect, url_for, abort, flash, \
    session, current_app, request, jsonify
from flask_login import login_required, current_user
from . import main
from .forms import UserDefaultPredictionSettings, UserMatchPredictionSettings
from .. import db, socketio
from ..models import User, Permission, Team, \
    Match, SavedForLater, PredictionModule, Message, \
    ModuleUserSettings, ModuleUserMatchSettings

from ..email import send_email
from ..decorators_me import permission_required, templated
from threading import Thread, Event
from ..threads.data_handle_threads import DataUpdateThread
from collections import namedtuple

# initiating a Thread
thread = Thread()
thread_stop_event = Event()
from gevent import monkey
monkey.patch_all()


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

    #we get the value of the show_played_matches cookie from the request cookie dictionary
    #and convert it to boolean
    show_played_matches = bool(request.cookies.get('show_played_matches', ''))

    if show_played_matches:
        my_query = Match.query.filter_by(was_played=True).order_by(Match.time_stamp.asc())
        sort_order_reversed = True
    else:
        my_query = Match.query.filter_by(was_played=False).order_by(Match.time_stamp.asc())
        sort_order_reversed = False

    query = db.session.query(Match.date_stamp.distinct().label("date_stamp"))
    unique_dates = [row.date_stamp for row in query.all()]

    matches = {date: my_query.filter_by(date_stamp=date).all()
               for date in unique_dates
               if my_query.filter_by(date_stamp=date).all()
    }

    #MatchForFormInfo(id=1788004, date_stamp=datetime.date(2014, 8, 18), time_stamp=datetime.time(19, 0), hometeam_id=9072, awayteam_id=9092, hometeam_score=1, awayteam_score=3, outcome='W')

    return dict(user=current_user, matches=matches, sort_order_reversed=sort_order_reversed)


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


@socketio.on('data_updated', namespace='/test')
def data_updated(msg):
    Match.update_all_matches()
    print 'matches updated using sockets'

@main.route('/messages')
@login_required
@templated()
def messages():
    me=current_user
    messages = me.messages.order_by(Message.timestamp.desc())
    if (not me.list_new_messages):
        socketio.emit('no_new_messages', namespace='/test')

    return dict(user=me, messages=messages)

# a unique url to each message
@main.route('/view_message/<int:id>')
@login_required
def view_message(id):
    me = current_user
    message = Message.query.get_or_404(id)
    message.new=False
    db.session.add(message)

    if (not me.list_new_messages):
        socketio.emit('no_new_messages', namespace='/test')


    return render_template('main/view_message.html', message=message, user=current_user)


@main.route('/delete_message/<int:id>')
@login_required
def delete_message(id):
    me = current_user
    message = Message.query.filter_by(id=id).first()

    Message.delete_message(message)
    flash("You have deleted a message from your postbox.")
    messages = me.messages.all()

    return redirect(url_for('.messages'))


@main.route('/delete_all_messages')
@login_required
def delete_all_messages():
    me = current_user
    me.delete_messages()

    return redirect(url_for('.messages'))


@main.route('/leaderboard')
@login_required
@templated()
def leaderboard():
    users = User.query\
              .order_by(User.win_points.desc())\
              .all()


    Winners = namedtuple('Winners',
                               'username win_points loss_points lsp')

    return dict(user=current_user, users=users)


@main.route('/save_match/<int:match_id>')
@login_required
def save_match(match_id):
    me = current_user
    match = Match.query.filter_by(id=match_id).first()

    if me.has_match_saved(match):
        flash("You have already saved this match to  your dashboard.")
        return redirect(url_for('.index'))

    me.save_match(match)
    #redirect(url_for('.index'))

    flash("Congratulations, you have saved a match to your dashboard!")
    return redirect(url_for('.index'))


@main.route('/commit_match/<int:match_id>')
@login_required
def commit_match(match_id):
    me = current_user
    savedmatch = me.list_matches(match_id=match_id)[0]
    prediction_modules = PredictionModule.query.all()
    module_length = len(prediction_modules)

    winner = Match.predicted_winner(savedmatch.match, me, savedmatch.user_hunch)
    team_winner_id = winner.team_winner_id
    default_weights = [module for module in prediction_modules]

    # check what settings were used
    if not me is None:
        user_prediction_settings = me.list_prediction_settings()
        user_match_prediction_settings = me.list_match_specific_settings(match_id=savedmatch.match.id)

    if user_match_prediction_settings:
        # use match specific
        weights_used = user_match_prediction_settings
    elif user_prediction_settings:
        # use user specific
        weights_used = user_prediction_settings

    else:
        # use default
        weights_used = default_weights

    if savedmatch.committed:
        return redirect(url_for('.dashboard'))
    else:
        savedmatch.committed = True
        savedmatch.weight_league_position = weights_used[0].weight
        savedmatch.weight_form = weights_used[1].weight
        savedmatch.weight_home_away = weights_used[2].weight
        savedmatch.predicted_winner = team_winner_id
        db.session.add(savedmatch)
        db.session.commit()
        flash("Congratulation! You have successfully committed your saved match!")
        return redirect(url_for('.dashboard'))

@main.route('/view_match/<int:match_id>')
def view_match(match_id):
    me = current_user
    match = Match.query.filter_by(id=match_id).first()

    lt = Team.league_table()
    lt_hometeam = lt[str(match.hometeam_id)]
    lt_awayteam = lt[str(match.awayteam_id)]


    return render_template('main/view_match.html',
                           match=match,
                           user=current_user,
                           lt_hometeam=lt_hometeam,
                           lt_awayteam=lt_awayteam
    )


@main.route('/dashboard')
@login_required
def dashboard():
    savedmatches = current_user.list_matches()

    upcomingmatches=[s for s in savedmatches if not s.was_played]

    return render_template('main/dashboard.html',
                           savedmatches=upcomingmatches,
                           user=current_user,
                           title='Dashboard')


@main.route('/archived')
@login_required
def archived():
    savedmatches = current_user.list_matches()
    playedmatches = [s for s in reversed(savedmatches) if s.was_played]


    return render_template('main/archived.html',
                           savedmatches=playedmatches,
                           user=current_user,
                           title='Archived')


@main.route('/prediction_settings', methods=['GET','POST'])
@login_required
def prediction_settings():
    me = current_user
    form = UserDefaultPredictionSettings()
    #current user prediction settings in the database

    # either I already set weights or use system default
    current_weights = me.prediction_settings.all()
    modules = PredictionModule.query.all()

    if form.validate_on_submit():

        for module in modules:
            # if user already has set default weights in the database
            if current_weights:
                settings_item = ModuleUserSettings.query.filter_by(user_id=me.id, module_id=module.id).first()
            else:
                # adding weights for the first time
                settings_item = ModuleUserSettings(user_id=me.id, module_id=module.id)

            settings_item.weight = float(form[module.name + '_weight'].data) / 100

            try:
                db.session.add(settings_item)
            except Exception:
                db.session.flush()

        flash("You have successfully adjusted your prediction weights!")

        return redirect(url_for('.prediction_settings'))
        #flash('You have saved your default prediction settings, congratulations!')

    # if user has no betting settings, make each current weight equal to an empty string

    """if not current_weights:
        current_weights = ['' for i in range(0, len(modules))]"""


    return render_template( 'main/prediction_settings.html', user=me, form=form, current_weights=current_weights)


@main.route('/view_match_dashboard/<int:match_id>', methods=['GET', 'POST'])
@login_required
def view_match_dashboard(match_id):
    me = current_user

    # 0 or Draw is the default value for user hunch
    # if weights for hunch is set, but hunch has not been chosen, 0 value
    # will "eliminate user hunch module from influencing the overall prediction"

    #user_hunch = request.args.get('user_hunch', 0, type=int)

    #savedmatch=current_user.list_matches(match_id=match_id)[0]

    # in case this match is not saved in my saved matches
    if not me.list_matches(match_id=match_id):
        return redirect (url_for('.dashboard'))

    savedmatch = me.list_matches(match_id=match_id)[0]
    match = savedmatch.match
    form = UserMatchPredictionSettings()

    match_specific_weights = me.list_match_specific_settings(match_id=match.id)
    prediction_settings = me.list_prediction_settings()
    modules = PredictionModule.query.all()

    if form.validate_on_submit():
        '''if(me.list_matches(match_id=match_id)[0].committed):
            return redirect(url_for('.view_match_dashboard', match_id=match_id))'''
        for module in modules:
            # if user already has set custom weights for the match
            if match_specific_weights:
                settings_item = ModuleUserMatchSettings.query.filter_by(user_id=me.id, match_id=match.id, module_id=module.id).first()
            else:
                # create a new one
                settings_item = ModuleUserMatchSettings(user_id=me.id, match_id=match.id, module_id=module.id)

            settings_item.weight = float((form[module.name + '_weight'].data)) /100

            try:
                db.session.add(settings_item)
            except Exception:
                db.session.flush()

        db.session.commit()

        return redirect(url_for('.view_match_dashboard', match_id=match.id))
        flash('You have saved your match specific prediction settings, congratulations!')

    if savedmatch.user_hunch:
        user_hunch = savedmatch.user_hunch
    else:
        user_hunch = 0

    winner = Match.predicted_winner(match, user=me, user_hunch=user_hunch)

    lt = Team.league_table()
    lt_hometeam = lt[str(match.hometeam_id)]
    lt_awayteam = lt[str(match.awayteam_id)]

    # current weights used for the prediction can be either user default or match specific
    # TODO: how about system settings?
    current_weights = match_specific_weights if match_specific_weights else prediction_settings


    return render_template('main/view_match_dashboard.html',
                           form=form,
                           savedmatch=savedmatch,
                           match=match,
                           user=current_user,
                           lt_hometeam=lt_hometeam,
                           lt_awayteam=lt_awayteam,
                           team_winner_name=winner[1],
                           probability=winner[2],
                           current_weights=current_weights
                           )


@main.route('/update_hunch/<int:match_id>', methods=['GET', 'POST'])
@login_required
def update_hunch(match_id):
    me = current_user
    match = Match.query.filter_by(id=match_id).first()
    savedmatch = me.list_matches(match_id=match_id)[0]

    user_hunch = request.args.get('hunch', 0, int)
    savedmatch.user_hunch = user_hunch
    db.session.add(savedmatch)
    db.session.commit()
    socketio.emit('hunch_updated', {'data':{'team_winner_name': match.predicted_winner(match, me, user_hunch)[1],
                                    'probability': match.predicted_winner(match, me, user_hunch)[2]
                                            }
                                    },
                  namespace='/test')

    return redirect(url_for('.view_match_dashboard', match_id=match.id))


    flash("Congratulations, you have updated user hunch value!")
    return redirect(url_for('.view_match_dashboard', match_id=match.id))


@main.route('/view_played_match/<int:match_id>')
@login_required
def view_played_match(match_id):
    me = current_user

    match = Match.query.filter_by(id=match_id).first()

    prediction = Match.predicted_winner(match, me)
    predicted_winner = prediction.team_winner_name
    predicted_probability = int(prediction.probability)

    match_settings = me.list_match_specific_settings(match_id=match.id)
    match_is_saved = me.has_match_saved(match)
    match_is_committed = me.has_match_committed(match)

    # how many times match was saved to dashboard
    saved_matches = match.saved_for_later.all()
    saved_matches_count = len(saved_matches)
    # how many time match was committed
    saved_matches_committed = [sm for sm in saved_matches if sm.committed]
    saved_matches_committed_count = len(saved_matches_committed)

    # how many users won the bet
    saved_matches_won = [sm for sm in saved_matches_committed if sm.bettor_won]
    saved_matches_won_bet_count = len(saved_matches_won)

    # how many users lost the bet
    saved_matches_lost_bet_count = saved_matches_committed_count - saved_matches_won_bet_count

    # how many times home/draw/away was predicted by users
    saved_matches_predicted_home = [sm for sm in saved_matches_committed if sm.predicted_winner == match.hometeam_id]

    if saved_matches_predicted_home != 0 and saved_matches_committed_count != 0:
        saved_matches_predicted_home_share = len(saved_matches_predicted_home) * 100 / saved_matches_committed_count
    else:
        saved_matches_predicted_home_share = 0

    saved_matches_predicted_away = [sm for sm in saved_matches_committed if sm.predicted_winner == match.awayteam_id]

    if saved_matches_predicted_away != 0 and saved_matches_committed_count != 0:
        saved_matches_predicted_away_share = len(saved_matches_predicted_away) * 100 / saved_matches_committed_count
    else:
        saved_matches_predicted_away_share = 0

    saved_matches_predicted_draw = [sm for sm in saved_matches_committed if sm.predicted_winner == -1]

    if saved_matches_predicted_draw != 0 and saved_matches_committed_count != 0:
        saved_matches_predicted_draw_share = len(saved_matches_predicted_draw) * 100 / saved_matches_committed_count
    else:
        saved_matches_predicted_draw_share = 0

    saved_match = me.list_matches(match_id=match.id)
    sm = [] if not saved_match else saved_match[0]

    return render_template('main/view_played_match.html',
                           match=match,
                           sm=sm,
                           is_saved=match_is_saved,
                           is_committed=match_is_committed,
                           sm_count=saved_matches_count,
                           committed_count=saved_matches_committed_count,
                           won_bet_count=saved_matches_won_bet_count,
                           lost_bet_count=saved_matches_lost_bet_count,
                           home_share=saved_matches_predicted_home_share,
                           away_share=saved_matches_predicted_away_share,
                           draw_share=saved_matches_predicted_draw_share,
                           user=current_user,
                           match_settings=match_settings,
                           predicted_winner=predicted_winner,
                           probability=predicted_probability)

@main.route('/remove_match/<int:match_id>')
@login_required
def remove_match(match_id):
    me = current_user
    match = Match.query.filter_by(id=match_id).first()

    me.remove_match(match)
    flash("Congratulations, you have removed this match from your dashboard!")
    saved_matches = me.saved_matches

    if match.was_played:
        return redirect(url_for('.archived', matches=saved_matches))
    else:
        return redirect(url_for('.dashboard', matches=saved_matches))


@main.route('/admin', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMINISTER)
@templated()
def admin():
    pass

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
    return redirect(url_for('auth.user', username=username))


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
    return redirect(url_for('auth.user', username=username))


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

# user profile to view by other users
@main.route('/user/<username>')
@login_required
def user(username):
    me = User.query.filter_by(username=username).first()
    if me is None:
        abort(404)
    won_bets =[]

    for m in me.list_matches(committed=True):
        if m.bettor_won:
            won_bets.append(m)
    won_bets = won_bets[-3:]

    #posts = Post.query.filter_by(author=user).order_by(Post.timestamp.desc()).all()

    return render_template('main/user.html', viewed_user=me, won_bets=won_bets)  #posts=posts

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

@main.route('/terms_and_conditions')
def terms_and_conditions():
    return render_template('main/terms_and_conditions.html', user=current_user, title='Terms and Conditions')

@main.route('/privacy_policy')
def privacy_policy():
    return render_template('main/privacy_policy.html', user=current_user, title='Privacy Policy')

@socketio.on('hunch_updated', namespace='/test')
def handle_message(message):
    print('received message: ' + message)

@socketio.on('connect', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')

    #Start the data update thread only if the thread has not been started before.
    if not thread.isAlive():
        print "Starting Thread"
        thread = DataUpdateThread()
        thread.start()


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    global disconnected
    disconnected = '/test'
    print('Client disconnected')
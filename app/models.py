from . import db, faw
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager
from datetime import datetime
import hashlib
from flask import flash, render_template, current_app
from sqlalchemy.ext.associationproxy import association_proxy
from collections import namedtuple


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()
        db.session.close()

    def __repr__(self):
        return '<Role (name={})>'.format(self.name)


class Message(db.Model):
    __tablename__='messages'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime(), index=True, default = datetime.utcnow)
    new = db.Column(db.Boolean, default=True)
    addressee_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def delete_message(message):
        m = Message.query.filter_by(id=message.id).first()
        if m:
            db.session.delete(m)

    def __repr__(self):
        """message representation"""
        return '<Message> title: {}, user_id: {}, timestamp: {}'\
            .format(self.title,
                    self.addressee_id,
                    self.timestamp
        )


class ModuleUserMatchSettings(db.Model):
    """set custom user % for each match"""
    __tablename__='moduleusermatchsettings'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('savedforlater.match_id'), primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('prediction_modules.id'), primary_key=True)
    weight = db.Column(db.Float)
    user = db.relationship('User', backref = "user_match_assoc")

    def __repr__(self):
        return "<ModuleUserMatchSettings> user_id: {}/match_id: {} (module_id: {}, weight:{})".format(
            self.user_id,
            self.match_id,
            self.module_id,
            self.weight
        )


class PredictionModule(db.Model):
    __tablename__ = 'prediction_modules'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    description = db.Column(db.String(64))
    weight = db.Column(db.Float)
    module = db.relationship('ModuleUserMatchSettings', backref=db.backref('module'),
                            lazy='dynamic',
                            primaryjoin='ModuleUserMatchSettings.module_id==PredictionModule.id')

    @staticmethod
    def insert_modules():
        modules = {
            'league_position': 0.50,
            'form': 0.30,
            'home_away': 0.20,
            'user_hunch': 0.0
        }
        for m in modules:
            module = PredictionModule.query.filter_by(name=m).first()
            if module is None:
                module = PredictionModule(name=m)
            module.weight = modules[m]
            db.session.add(module)
        db.session.commit()
        db.session.close()

    def __repr__(self):
        return "<PredictionModule> id:{} name:{} weight:{}".format(
                self.id,
                self.name,
                self.weight
        )


class ModuleUserSettings(db.Model):
    """set custom user %"""
    __tablename__='moduleusersettings'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('prediction_modules.id'), primary_key=True)
    weight = db.Column(db.Float)
    user = db.relationship("User", backref = "user_assocs")


    def __repr__(self):
        return "<ModuleUserSettings> user_id: {}, module_id: {}, weight:{}".format(
            self.user_id,
            self.module_id,
            self.weight
        )


class SavedForLater(db.Model):
    """matches saved by users, association table"""
    __tablename__='savedforlater'
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), primary_key=True)
    committed = db.Column(db.Boolean, default=False)
    weight_league_position = db.Column(db.Float, default=None)
    weight_form = db.Column(db.Float, default=None)
    weight_home_away = db.Column(db.Float, default=None)
    user_hunch = db.Column(db.Integer, default=0)
    predicted_winner = db.Column(db.Integer, default=None)
    match = db.relationship("Match", backref = "user_assocs", order_by="Match.date_stamp, Match.time_stamp")
    bettor = db.relationship("User", backref="bettor")
    match_specific_settings = db.relationship("ModuleUserMatchSettings",
                                                backref=db.backref('settings', lazy='joined'),
                                                lazy='dynamic',
                                                cascade='all, delete-orphan'
    )

    was_played = association_proxy('match', 'was_played')

    #TODO
    def update_lsp(self, rate):
        lsp = 0
        rateArr=map(int, rate.split('/'))
        print rateArr
        if rateArr[0] > rateArr[1]:
            lsp = 1 + rateArr[0] / rateArr[1]
        else:
            lsp = rateArr[0] / rateArr[1]

        self.bettor.lsp = lsp
        # should i add this to a session?

    @property
    def bettor_won(self):
        # predicted winner is calculated based on the weights + winners for each module
        if self.match.actual_winner == Match.predicted_winner(self.match, self.bettor).team_winner_id:
            return True
        else:
            return False
    @property
    def predicted_winner_name(self):
        return Team.query.filter_by(id=self.predicted_winner).first().name

    def __repr__(self):
        return "<SavedForLater {}/{}> " \
               "userid: {}, matchid: {}, date:{}, committed:{}, " \
               "w_league_position: {} " \
               "w_form: {} " \
               "w_home_away: {} " \
               "predicted_winner:{}"\
            .format(
                self.match.hometeam.name,
                self.match.awayteam.name,
                self.users_id,
                self.match_id,
                self.match.date,
                self.committed,
                self.weight_league_position,
                self.weight_form,
                self.weight_home_away,
                self.predicted_winner
    )

    @staticmethod
    def on_changed_match_status(target, value, old_value, initiator):
        all_savedmatches = SavedForLater.query.all()

        # make sure the match is not just overwritten and win/loss points are re-added for the second time
        if value is True and old_value is False:

            # looping through all occurences of this match being saved by any user
            for savedmatch in all_savedmatches:

                if(savedmatch.match==target and savedmatch.committed):

                    msg = Message(addressee_id=savedmatch.bettor.id)

                    print "users having this match saved and committed: %s" % savedmatch.bettor
                    print 'Won?' + str(savedmatch.bettor_won)
                    print 'Played?' + str(savedmatch.match.was_played)
                    predicted_winner = Team.query.filter_by(id=savedmatch.predicted_winner).first()
                    actual_winner = Team.query.filter_by(id=savedmatch.match.actual_winner).first()


                    if savedmatch.bettor_won:
                        print "old value: " + str(savedmatch.bettor.win_points)
                        savedmatch.bettor.win_points += 1
                        print "new value: " + str(savedmatch.bettor.win_points)
                        title = "You won a bet for " \
                               + savedmatch.match.hometeam.name \
                               + ' vs. ' \
                               + savedmatch.match.awayteam.name \
                               + ', played on ' \
                               + savedmatch.match.date

                        body = "congratulation, you predicted this match results correctly!"

                    elif not savedmatch.bettor_won:
                        savedmatch.bettor.loss_points += 1
                        title = "You lost a bet for " \
                                + savedmatch.match.hometeam.name \
                                + ' vs.' \
                                + savedmatch.match.awayteam.name \
                                + ', played on ' \
                                + savedmatch.match.date

                        body = "unfortunately, you did not predict this match result correctly!"
                    else:
                        return False

                    if predicted_winner is not None:
                        predicted_winner_name = predicted_winner.name
                    else:
                        predicted_winner_name = 'Draw'


                    if actual_winner is not None:
                        actual_winner_name = actual_winner.name
                    else:
                        actual_winner_name = 'Draw'


                    msg.title = title
                    msg.body = render_template('messages/message' + '.html',
                                               savedmatch=savedmatch,
                                               body=body,
                                               predicted_winner_name=predicted_winner_name,
                                               actual_winner_name=actual_winner_name)

                    db.session.add(msg)
                    db.session.add(savedmatch.bettor)

            try:
                db.session.commit()
            except:
                db.session.rollback()
                raise

        # update user's LSP
        # u=User.query.all()[2]
        #  match1=User.query.all()[2].list_matches()[0]
        # match1.match.was_played=False



class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    # user will log with an email address
    email = db.Column(db.String(120), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    real_name = db.Column(db.String(64))
    # password is stored in this field
    password_hash = db.Column(db.String(128))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    fav_team = db.Column(db.Text())
    confirmed = db.Column(db.Boolean, default=False)
    member_since = db.Column(db.DateTime(), default = datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default = datetime.utcnow)
    win_points = db.Column(db.Integer, default=0, nullable=True)
    loss_points = db.Column(db.Integer, default=0, nullable=True)
    lsp = db.Column(db.Float, default=0, nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))


    # I saved those matches for a review
    saved_matches = db.relationship('SavedForLater',
                                    foreign_keys=[SavedForLater.users_id],
                                    backref=db.backref('user', lazy='joined'),
                                    lazy='dynamic',
                                    passive_deletes=True,
                                    cascade='all, delete-orphan'
                                    )

    prediction_settings = db.relationship('ModuleUserSettings',
                                          backref=db.backref('bettor', lazy='joined'),
                                          foreign_keys=[ModuleUserSettings.user_id],
                                          lazy='dynamic',
                                          cascade='all, delete-orphan'
    )

    match_specific_settings = db.relationship('ModuleUserMatchSettings',
                                              backref=db.backref('bettor_match', lazy='joined'),
                                              foreign_keys=[ModuleUserMatchSettings.user_id, PredictionModule.id],
                                              lazy='dynamic',
                                              cascade='all, delete-orphan'
    )

    messages = db.relationship('Message', backref='addressee', lazy='dynamic')

    # take a look, this provides me an overview of matches for the user, only this value
    bets_won = association_proxy('saved_matches', 'bettor_won')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

        if self.role is None:
            if self.email == 'shchukina.marina@gmail.com': #current_app.config['FOOTY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
                flash('SUPER POWERS, can I write articles? %r' % self.can(Permission.WRITE_ARTICLES))
            else:
                self.role = Role.query.filter_by(default=True).first()
                flash('COMMONER, can I write articles? %r' % self.can(Permission.WRITE_ARTICLES))

        self.location='Aberdeen'
        #self.follow(self)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'verify' : self.id})

    def verify(self, token, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        try:
            data = s.loads(token)
            if data.get('verify') != self.id:
                return False
        except Exception:
            return False
        else:
            self.confirmed = True
            db.session.add(self)
            return True

    def measure_time(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def avatar(self, size=230, default='retro', rating='g'):
        """size is in pixels"""
        url='http://gravatar.com/avatar'
        # md hash tag of the user's email address
        hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default, rating=rating)

    def verify_password(self, value):
        return check_password_hash(self.password_hash, value)

    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def save_match(self, match):
        if not self.has_match_saved(match):
            #self.saved_matches.append(match)
            s = SavedForLater(user=self, match=match)
            db.session.add(self)

    def remove_match(self, match):
        s = self.saved_matches.filter_by(match_id=match.id).first()
            #print 'It is!'
            #self.saved_matches.remove(match)
        if s:
            db.session.delete(s)

    def has_match_saved(self, match):
        return self.saved_matches.filter_by(match_id=match.id).first() is not None

    def has_match_committed(self, match):
        sm = self.saved_matches.filter_by(match_id=match.id).first()
        if sm is not None:
            return sm.committed

    def list_matches(self, *args, **kwargs):
        """insert your match id as a parameter in case you want to see only one match"""
        return [match
                for match in self.saved_matches.filter_by(**kwargs).order_by(*args)
        ]

    def list_prediction_settings(self, **kwargs):
        """insert your module id as a parameter in case you want to see only one module value"""
        return [settings
                for settings in self.prediction_settings.filter_by(**kwargs)
                ]

    def list_match_specific_settings(self, **kwargs):
        """insert your match id AND module id as a parameter in case you want to see only one module value"""
        return [settings
                for settings in self.match_specific_settings.filter_by(**kwargs)
                ]

    @property
    def list_new_messages(self):
        return self.messages.filter_by(new=True).all()

    def delete_messages(self):
        msgs=self.messages.all()
        if msgs:
            for msg in msgs:
                db.session.delete(msg)

    def list_won_bets(self, match):
        return []

    # using property because I want to protect the password
    @property
    def password(self):
        raise AttributeError('This property cant be accessed!')

    @password.setter
    def password(self, value):
        self.password_hash = generate_password_hash(value)


    def __repr__(self):
        """user representation"""
        return '<User (username={}, real_name={}, location={})>'\
            .format(self.username,
                    self.real_name,
                    self.location
        )


class AnonymousUser(AnonymousUserMixin):
    """class is assigned to the current user when the user is not logged in"""
    def can(self):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser

# callback function that loads a user from the database
# user ids in flask-login are always unicode strings, needs to be converted to an
# int
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Team(db.Model):
    """represents a football team"""
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    hometeam = db.relationship('Match', backref=db.backref('hometeam'), lazy='dynamic',
                               primaryjoin="Match.hometeam_id==Team.id")
    awayteam = db.relationship('Match', backref=db.backref('awayteam'), lazy='dynamic',
                               primaryjoin="Match.awayteam_id==Team.id")

    @property
    def position(self):
       current_position = faw.league_table[str(self.id)].position
       return current_position

    @property
    def form(self):
        current_form = faw.league_table[str(self.id)].form
        return current_form

    @property
    def last_match(self):
        """ Previous match result """
        last_match_data = faw.form_and_tendency(self.id)[0]

        return last_match_data

    @property
    def last_matches(self):
        """ Last 6 matches for the team """
        last_matches_data = faw.form_and_tendency(self.id)[:6]

        return last_matches_data

    @property
    def form_last_6(self):
        """
        Create a tuple with the current values (wins, losses) for 6 last matches
        :return league_table tuple
        """
        # matches data for the team
        TeamInfo = namedtuple('TeamInfo', 'name w d l gf ga gd pts form')
        matches_data = faw.form_and_tendency(self.id)[:6]

        wins = sum([1 for match in matches_data if match.outcome == 'W'])
        draws = sum([1 for match in matches_data if match.outcome == 'D'])
        losses = sum([1 for match in matches_data if match.outcome == 'L'])

        gf = 0
        ga = 0
        form = ''

        # t=Team.query.first()
        for m in matches_data:
            # finding goals for, if team is at home, sum all goals that hometeam scored
            # this team is at home
            if m.hometeam_id != m.opponent_id:
                ga += m.awayteam_score
                gf += m.hometeam_score
            else:
                # this team is away
                ga += m.hometeam_score
                gf += m.awayteam_score
            if m.outcome == 'W':
                form += 'W'
            elif m.outcome == 'D':
                form += 'D'
            else:
                form += 'L'

        gd = gf - ga

        league_table = TeamInfo(self.name, wins, draws, losses, gf, ga, gd, 3 * wins + 1 * draws, form)

        return league_table

    @property
    def form_home_away(self):
        """
        Create two tuples with the current values (wins, losses) for 6 last matches
        representing home/away performance for a team
        :return a tuple containing two league_table tuples
        """
        # the main tuple to be returned
        HomeAway = namedtuple('HomeAway', 'home away')
        TeamInfo = namedtuple('TeamInfo', 'name w d l gf ga gd pts form')
        matches_data = faw.form_and_tendency(self.id)
        home = away= 0
        home_wins = away_wins = 0
        home_losses = away_losses = 0
        home_draws = away_draws = 0
        home_gf = away_gf = 0
        home_ga = away_ga = 0
        home_form = away_form = ''

        for m in matches_data:
            if home == 6 and away == 6:
                break
            if m.home:
                if home == 6:
                    continue
                else:
                    home += 1
                if m.outcome == 'W':
                    home_wins += 1
                    home_form += 'W'
                elif m.outcome == 'L':
                    home_losses += 1
                    home_form += 'L'
                else:
                    home_draws += 1
                    home_form += 'D'
                # finding goals for, if team is at home, sum all goals that hometeam scored
                # this team is at home
                home_gf += m.hometeam_score
                home_ga += m.awayteam_score
            else:
                if away == 6:
                    continue
                else:
                    away += 1

                if m.outcome == 'W':
                    away_wins += 1
                    away_form += 'W'
                elif m.outcome == 'L':
                    away_losses += 1
                    away_form += 'L'
                else:
                    away_draws += 1
                    away_form += 'D'
                away_gf += m.awayteam_score
                away_ga += m.hometeam_score

        home = TeamInfo(self.name, home_wins, home_draws, home_losses, home_gf, home_ga, home_gf-home_ga,
                        3 * home_wins + 1 * home_draws, home_form)
        away = TeamInfo(self.name, away_wins, away_draws, away_losses, away_gf, away_ga, away_gf-away_ga,
                        3 * away_wins + 1 * away_draws, away_form)

        return HomeAway(home, away)

    def __init__(self, **kwargs):
        super(Team, self).__init__(**kwargs)


    @staticmethod
    def insert_teams():
        """
        @param id_names: Dictionary with the ids and names of the league teams
        """
        ids_names = faw.ids_names

        for id, name in ids_names.items():
            team = Team.query.filter_by(id=id).first()
            if team is None:
                team = Team()
            team.id = id
            team.name = name
            db.session.add(team)
        db.session.commit()
        db.session.close()


    @staticmethod
    def league_table():
        league_table = faw.league_table

        return league_table

    def __repr__(self):
        return '<Team> {}/{} league_position:{}'.format(
            self.id,
            self.name,
            self.position
            )

class Match(db.Model):
    """represents a football match"""
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(16))
    time = db.Column(db.String(16))
    date_stamp = db.Column(db.Date())
    time_stamp = db.Column(db.Time())
    was_played = db.Column(db.Boolean, unique=False, default=False)
    hometeam_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    awayteam_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    hometeam_score = db.Column(db.String(4))
    awayteam_score = db.Column(db.String(4))
    saved_for_later = db.relationship('SavedForLater', backref='saved_matches', lazy='dynamic')
    users_who_saved_match = association_proxy('saved_by_users', 'users_id')

    @staticmethod
    def update_all_matches():
        """Inserting all the matches to the database"""
        anchor = 0
        matches = faw.all_matches

        if Match.query.all():
            # there are matches in the database

            # there are unplayed matches in the database
            if Match.query.filter_by(was_played=False).all():
                # we are updating all matches staring from the first unplayed
                anchor = Match.query.filter_by(was_played=False).first().id
            elif faw.played_matches:
                # there are no unplayed matches in the database, all of them are played
                # no need to update, anchor is the very last match in the database
                anchor = Match.query.order_by(Match.id.desc()).first().id
        else:
            # there are no matches in the database
            # just add them all, start from 0
            anchor = 0

        for m in matches:
            if m.id < anchor:
                continue

            # find the match in the database
            match = Match.query.filter_by(id=m.id).first()

            # if not in the database, create a new match
            if match is None:
                match = Match(id=m.id, hometeam_id=m.hometeam_id, awayteam_id=m.awayteam_id, date=m.date, time=m.time,
                              date_stamp=m.date_stamp, time_stamp=m.time_stamp)

            match.hometeam_score = m.hometeam_score
            match.awayteam_score = m.awayteam_score

            if m.ft_score != '':
                match.was_played = True
            else:
                match.was_played = False

            db.session.add(match)

        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise
        finally:
            db.session.close()

    @property
    def prediction_league_position(self):
        """calculate the winner for the league position prediction module
           ((20-homeposition)-(20-awayposition))/19
           if prediction value is positive, it increases the probability of hometeam to win
           if it is negative, it increases the probability of awayteam to win
        """
        hometeam_diff = 20 - int(self.hometeam.position)
        awayteam_diff = 20 - int(self.awayteam.position)
        prediction_value = (hometeam_diff-awayteam_diff) * 100 / 19

        return prediction_value

    @property
    def prediction_form(self):
        """calculate the winner for the form prediction module
           (hometeam points - awayteam points)/18
           18 is the maximum amount of points a team can achieve
           if prediction value is positive, it increases the probability of hometeam to win
           if it is negative, it increases the probability of awayteam to win
        """
        hometeam_pts = self.hometeam.form_last_6.pts
        awayteam_pts = self.awayteam.form_last_6.pts
        prediction_value = (hometeam_pts - awayteam_pts) * 100 / 18

        return prediction_value


    @property
    def prediction_homeaway(self):
        """calculate the winner for the home away module
           (hometeam at home points - awayteam away points)/18
           18 is the maximum amount of points a team can achieve
           if prediction value is positive, it increases the probability of hometeam to win
           if it is negative, it increases the probability of awayteam to win
        """
        # hometeam's performance at home (last 6 matches)
        hometeam_home_pts = self.hometeam.form_home_away.home.pts

        # awayteam's performance away (last 6 matches)
        awayteam_away_pts = self.awayteam.form_home_away.away.pts

        prediction_value = (hometeam_home_pts - awayteam_away_pts) * 100 / 18

        return prediction_value

    @staticmethod
    def predicted_winner(match, user=None, user_hunch=-1):
        """predicted winner based on user prediction settings"""
        total_weight = 0

        # these are the percentages (floats)
        module_values = [match.prediction_league_position,
                         match.prediction_form,
                         match.prediction_homeaway,
                         user_hunch]
        prediction_modules = PredictionModule.query.all()
        module_length = len(prediction_modules)
        Winner = namedtuple("Winner", "team_winner_id, team_winner_name, probability")
        user_prediction_settings=[]
        user_match_prediction_settings=[]

        if not user is None:
            user_prediction_settings = user.list_prediction_settings()
            user_match_prediction_settings = user.list_match_specific_settings(match_id=match.id)

        # we use module_length-1 because user hunch settings can be only used for a match specific settings
        # user hunch cannot be set by default!!
        for i in range(0, module_length - 1):
            if user_match_prediction_settings:
                #print('User saved match specific settings')
                weight = user_match_prediction_settings[i].weight

            elif user_prediction_settings:
                #print('User settings provided, use default USER settings')
                weight = user_prediction_settings[i].weight
            else:
                #print('No user settings provided, use default SYSTEM settings')
                weight = prediction_modules[i].weight

            total_weight += module_values[i] * float(weight)
            #print module_values[i], float(weight)

        if user_hunch != -1:
            # user hunch is always the last module
            c = len(module_values) - 1
            if user_match_prediction_settings:
                # replace with augmented assignment
                total_weight += user_hunch * user_match_prediction_settings[c].weight
            elif user_prediction_settings:
                total_weight += user_hunch * user_prediction_settings[c].weight
            else:
                total_weight += user_hunch * prediction_modules[c].weight

        winner_probability = total_weight

        if total_weight > 0:
            return Winner(match.hometeam.id, match.hometeam.name, winner_probability)
        elif total_weight < 0:
            return Winner(match.awayteam.id, match.awayteam.name, -1 * winner_probability)
        else:
            return Winner(-1, 'Draw', 0)


    @property
    def actual_winner(self):
        """who actually won the match?"""
        if self.hometeam_score != '?' and self.awayteam_score != '?':
            if int(self.hometeam_score) > int(self.awayteam_score):
                return self.hometeam_id
            elif int(self.hometeam_score) == int(self.awayteam_score):
                return -1
            else:
                return self.awayteam_id
    @property
    def actual_winner_name(self):
        if self.actual_winner == -1:
            return None
        else:
            return Team.query.filter_by(id=self.actual_winner).first().name

    def __repr__(self):
        return "<Match> date:{} time: {} id:{} {}/{} was_played {} score: {}:{}".format(
            self.date,
            self.time,
            self.id,
            self.hometeam_id,
            self.awayteam_id,
            self.was_played,
            self.hometeam_score,
            self.awayteam_score
        )

db.event.listen(Match.was_played, 'set', SavedForLater.on_changed_match_status, retval=False)

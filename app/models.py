from . import db, faw
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app, request
from . import login_manager
from datetime import datetime
import hashlib
from flask import flash
from markdown import markdown
import bleach
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relation
from collections import namedtuple



"""Database models representation"""
class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

# Defining models
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


'''class ModelUsingMarkdown(db.Model):

    @staticmethod
    def on_changed_body(self, target, value, old_value, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']

        target.body_html = bleach.linkify (bleach.clean(markdown(value, output_format='html')))
'''


'''class Post(db.Model):
    __tablename__='posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime(), index=True, default = datetime.utcnow)
    edited = db.Column(db.Boolean, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')


    @staticmethod
    def on_changed_body(self, target, value, old_value, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']

        target.body_html = bleach.linkify (bleach.clean(markdown(value, output_format='html')))

    def __repr__(self):
        'posts representation'
        return '<Post %r> %r %r' % (self.body_html, self.author_id, self.timestamp)

#db.event.listen(Post.body, 'set', Post.on_changed_body)

class Comments(db.Model):
        __tablename__ = 'comments'
        id = db.Column(db.Integer, primary_key=True)
        body = db.Column(db.Text)
        body_html = db.Column(db.Text)
        timestamp = db.Column(db.DateTime(), index=True, default = datetime.utcnow)

        #will be used by moderators to supress comments that are offensive
        disabled = db.Column(db.Boolean, default=False)
        edited = db.Column(db.Boolean, default=False)
        author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
        post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))


        @staticmethod
        def on_changed_body(self, target, value, old_value, initiator):
            allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']

            target.body_html = bleach.linkify (bleach.clean(
                markdown(value, output_format='html'),
                tags=allowed_tags,
                strip=True
            ))

        def __repr__(self):
            'comment representation'
            return '<Comment %r> %r %r' % (self.body, self.author_id, self.timestamp)

#db.event.listen(Comment.body, 'set', Comment.on_changed_body)
'''
class PredictionModule(db.Model):
    __tablename__ = 'prediction_modules'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    description = db.Column(db.String(64))
    default_weight = db.Column(db.Float)

    @staticmethod
    def insert_modules():
        modules = {
            'league_position': 0.50,
            'form': 0.30,
            'home_away': 0.20
        }
        for m in modules:
            module = PredictionModule.query.filter_by(name=m).first()
            if module is None:
                module = PredictionModule(name=m)
            module.default_weight = modules[m]
            db.session.add(module)
        db.session.commit()
        db.session.close()

    def __repr__(self):
        return "<PredictionModule> id:{} name:{} weight:{}".format(
                self.id,
                self.name,
                self.default_weight
        )

class ModuleUserSettings(db.Model):
    'set custom user %'
    __tablename__='moduleusersettings'
    user_id=db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('prediction_modules.id'), primary_key=True)
    weight = db.Column(db.Float)
    user = db.relationship("User", backref = "user_assocs")

    def __repr__(self):
        return "<ModuleUserSettings> user_id: {}, module_id: {}, weight:{}".format(
            self.user_id,
            self.module_id,
            self.weight
        )


class ModuleUserMatchSettings(db.Model):
    'set custom user % for each match'
    __tablename__='moduleusermatchsettings'
    user_id=db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    match_id=db.Column(db.Integer, db.ForeignKey('savedforlater.match_id'), primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('prediction_modules.id'), primary_key=True)
    weight = db.Column(db.Float)
    user = db.relationship("User", backref = "user_match_assoc")

    def __repr__(self):
        return "<ModuleUserMatchSettings> user_id: {}/match_id: {} (module_id: {}, weight:{})".format(
            self.user_id,
            self.match_id,
            self.module_id,
            self.weight
        )


class SavedForLater(db.Model):
    'matches saved by users, association table'
    __tablename__='savedforlater'
    users_id=db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    match_id=db.Column(db.Integer, db.ForeignKey('matches.id'), primary_key=True)
    committed = db.Column(db.Boolean, default=False)
    weight_league_position = db.Column(db.Float, default=None)
    weight_form = db.Column(db.Float, default=None)
    weight_home_away = db.Column(db.Float, default=None)
    predicted_winner = db.Column(db.Integer, default=None)
    match = db.relationship( "Match", backref = "user_assocs")
    bettor = db.relationship( "User", backref="bettor")
    match_specific_settings = db.relationship( "ModuleUserMatchSettings", backref="settings")

    savedmatch_played = association_proxy('match', 'played')

    def __repr__(self):
        return "<SavedForLater> userid: {}, matchid: {}, committed:{}, predicted_winner:{}".format(
            self.users_id,
            self.match_id,
            self.committed,
            self.predicted_winner
        )

    @staticmethod
    def on_changed_match_status(target, value, old_value, initiator):
        all_savedmatches=SavedForLater.query.all()

        #make sure the match is not just overwritten and win/loss points are re-added for the second time
        if value is True and old_value is False:

            # looping through all occurences of this match being saved by any user
            for savedmatch in all_savedmatches:

                if(savedmatch.match==target and savedmatch.committed):

                    print "users having this match saved and committed: %s" % savedmatch.bettor

                    if savedmatch.match.actual_winner != savedmatch.predicted_winner and not savedmatch.match.actual_winner is None:
                        print "old value: " + str(savedmatch.bettor.win_points)
                        savedmatch.bettor.win_points = savedmatch.bettor.win_points+1
                        print ('Win user points updated')
                        print "new value: " + str(savedmatch.bettor.win_points)

                    elif(savedmatch.match.actual_winner is None):
                        return False
                    else:
                        print "old value: " + str(savedmatch.bettor.loss_points)

                        savedmatch.bettor.loss_points = savedmatch.bettor.loss_points+1
                        print "new value: " + str(savedmatch.bettor.loss_points)

                        print ('Win user points updated')

                    db.session.add(savedmatch.bettor)

            #try:
            db.session.commit()
            #except:
                #db.session.rollback()
            #   raise



        #m=Match.query.filter_by(id=1963811).first()
        # update user's LSP
        # u=User.query.all()[0]
        #  match1=u.list_matches()[0]
        # match1.match.played=True

class Follow(db.Model):
    'following-follower feature'
    __tablename__='follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


"""class Performance(db.Model):
    __tablename__ = 'user_performance'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    win_points = db.Column(db.Integer, default=0)
    loss_points = db.Column(db.Integer, default=0)
    lsp = db.Column(db.Float, default=0)

    def __repr__(self):
        'user performance representation'
        return '<Performace (user_id={}, wins={}, losses={}, lsp={})>'\
            .format(self.user_id,
                    self.win_points,
                    self.loss_points,
                    self.lsp
        )"""


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

    #performance = db.relationship("Performance", uselist=True, backref="performing_user")


    #posts = db.relationship('Post', backref='author', lazy='dynamic')
    #comments = db.relationship('Comment', backref='author', lazy='dynamic')

    #foreign key is an optional argument, backreferences in this case are applied to the Follow model,
    #not to each other

    # I am followed by those users
    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    # I follow those users
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    # I saved those matches for a review
    saved_matches = db.relationship('SavedForLater',
                                    foreign_keys=[SavedForLater.users_id],
                                    backref=db.backref('user', lazy='joined'),
                                    lazy='dynamic',
                                    cascade='all, delete-orphan'
                                    )

    prediction_settings = db.relationship('ModuleUserSettings',
                                          backref='bettor',
                                          foreign_keys=[ModuleUserSettings.user_id], lazy='dynamic')

    match_specific_settings = db.relationship('ModuleUserMatchSettings',
                                          backref='bettor_match',
                                          foreign_keys=[ModuleUserMatchSettings.user_id, PredictionModule.id],
                                          lazy='dynamic')


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
        #self.create_performance()


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
        #db.session.commit()
        #db.session.close()

    def avatar(self, size=230, default='retro', rating='g'):
        'size is in pixels'
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

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    '''def create_performance(self):
        #if not self.performance:
        flash('Creating performance')

        #NOT CREATING PERFORMANCE!!
        p=Performance(user_id=self.id)
        db.session.add(p)
        db.session.commit()'''

    def unfollow(self, user):
        f=self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None


    def is_followed_by(self, user):
        return self.follower.filter_by(follower_id=user.user_id).first() is not None

    def save_match(self, match):
        '''add restriction to only save matches that have not yet been played'''
        if not self.is_match_saved(match):
            #self.saved_matches.append(match)
            s = SavedForLater(user=self, match=match)
            db.session.add(self)

    def remove_match(self, match):
        s = self.saved_matches.filter_by(match_id=match.id).first()
            #print 'It is!'
            #self.saved_matches.remove(match)
        if s:
            db.session.delete(s)

    def is_match_saved(self, match):
        return self.saved_matches.filter_by(match_id=match.id).first() is not None

    'insert your match id as a parameter in case you want to see only one match'
    def list_matches(self, **kwargs):
        return [match
                for match in self.saved_matches.filter_by(**kwargs)
        ]

    'insert your module id as a parameter in case you want to see only one module value'

    def list_prediction_settings(self, **kwargs):
       return [settings
                for settings in self.prediction_settings.filter_by(**kwargs)
                ]

    def list_match_specific_settings(self, **kwargs):
        return [settings
                for settings in self.match_specific_settings.filter_by(**kwargs)
                ]

    '''def user_betting_settings(self, match):
        if not self.is_match_saved(match):
            #self.saved_matches.append(match)
            s = SavedForLater(user=self, match=match)
            db.session.add(self)'''

    # using property because I want to protect the password
    @property
    def password(self):
        raise AttributeError('This property cant be accessed!')

    @password.setter
    def password(self, value):
        self.password_hash = generate_password_hash(value)

    # self-follow for users that are already in the database
    @staticmethod
    def update_self_follows():
        for user in User.query.all():
            user.follow(user)
            db.session.add(user)
            print user.followers.count()
        #db.session.commit()
        #db.session.close()

    def __repr__(self):
        'user representation'
        return '<User (username={}, real_name={}, location={})>'\
            .format(self.username,
                    self.real_name,
                    self.location
        )

class AnonymousUser(AnonymousUserMixin):
    'class is assigned to the current user when the user is not logged in'
    def can(self):
        return False

    def is_administrator(self):
        return False

class ReadOnly(AttributeError):
        'custom exception'
        pass

login_manager.anonymous_user = AnonymousUser

# callback function that loads a user from the database
# user ids in flask-login are always unicode strings, needs to be converted to an
# int
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Team(db.Model):
    '''represents a football team'''
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    hometeam = db.relationship('Match', backref=db.backref('hometeam'), lazy='dynamic', primaryjoin="Match.hometeam_id==Team.id")
    awayteam = db.relationship('Match', backref=db.backref('awayteam'), lazy='dynamic', primaryjoin="Match.awayteam_id==Team.id")

    @property
    def position(self):
       current_position = faw.league_table[str(self.id)].position
       return current_position

    @property
    def form(self):
       current_form = faw.league_table[str(self.id)].form
       return current_form

    def __init__(self, **kwargs):
        super(Team, self).__init__(**kwargs)
        #self.league_position = 1
        '''if self.role is None:
            if self.email == 'shchukina.marina@gmail.com': #current_app.config['FOOTY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
                flash('SUPER POWERS, can I write articles? %r' % self.can(Permission.WRITE_ARTICLES))
            else:
                self.role = Role.query.filter_by(default=True).first()
                flash('COMMONER, can I write articles? %r' % self.can(Permission.WRITE_ARTICLES))'''

        #self.location='Aberdeen'
        #self.follow(self)

    @staticmethod
    def insert_teams():
        '''
        @param id_names: Dictionary with the ids and names of the league teams
        '''
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

    def __repr__(self):
        return '<Team> {}/{} league_position:{}'.format(
            self.id,
            self.name,
            self.position
            )

class Match(db.Model):
    'represents a football match'
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(16))
    time = db.Column(db.String(16))
    date_stamp = db.Column(db.Date())
    time_stamp = db.Column(db.Time())
    played = db.Column(db.Boolean)
    hometeam_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    awayteam_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    hometeam_score = db.Column(db.String(4))
    awayteam_score = db.Column(db.String(4))
    users = db.relationship('SavedForLater', backref='saved_matches', lazy='dynamic')
    comments = db.relationship('Comment', backref='match', lazy='dynamic')

    @staticmethod
    def update_all_matches():
        'Inserting all the matches to the database'
        matches = faw.all_matches

        for m in matches:
            # hope this will not be a bottleneck, find a smarter way to check what is already in the database??
            #store last inserted match id in a variable?

            'find the match in the database'
            match = Match.query.filter_by(id=m.id).first()

            'if not in the database, create a new match'
            if match is None:
                match = Match(id=m.id, hometeam_id = m.hometeam_id, awayteam_id = m.awayteam_id, date = m.date, time = m.time,
                        date_stamp = m.date_stamp, time_stamp = m.time_stamp)

                match.hometeam_score = m.hometeam_score
                match.awayteam_score = m.awayteam_score

                # if match is newly created
                if(m.ft_score != ''):
                    match.played = True
                else:
                    match.played = False

            # if match is updated from not played to played
            if(not match.played and m.ft_score != ''):
                match.played = True

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
        'calculate the winner for the league position prediction module'

        if (int(self.hometeam.position) < int(self.awayteam.position)):
            return self.hometeam
        else:
            return self.awayteam

    @property
    def prediction_homeaway(self):
        '''calculate the winner for the home/away prediction module
            to be improved
        '''

        return self.hometeam

    @property
    def prediction_form(self):
        '''calculate the winner for the form prediction module
            to be improved
        '''

        return self.awayteam

    @staticmethod
    def predicted_winner(match, user=None):

        total_weight = 0
        module_winners = [match.prediction_league_position, match.prediction_form, match.prediction_homeaway]
        prediction_modules = PredictionModule.query.all()
        module_length = len(prediction_modules)
        Winner = namedtuple("Winner", "team_winner_id, team_winner_name, probability")
        user_prediction_settings=[]
        user_match_prediction_settings=[]

        if not user is None:
            user_prediction_settings = user.list_prediction_settings()
            user_match_prediction_settings = user.list_match_specific_settings(match_id=match.id)


        for i in range( 0, module_length ):
            if user_match_prediction_settings:
                print('User saved match specific settings')
                weight=user_match_prediction_settings[i].weight

            elif (user_prediction_settings):
                print('User settings provided, use default USER settings')
                #why outputs unicode instead of float???
                weight=user_prediction_settings[i].weight
            else:
                print('No user settings provided, use default SYSTEM settings')
                weight=prediction_modules[i].default_weight


            if( match.hometeam_id == module_winners[i].id ):
                total_weight += float(weight)


        winner_probability = total_weight

        if total_weight > 0.5:
            return Winner(match.hometeam.id, match.hometeam.name, winner_probability)
        elif total_weight < 0.5:
            return Winner(match.hometeam.id, match.awayteam.name, 1-winner_probability)
        else:
            return (-1, 'To Close To Call...', 0.5)

    'who won the match?'
    @property
    def actual_winner(self):
        if self.hometeam_score != '?' and self.awayteam_score != '?':
            if (int(self.hometeam_score) > int(self.awayteam_score)):
                return self.hometeam_id
            elif(int(self.hometeam_score) == int(self.awayteam_score)):
                return '-1'
            else:
                return self.awayteam_id

    def __repr__(self):
        return "<Match> date:{} id:{} {}/{} Played? {} Score: {}:{}".format(
            self.date,
            self.id,
            self.hometeam_id,
            self.awayteam_id,
            self.played,
            self.hometeam_score,
            self.awayteam_score
            )

db.event.listen(Match.played, 'set', SavedForLater.on_changed_match_status, retval=True)


class Comment(db.Model):
        __tablename__ = 'comments'
        id = db.Column(db.Integer, primary_key=True)
        body = db.Column(db.Text)
        timestamp = db.Column(db.DateTime(), index=True, default = datetime.utcnow)

        #will be used by moderators to supress comments that are offensive
        disabled = db.Column(db.Boolean, default=False)
        edited = db.Column(db.Boolean, default=False)
        author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
        match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))

        def __repr__(self):
            return "<Comment> id:{}".format(
                self.id
            )
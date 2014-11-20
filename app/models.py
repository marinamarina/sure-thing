from . import db
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
from . import faw


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

class Game(db.Model):
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

class Follow(db.Model):
    __tablename__='follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User (UserMixin, db.Model):
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
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    #posts = db.relationship('Post', backref='author', lazy='dynamic')
    #comments = db.relationship('Comment', backref='author', lazy='dynamic')

    #foreign key is an optional argument, backreferences in this case are applied to the Follow model,
    #not to each other

    #I am followed by those users
    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    #I follow those users
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        print Role.query.filter_by(permissions=0xff).first()
        if self.role is None:
            if self.email == 'shchukina.marina@gmail.com': #current_app.config['FOOTY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
                flash('SUPER POWERS, can I write articles? %r' % self.can(Permission.WRITE_ARTICLES))
            else:
                self.role = Role.query.filter_by(default=True).first()
                flash('COMMONER, can I write articles? %r' % self.can(Permission.WRITE_ARTICLES))

            self.location='Old Aberdeen'
            self.follow(self)

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

    def unfollow(self, user):

        f=self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None


    def is_followed_by(self, user):
        return self.follower.filter_by(follower_id=user.user_id).first() is not None

    '''@property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id).filter(Follow.follower_id==self.id)'''


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
        db.session.commit()
        db.session.close()

    def __repr__(self):
        'user representation'
        return '<User (username={}, real_name={}, location={})>'.format(self.username, self.real_name, self.location)

class AnonymousUser(AnonymousUserMixin):
    'class is assigned to the current user when the user is not logged in'
    def can(self):
        return False

    def is_administrator(self):
        return False

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
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
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    league_position = db.Column(db.Integer, unique=True)

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

    def __repr__(self):
        return '<TEAM> {}/{} league_position:{}'.format(
            self.id,
            self.name,
            self.league_position
            )

class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime())
    time = db.Column(db.DateTime())
    played = db.Column(db.Boolean)
    hometeam_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    awayteam_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    hometeam_score = db.Column(db.Integer)
    awayteam_score = db.Column(db.Integer)
    #users = db.relationship('User', backref='role', lazy='dynamic')

    '''
    @staticmethod
    def insert_old_matches():
        pass
        games = {
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
        '''

    def __repr__(self):
        return "<Match> date:{} home_team_id:{} away_team_id:{} score:{}-{} played?:{}".format(
            self.date,
            self.hometeam_id,
            self.awayteam_id,
            self.hometeam_score,
            self.awayteam_score,
            self.played
            )

'''class Follow(db.Model):
    __tablename__='follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

registrations  =  db.Table('registrations' ,
db . Column ( 'student_id' ,  db . Integer ,  db . ForeignKey ( 'students.id' )),
db . Column ( 'class_id' ,  db . Integer ,  db . ForeignKey ( 'classes.id' )) )

class Play (db.Model):
    __tablename='plays'

    localteam_id = db.Column(db.Integer, db.ForeignKey('matches.id')
    Match,match_table,properties={
      'team1':relationship(Team, foreign_keys=[match_table.c.matchTeam1],
          primaryjoin=match_table.c.matchTeam1==team_table.teamID),
      'team2':relationship(Team, foreign_keys=[match_table.c.matchTeam2],
          primaryjoin=match_table.c.matchTeam2==team_table.teamID),
    })'''


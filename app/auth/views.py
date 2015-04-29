from flask import url_for, render_template, redirect, request, flash
from . import auth
from flask_login import login_user, current_user, logout_user, login_required
from ..main.forms import LoginForm, RegistrationForm, PasswordChangeForm, EditProfile,\
    AdminManageProfiles
from ..models import User
from app import db
from ..email import send_email
from sqlalchemy.exc import IntegrityError
from flask import abort

@auth.before_app_request
def before_request():
    pass
    # still todo
    """if current_user.is_authenticated():

        if not current_user.confirmed \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))"""

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    #is form submission valid?
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()

        if user is None:
            flash('There is not a such user in database')

        if user is not None and user.verify_password(form.password.data):

            try:
                login_user(user, remember=form.rememberMe.data)
            except IntegrityError, e:
                print "IntegrityError", e
                flash ("You have NOT been authorized!")
            else:
                pass
                #flash ("You have NOT been authorized!")
            finally:
                flash ("You have now been authorized!" + str(current_user.role))
                return redirect(request.args.get('next') or url_for('main.index'))

        flash('Invalid username or password.')


    return render_template('auth/login.html', form = form, title='Sign In')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out!")
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated():
            logout_user()

    form = RegistrationForm()

    #is form submission valid?
    if(form.validate_on_submit()):
        #if form.email.data
        user = User(email = form.email.data,
                    username = form.username.data,
                    password = form.password.data)

        db.session.add(user)
        db.session.commit()
        #print("User with username {} cannot be registered".format(form.username.data))

        # generate a token
        token = user.generate_confirmation_token()

        #url = su.encode_url(12)
        #uid = su.decode_url(url)
        send_email(user.email, 'Please, verify your account', 'auth/email/verify', user=user, token=token)
        flash ('Verification email has been sent to your email.')

        return redirect( url_for('main.index') )
    else:
        print("Error, you have not been registered!")

    return render_template('auth/register.html', form = form, title='Register')

@auth.route('/verify/<token>')
@login_required
def verify(token):
    if current_user.is_anonymous():
        return redirect(url_for('auth.login'))

    if current_user.confirmed:
        return redirect(url_for('main.index'))
    elif current_user.verify(token):
        flash('Thank you for verifying your account!')
    else:
        flash('The confirmation token has expired!')
    return redirect(url_for('main.index'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous() or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/verify')
@login_required
def resend_verification_email():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Please, verify your account', 'auth/email/verify', user=current_user, token=token)
    flash ('Verification email has been sent to your email.')

    return redirect(url_for('main.index'))

@auth.route('/profile/<user>', methods=['GET', 'POST'])
@login_required
def profile(user):
    user = User.query.filter_by(username=user).first()
    if user is None:
        abort(404)
    return render_template('auth/profile.html', user=user, title='My profile', current_user = current_user)


@auth.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    me = current_user
    form = EditProfile()

    if form.validate_on_submit():
        current_user.real_name = form.real_name.data
        current_user.location = form.location.data
        current_user.fav_team = form.fav_team.data
        current_user.about_me = form.about_me.data

        db.session.add(me)
        db.session.commit()

        flash('Your profile has been edited!' + me.__repr__())

        return redirect( url_for('auth.user', username=me.username) )

    return render_template('auth/edit_profile.html', user=me, form=form, title='Edit profile')

@auth.route('/change_password.html', methods=['GET', 'POST'])
@login_required
def change_password():
    form = PasswordChangeForm()

    if form.validate_on_submit():
        if (current_user.verify_password(form.old_password.data)):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            flash('Your password has been changed!')
            return redirect( url_for('main.index') )
        else:
            flash('Incorrect password!')

    return render_template('auth/change_password.html', title='Change Password', user=current_user, form=form)

from flask import url_for, render_template, redirect, request, flash
from . import auth
from flask_login import login_user, current_user, logout_user, login_required
from ..main.forms import LoginForm, RegistrationForm, PasswordChangeForm, ManageProfile, AdminManageProfiles
from ..models import User
from app import db
from ..email import send_email
from sqlalchemy.exc import IntegrityError
from flask import abort
from ..decorators_me import admin_required

@auth.before_app_request
def before_request():

    '''if current_user.is_authenticated():
        current_user.measure_time()

        if not current_user.confirmed and request.endpoint[0:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))'''


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

'''The page that is presented to unconfirmed users just renders a template that gives users instructions
for how to confirm their account and offers a link to request a new confirmation email,
in case the original email was lost. The route that resends the confirmation email is shown in Example 8-23.'''
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

@auth.route('/manage_profile', methods=['GET', 'POST'])
@login_required
def manage_profile():
    form = ManageProfile()

    if form.validate_on_submit():
        current_user.real_name = form.real_name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data

        db.session.add(current_user)
        db.session.commit()

        flash('Your profile has been edited!' + current_user.__repr__())
        return redirect( url_for('auth.profile', user=current_user.username) )

    return render_template('auth/manage_profile.html', title='Manage profile', form=form)

@auth.route('/admin_manage_profiles/<int:id>', methods=['GET', 'POST'])
@login_required
#@admin_required
def admin_manage_profiles(id):
    user = User.query.get_or_404(id)
    form = AdminManageProfiles(user=user)

    flash(user.username + user.real_name)
    if form.validate_on_submit():
        flash('Form is valid')
        user.username = form.username.data
        user.email = form.email.data
        user.confirmed = form.confirmed.data
        user.real_name = form.real_name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        user.role = form.role.data

        #db.session.add(user)
        #db.session.commit()

        flash('You have edited the users profile!' + user.__repr__())
        return redirect( url_for('.user', username=user.username) )
    form.confirmed.data = user.confirmed

    return render_template('auth/admin_manage_profiles.html', title='Admin manage profile', form=form, user=user)

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

    return render_template('auth/change_password.html', title='Change Password', form=form)
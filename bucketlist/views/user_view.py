# This is where the routes are defined.
# It may be split into a package of its own (yourapp/views/) with related views
# grouped together into modules.

import os

from flask import Flask
from flask import redirect, url_for, render_template
from flask_login import login_required, current_user

from bucketlist import app
# import bucketlist
from bucketlist.forms import RegistrationForm, EmailForm, PasswordForm
# from .models import db, Role, User, Bucketlist
# from .util import ts, send_email


@app.route('/user/register', methods=['GET', 'POST'])
def register():
    """The application needs to register users before they can log in"""

        # user = User(form.username.data,
        #             form.email.data,
        #             bcrypt.generate_password_hash(form.password.data),
        #             'User'
        #             )

        # # User requires to authenticate account before account is activated
        # user.active = False
        # try:
        #     db.session.add(user)
        #     db.session.commit()
        # except:
        #     db.session.flush()
        #     db.rollback()



@app.route('/confirm/<token>')
def confirm_email(token):
    """Confirm user email"""

    # Check that the token is valid
    try:
        email = ts.loads(token, salt="email-confirm-key", max_age=86400)
    except:
        abort(404)

    user = User.query.filter_by(email=email).first_or_404()

    user.active = True

    db.session.add(user)
    db.session.commit()

    return redirect(url_for('login'))


@app.route("/user/login", methods=["GET", "POST"])
def login():
    """For GET requests, display the login form. For POSTS, login the current user
    by processing the form."""
    print (db)
    if request.method == 'GET':
        return render_template("login.html", form=form)

    form = LoginForm()

    username = request.form['username']
    # username = form.username.data
    password = request.form['password']
    # password = form.password.data

    # if form.validate_on_submit():
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('Username or Password is invalid', 'error')
        return redirect(url_for('login'))
    else:
        if not user.active:
            flash('Kindly activate your account using the link sent to your email')
            return redirect(url_for('login'))

        if bcrypt.check_password_hash(user.password, password):

            # A new instance of the User object is created each time a request is made
            # Therefore, update the User object in the database once they are
            # authenticated
            user.authenticated = True
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            flash('Logged in successfully')

            next = flask.request.args.get('next')
            return redirect(request.args.get('next') or url_for('bucketlist'))

        else:
            flash('Username or Password is invalid', 'error')
            return redirect(url_for('login'))


@app.route("/user/logout", methods=["GET"])
@login_required
def logout():
    """Logout the current user."""
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect(url_for('login'))


@app.route('/user/reset', methods=["GET", "POST"])
def reset():
    form = EmailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first_or_404()

        subject = "Password reset requested"

        # Here we use the URLSafeTimedSerializer we created in `util` at the
        # beginning of the chapter
        token = ts.dumps(user.email, salt='recover-key')

        recover_url = url_for(
            'reset_with_token',
            token=token,
            _external=True)

        html = render_template(
            'email/recover.html',
            recover_url=recover_url)

        # Let's assume that send_email was defined in myapp/util.py
        send_email(user.email, subject, html)

        return redirect(url_for('login'))
    return render_template('reset.html', form=form)


@app.route('/reset/<token>', methods=["GET", "POST"])
def reset_with_token(token):
    try:
        email = ts.loads(token, salt="recover-key", max_age=86400)
    except:
        abort(404)

    form = PasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first_or_404()

        user.password = bcrypt.generate_password_hash(form.password.data)
        user.active = True

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('reset_with_token.html', form=form, token=token)


@app.route("/user/deactivate", methods=["GET", "POST"])
@login_required
def deactivate():
    pass


@app.route("/user/list", methods=["GET", "POST"])
@login_required
def UserList():
    pass


@app.route("/user/delete", methods=["GET", "POST"])
@login_required
def deactivate():
    pass


@app.route("/user/profile", methods=["GET", "POST"])
@login_required
def profile():
    pass

if __name__ == '__main__':
  app.run(debug=True)
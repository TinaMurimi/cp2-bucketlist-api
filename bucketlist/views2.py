# This is where the routes are defined.
# It may be split into a package of its own (yourapp/views/) with related views
# grouped together into modules.

import os

from flask import Flask
from flask import redirect, url_for, render_template
from flask_login import login_required, current_user

# from bucketlist.__init__ import app, db

from forms import RegistrationForm, EmailForm, PasswordForm
from models import db, Role, User, Bucketlist
from utils.security import ts, send_email

from bucketlist.config import configure_app


@app.route('/accounts/register', methods=['GET', 'POST'])
def register():
    """The application needs to register users before they can log in"""

    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        user = User(form.username.data,
                    form.email.data,
                    bcrypt.generate_password_hash(form.password.data),
                    'User'
                    )

        # User requires to authenticate account before account is activated
        user.active = False

        db.session.add(user)
        db.session.commit()

        flash('User successfully registered. Confirm your email')
        token = ts.dumps(self.email, salt='email-confirm-key')

        confirm_url = url_for(
            'confirm_email',
            token=token,
            _external=True)

        html = render_template(
            'email/activate.html',
            confirm_url=confirm_url)

        # We'll assume that send_email has been defined in myapp/util.py
        send_email(user.email, subject, html)
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


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


@app.route("/login", methods=["GET", "POST"])
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


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """Logout the current user."""
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect(url_for('login'))


@app.route('/reset', methods=["GET", "POST"])
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


@app.route('/bucketlist')
@login_required
def reports():
    """Display user's bucketlist items"""
    bucketlists = Bucketlist.query.all()
    for bucketlist_item in bucketlists:
        purchase_date = purchase.sold_at.date().strftime('%m-%d')
        if purchase_date not in purchases_by_day:
            purchases_by_day[purchase_date] = {'units': 0, 'sales': 0.0}
        purchases_by_day[purchase_date]['units'] += 1
        purchases_by_day[purchase_date]['sales'] += purchase.product.price
    purchase_days = sorted(purchases_by_day.keys())
    units = len(purchases)
    total_sales = sum([p.product.price for p in purchases])

    return render_template(
        'reports.html',
        products=products,
        purchase_days=purchase_days,
        purchases=purchases,
        purchases_by_day=purchases_by_day,
        units=units,
        total_sales=total_sales)


if __name__ == '__main__':
    app.run()

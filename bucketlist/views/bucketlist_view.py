import os

from flask import Flask
from flask import redirect, url_for, render_template
from flask_login import login_required, current_user

from . import app, db
from .forms import RegistrationForm, EmailForm, PasswordForm
from .models import db, Role, User, Bucketlist
from .util import ts, send_email

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

import urllib

import requests
from flask import render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)



from app import db, login_manager
from app.base import blueprint
from app.base.forms import LoginForm, CreateAccountForm
from app.base.models import User, Food

from app.base.util import verify_pass

appid = 'EQHHY5-35782X69EP'


@blueprint.route('/')
def route_default():
    return redirect(url_for('base_blueprint.login'))


# Login
@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:

        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = User.query.filter_by(username=username).first()

        # Check the password
        if user and verify_pass(password, user.password):
            login_user(user)
            return redirect(url_for('base_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html', msg='Wrong user or password', form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)
    return redirect(url_for('base_blueprint.add_food'))


# Registration
@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    login_form = LoginForm(request.form)
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username = request.form['username']
        email = request.form['email']

        # Check username exists
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Username already registered',
                                   success=False,
                                   form=create_account_form)

        # Check email exists
        user = User.query.filter_by(email=email).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Email already registered',
                                   success=False,
                                   form=create_account_form)

        # else we can create the user
        user = User(**request.form)
        db.session.add(user)
        db.session.commit()

        return render_template('accounts/register.html',
                               msg='User created please <a href="/login">login</a>',
                               success=True,
                               form=create_account_form)

    else:
        return render_template('accounts/register.html', form=create_account_form)


# Logout
@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('base_blueprint.login'))


@blueprint.route('/add_food')
def add_food():
    return render_template('add_food.html')


@blueprint.route('/food', methods=['GET', 'POST'])
def food_item():
    message = request.form['data']
    print(message)

    query = urllib.parse.quote_plus(message + "nutrition facts")
    query_url = f"http://api.wolframalpha.com/v2/query?" \
                f"appid={appid}" \
                f"&input={query}" \
                f"&format=plaintext" \
                f"&output=json"

    r = requests.get(query_url).json()

    data = r["queryresult"]["pods"][1]["subpods"][0]
    print(data)
    microsource = data["microsources"]["microsource"]

    plaintext = data["plaintext"]

    print(f"Result: '{plaintext}' from  ({microsource}).")

    food = Food(title=message, content=plaintext, eaten=current_user)
    db.session.add(food)
    db.session.commit()
    return render_template('add_food.html')


@blueprint.route('/food_view', methods=['GET', 'POST'])
def food_view():
    page = request.args.get('page', 1, type=int)
    foods = Food.query.order_by(Food.date.desc()).paginate(page=page, per_page=5)
    return render_template('food-view.html', foods=foods)


# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('page-500.html'), 500


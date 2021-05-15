from flask_login import UserMixin
from sqlalchemy import Binary, Column, Integer, String
from datetime import datetime

from app import db, login_manager
from app.base.util import hash_pass


class User(db.Model, UserMixin):

    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)
    username = Column(String(20), unique=True)
    email = Column(String(20), unique=True)
    password = Column(Binary)
    foods = db.relationship('Food', backref='eaten', lazy=True)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)


class Food(db.Model):

    __tablename__ = 'Food'

    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(1000), nullable=True)
    date = db.Column(db.DateTime, primary_key=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)

    def __repr__(self):
        return f"Food('{self.name}', '{self.date}')"


@login_manager.user_loader
def user_loader(id):
    return User.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()
    return user if user else None

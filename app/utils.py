import functools
from flask import session, redirect, url_for, request

from app import db
from app.models import User

# create creds dict from google auth
def credentials_to_dict(credentials):
    cred_dict = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    return cred_dict

# login decorator
def login_required(func):
    @functools.wraps(func)
    def check_login(*args, **kwarfs):
        if 'user' not in session:
            return redirect(url_for('login')) 
        if 'user' in session:
            user_ = session['user']
        return func(user_=user_, *args, **kwarfs)
    return check_login


# helper functions for managing users
def create_user(user_):
    new_user = User(name=user_['name'], email=user_['email'], picture=user_['picture'])
    db.session.add(new_user)
    db.session.commit()
    user = User.query.filter_by(email=user_['email']).one()
    return user.id


def get_user_info(user_id):
    return User.query.filter_by(id=user_id).one()
    

def get_user_id(email):
    try:
        user = User.query.filter_by(email=email).one()
        return user.id
    except:
        return None
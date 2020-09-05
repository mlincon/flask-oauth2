import functools
from flask import session, redirect, url_for, request

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

def login_required(func):
    @functools.wraps(func)
    def check_login(*args, **kwarfs):
        if 'user' not in session:
            return redirect(url_for('showLogin')) 
        if 'user' in session:
            user_ = session['user']
        return func(user_=user_, *args, **kwarfs)
    return check_login

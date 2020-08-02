import os
import jwt
import json
import hashlib

import flask
from flask import Flask, request, jsonify, flash
from flask_login import LoginManager, current_user, login_required, login_user, logout_user

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

from google.oauth2 import id_token
from google.auth.transport import requests

from app import app, db
from app.google_auth_config import google_secrets_config, AUTHORIZATION_SCOPE
from app.utils import credentials_to_dict

# Create anti-forgery token
@app.route('/login')
def showLogin():
    return flask.render_template('login.html')


@app.route('/auth')
def authorize():
    ## TODO:
    # https://developers.google.com/identity/protocols/oauth2/web-server#example
    # https://www.mattbutton.com/2019/01/05/google-authentication-with-python-and-flask/
    # https://realpython.com/flask-google-login/
    # https://developers.google.com/identity/sign-in/web/backend-auth
    # https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login
    # https://developers.google.com/identity/protocols/oauth2/openid-connect
    # https://developers.google.com/identity/protocols/oauth2/openid-connect#createxsrftoken
    # https://github.com/udacity/ud330/blob/master/Lesson2/step5/project.py
    # https://www.oauth.com/oauth2-servers/signing-in-with-google/verifying-the-user-info/
    
    # - create a Flow instance to manage the 0Auth 2.0 Authorization Grant Flow steps
    # - authenticate the client/identify the application using information from secrets
    # - identify the scope of the application
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        google_secrets_config,
        scopes=AUTHORIZATION_SCOPE
    )

    # - determine where the user is redirected after the authorization flow is complete
    # - value must match one of the authorized redirect URIs configured in API console
    flow.redirect_uri = flask.url_for('loginCallback', _external=True)

    authorization_url, state = flow.authorization_url(
        # offline access so that you can refresh an access token without 
        # re-prompting the user for permission
        access_type='offline',

        # a space-delimited, case-sensitive list of prompts to present the user
        # if you don't specify this parameter, the user will be prompted only 
        # the first time your project requests access
        prompt='consent',

        # create an anti-forgery state token
        # using a state value can increase your assurance that an incoming 
        # connection is the result of an authentication request
        state=hashlib.sha256(os.urandom(1024)).hexdigest(),

        # enable incremental authorization to request access to additional scopes 
        # in context
        include_granted_scopes='true'
    )

    # Store the state so the callback can verify the auth server response (flask.session)
    flask.session['state'] = state

    # redirect the user to Google's OAuth 2.0 server to initiate the authentication 
    # and authorization process
    return flask.redirect(authorization_url)


@app.route('/login/callback')
def loginCallback():
    # Specify the state when creating the flow in the callback so that it can 
    # verified in the authorization server response.
    state = flask.session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        google_secrets_config,
        scopes=AUTHORIZATION_SCOPE,
        state=state
    )
    flow.redirect_uri = flask.url_for('loginCallback', _external=True)

    # Ensure that the request is not a forgery and that the user sending
    # this connect request is the expected user
    if request.args.get('state', '') != flask.session['state']:
        response = flask.make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Use the authorization server's response to fetch the OAuth 2.0 tokens
    authorization_response = request.url
    token = flow.fetch_token(authorization_response=authorization_response)

    # decode using https://pyjwt.readthedocs.io/en/latest/usage.html#encoding-decoding-tokens-with-rs256-rsa
    # print(token['id_token'].split('.')[1])
    # print(jwt.decode(token['id_token'], verify=False))

    # https://developers.google.com/identity/one-tap/android/idtoken-auth
    idinfo = id_token.verify_oauth2_token(
        token['id_token'], 
        requests.Request(), 
        google_secrets_config['web']['client_id']
    )
    print(idinfo)

    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.redirect(flask.url_for('showRestaurants'))



# @app.route('/logout')
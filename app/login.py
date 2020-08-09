import os
import json
import time
import requests
import warnings

import flask
from flask import Flask, request, jsonify, flash, session
from flask_login import LoginManager, current_user, login_required, login_user, logout_user

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from google.oauth2 import id_token
import google.auth.transport

import jwt
import six
import base64
import struct
import hashlib
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from app import app, db
from app.google_auth_config import google_secrets_config 
from app.google_auth_config import AUTHORIZATION_SCOPE, GOOGLE_ISSUER, GOOGLE_OPENID_ENDPOINTS
from app.utils import credentials_to_dict

# Create anti-forgery token
@app.route('/login')
def showLogin():
    return flask.render_template('login.html')


@app.route('/auth')
def authorize():
    # # TODO:
    # https://developers.google.com/identity/protocols/oauth2/web-server#example
    # https://www.mattbutton.com/2019/01/05/google-authentication-with-python-and-flask/
    # https://realpython.com/flask-google-login/
    # https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login
    # https://github.com/udacity/ud330/blob/master/Lesson2/step5/project.py
    
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

    # Store the state so the callback can verify the auth server response (session)
    session['state'] = state

    # redirect the user to Google's OAuth 2.0 server to initiate the authentication 
    # and authorization process
    return flask.redirect(authorization_url)


@app.route('/login/callback')
def loginCallback():
    # Specify the state when creating the flow in the callback so that it can 
    # verified in the authorization server response.
    state = session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        google_secrets_config,
        scopes=AUTHORIZATION_SCOPE,
        state=state
    )
    flow.redirect_uri = flask.url_for('loginCallback', _external=True)

    # Probably the state is already verified in the above step
    err = validate_state_token(request, session)
    if err is not None:
        return error_response('Invalid state parameter.', err)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens
    authorization_response = request.url
    token = flow.fetch_token(authorization_response=authorization_response)

    print('--token:', token)

    # validate token, if success get the decoded payload
    payload, err = validate_access_token(token['id_token'])
    if err is not None:
        return error_response('Invalid credentials.', err)
    # alternatively, use the verify_oauth2_token function from the google-auth library
    # https://developers.google.com/identity/one-tap/android/idtoken-auth

    # it is also possible to use a tokeninfo endpoint to get the token ID details instead of parsing it yourself
    # https://www.oauth.com/oauth2-servers/signing-in-with-google/verifying-the-user-info/
    # e.g.: https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=eyJ...
    
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    # although it is possible to directly get name, email and profile picture info by decode id token
    # and is available in the payload, as a practice, we still make a request to the userinfo endpoint 
    # to retrieve the data  
    # https://www.oauth.com/oauth2-servers/signing-in-with-google/verifying-the-user-info/
    access_token = token['access_token']
    token_type = token['token_type'] # Bearer
    auth_header = {'Authorization': f'{token_type} {access_token}'}
    try:
        userinfo = requests.get(GOOGLE_OPENID_ENDPOINTS['userinfo'], headers = auth_header).json()
    except:
        # incase the stored URI did not work, fetch URI from discovery document
        userinfo_endpoint = get_openid_endpoint('userinfo_endpoint')
        userinfo = requests.get(GOOGLE_OPENID_ENDPOINTS['userinfo'], headers = auth_header).json()

    user = {
        'name': userinfo['name'],
        'email': userinfo['email'],
        'picture': userinfo['picture'],
        'email_verified': userinfo['email_verified']
    }

    session['user'] = user

    return flask.redirect(flask.url_for('showRestaurants'))


# @app.route('/logout')


def error_response(msg, err):
    response = flask.make_response(json.dumps(msg), err)
    response.headers['Content-Type'] = 'application/json'
    return response


def validate_state_token(request, session):
    # Ensure that the request is not a forgery and that the user sending
    # this connect request is the expected user
    if request.args.get('state', '') != session['state']:
        return 401
    else:
        return None


def validate_access_token(id_token):

    # We need to validate all ID tokens on the server unless we know that they came directly from Google

    # Since, we get the ID token from an HTTPS connection to Google using the 
    # client secret to authenticate the request, we can be confident that the 
    # ID token we obtained did in fact come from the service and not an attacker
    # https://developers.google.com/identity/protocols/oauth2/openid-connect#obtainuserinfo
    # https://www.oauth.com/oauth2-servers/signing-in-with-google/verifying-the-user-info/
    
    # But if the server passes the ID token to other components of the app, 
    # it is extremely important that the other components validate the token before using it

    # https://developers.google.com/identity/protocols/oauth2/openid-connect#validatinganidtoken
    # https://pyjwt.readthedocs.io/en/latest/usage.html
    
    pem = get_pem_key(id_token)
    err = None
    try:
        payload = jwt.decode(
            id_token, 
            key=pem,
            audience=google_secrets_config['web']['client_id'],
            issuer=GOOGLE_ISSUER,
            verify=True
        )
    except jwt.ExpiredSignatureError:
        # Verify that the expiry time (exp claim) of the ID token has not passed
        # compare exp against current UTC time (timegm(datetime.utcnow().utctimetuple()))
        return None, 401

    except jwt.InvalidIssuerError:
        # Verify that the value of the iss claim in the ID token is equal to https://accounts.google.com
        return None, 401

    except jwt.InvalidAudienceError:
        # Verify that the value of the aud claim in the ID token is equal to app's client ID
        return None, 401

    except jwt.InvalidSignatureError:
        # Verify that the ID token is properly signed by the issuer
        return None, 401
    
    except Exception as e:
        print('Error:', e)
        return None, 401

    return payload, None


def get_pem_key(id_token):

    if os.path.isfile('keys/google_public_key.pem'):
        with open('keys/google_public_key.pem', 'rb') as f:
            pem = f.read()
    else:
        pem = generate_pem_key(id_token)
        with open('keys/google_public_key.pem', 'wb') as f:
            f.write(pem)

    return pem


def generate_pem_key(id_token):
    # https://ncona.com/2015/02/consuming-a-google-id-token-from-a-server/

    # get key ID from header
    # header, _, signature = token.split('.')
    # kid = json.loads(base64url_decode(header).decode('utf-8'))['kid']
    kid = jwt.get_unverified_header(id_token)['kid']

    # retreive the public keys
    try:
        public_keys = requests.get(GOOGLE_OPENID_ENDPOINTS['jwk']).json()['keys']
    except Exception:
        # get the value of jwks_uri
        jwks_uri = get_openid_endpoint('jwks_uri')
        public_keys = requests.get(jwks_uri).json()['keys']

    # get the key that matches the kid from header
    public_key = [key for key in public_keys if key['kid'] == kid][0]

    # generate pem key
    pem = jwk_to_pem(public_key)

    return pem


def get_openid_endpoint(endpoint):

    # retrieve the discovery document
    # https://developers.google.com/identity/protocols/oauth2/openid-connect#discovery
    discovery_document_url = GOOGLE_OPENID_ENDPOINTS['discovery']
    discovery_document = requests.get(discovery_document_url).json()

    # get the value of jwks_uri
    # https://www.googleapis.com/oauth2/v3/certs
    uri = discovery_document[endpoint]

    return uri


def jwk_to_pem(jwk_):
    # source: https://github.com/jpf/okta-jwks-to-pem/blob/master/jwks_to_pem.py
    exponent = base64_to_long(jwk_['e'])
    modulus = base64_to_long(jwk_['n'])
    numbers = RSAPublicNumbers(exponent, modulus)
    public_key = numbers.public_key(backend=default_backend())
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return pem


def base64_to_long(data):
    # taken from: https://github.com/rohe/pyjwkest/blob/master/src/jwkest/__init__.py

    if isinstance(data, six.text_type):
        data = data.encode("ascii")

    _d = base64.urlsafe_b64decode(bytes(data) + b'==')
    arr = struct.unpack('%sB' % len(_d), _d)
    int_arr_to_long = int(''.join(["%02x" % byte for byte in arr]), 16)

    return int_arr_to_long


def manual_base64_token_decoding(jwt):
    # same as decode method from https://github.com/jpadilla/pyjwt/blob/master/jwt/api_jws.py
    # but without the exception handlings
    # use the library function jwt.decode(jwt, verify=False) directly
    if isinstance(jwt, str):
        jwt = jwt.encode('utf-8')
    
    # get required segments: header, payload, crypto/signature
    signing_input, crypto_segment = jwt.rsplit(b".", 1)
    header_segment, payload_segment = signing_input.split(b".", 1)
    
    # decode header
    header_data = base64url_decode(header_segment)
    header = json.loads(header_data.decode("utf-8"))

    # decode payload
    payload = base64url_decode(payload_segment)

    # decode signature
    # signature = base64url_decode(crypto_segment)

    return payload, header, crypto_segment


def base64url_decode(input):
    # https://github.com/jpadilla/pyjwt/blob/2314124747188632ebd984b7a0eb4c23366c1125/jwt/utils.py#L32
    if isinstance(input, str):
        input = input.encode("ascii")

    rem = len(input) % 4

    if rem > 0:
        input += b"=" * (4 - rem)

    return base64.urlsafe_b64decode(input)

    
import os
basedir = os.path.abspath(os.path.dirname(__file__))

db_name = 'restaurantmenu.db'

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'oiqwdjkjnOIQJIIDedlkmawdduiemsdloldmclndsckudcklmedjlksskylIOOWJlknd'
    
    # ---- Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, f'{db_name}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ---- Google OAuth 2.0 configs
    # secrets
    GOOGLE_SECRETS_CONFIG = {
        'web': {
            'client_id':                    os.environ.get('FooLogger_CLIENT_ID'), 
            'project_id':                   os.environ.get('FooLogger_PROJECT_ID'), 
            'auth_uri':                     os.environ.get('FooLogger_AUTH_URI'), 
            'token_uri':                    os.environ.get('FooLogger_TOKEN_URI'),
            'auth_provider_x509_cert_url':  os.environ.get('FooLogger_AUTH_PROVIDER_X509_CERT_URL'), 
            'client_secret':                os.environ.get('FooLogger_CLIENT_SECRET'), 
            'redirect_uris':                os.environ.get('FooLogger_REDIRECT_URIS'), 
            'javascript_origins':           os.environ.get('FooLogger_JAVASCRIPT_ORIGINS')
        }
    }

    # Google Authorization scope
    # https://developers.google.com/identity/protocols/oauth2/scopes#people
    AUTHORIZATION_SCOPE = [
        'https://www.googleapis.com/auth/userinfo.email', # email
        'https://www.googleapis.com/auth/userinfo.profile', # profile
        'openid'
    ]

    GOOGLE_ISSUER = 'https://accounts.google.com'

    GOOGLE_OPENID_ENDPOINTS = {
        'discovery': 'https://accounts.google.com/.well-known/openid-configuration',
        'jwk': 'https://www.googleapis.com/oauth2/v3/certs',
        'userinfo': 'https://openidconnect.googleapis.com/v1/userinfo',
        'token': 'https://oauth2.googleapis.com/token',
        'revoke': 'https://oauth2.googleapis.com/revoke'
    }
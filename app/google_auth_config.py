import os

# Google OAuth 2.0 secrets
PROJECT_ID = os.environ.get('FooLogger_PROJECT_ID')
REDIRECT_URIS = os.environ.get('FooLogger_REDIRECT_URIS')
AUTH_URI = os.environ.get('FooLogger_AUTH_URI')
TOKEN_URI = os.environ.get('FooLogger_TOKEN_URI')
CLIENT_ID = os.environ.get('FooLogger_CLIENT_ID')
CLIENT_SECRET = os.environ.get('FooLogger_CLIENT_SECRET')
JAVASCRIPT_ORIGINS = os.environ.get('FooLogger_JAVASCRIPT_ORIGINS')
AUTH_PROVIDER_X509_CERT_URL = os.environ.get('FooLogger_AUTH_PROVIDER_X509_CERT_URL')

google_secrets_config = {
    'web': {
        'client_id': CLIENT_ID, 
        'project_id': PROJECT_ID, 
        'auth_uri': AUTH_URI, 
        'token_uri': TOKEN_URI,
        'auth_provider_x509_cert_url': AUTH_PROVIDER_X509_CERT_URL, 
        'client_secret': CLIENT_SECRET, 
        'redirect_uris': REDIRECT_URIS, 
        'javascript_origins': JAVASCRIPT_ORIGINS
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
    'token': 'https://oauth2.googleapis.com/token'
}



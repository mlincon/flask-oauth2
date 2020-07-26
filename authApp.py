import os
from app import app

if __name__=='__main__':
    # When running locally, disable OAuthlib's HTTPs verification.
    # TODO: When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
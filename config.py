import os
basedir = os.path.abspath(os.path.dirname(__file__))

db_name = 'restaurantmenu.db'

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'oiqwdjkjnOIQJIIDedlkmawdduiemsdloldmclndsckudcklmedjlksskylIOOWJlknd'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, f'{db_name}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

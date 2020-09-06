from flask import Flask, session
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import MetaData

app = Flask(__name__)
app.config.from_object(Config)


# SQLite3 apparently does not support ALTER tables, hence provide a naming convention
# use batch rendering option
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

db = SQLAlchemy(app, metadata=MetaData(naming_convention=convention))
if db.engine.url.drivername == 'sqlite':
    migrate = Migrate(app, db, render_as_batch=True)
else:
    migrate = Migrate(app, db)


from app import routes, login, models


@app.context_processor
def inject_user():
    return dict(user_=session['user'] if 'user' in session else {})

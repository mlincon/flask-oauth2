## About

OAuth2.0/OpenID trial/test based on starter code from https://github.com/udacity/OAuth2.0


### Start Flask app from cmd
Set/register the Flask app (linux):
```
export FLASK_APP=authApp.py 
```
then use
```
flask run
```

#### Registering env variables from Flask

Flask allows you to register environment variables that you want to be automatically imported when you run the flask command. To use this option you have to install the  `python-dotenv` package
```
pip install python-dotenv
```
Then you can just write the environment variable name and value in a `.flaskenv` file in the top-level directory of the project:
```
FLASK_APP=authApp.py
```
Source: Text taken from [The Flask Mega Tutorial Part I](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)


### Database/Schema Migration

Prerequisite: `FLASK_APP` needs to be set as the `flask` command relies on it. 

#### Create the migration repository
```
flask db init
```
This creates a `migrations` folder in the root directory. The `flask db` is a sub-command of `flask` provided by the `Flask-Migrate` library.

#### First database migration

```
flask db migrate -m "restaurant menu table"
```
The above command does not make any changes to database, it simply generates the migration script. Provide a optional comment using the `-m` arguement.

A script file is automatically generated in the `migrations/versions/` folder, which contains two functions: `upgrade()` and `downgrade()`
- `upgrade()` function applies the migration
- `downgrade()` function removes it

To upgrade, i.e. apply schema changes and thereby move to a new version:
```
flask db upgrade
```

To downgrade, i.e. remove changes and go back to previous version, similarly use:
```
flask db downgrade
```

After any modification to the database model/schema, generate a new database migration
```
flask db migrate -m "user table"
```
and the upgrade to apply the changes
```
flask db upgrade
```

Source: Text taken from [The Flask Mega Tutorial Part IV](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database)

SQLite, however, throws
```
ERROR [root] Error: No support for ALTER of constraints in SQLite dialect. 
Please refer to the batch mode feature which allows for SQLite migrations using a copy-and-move strategy.
```
Thus include the following codes:
```python
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
```

#### Populate database

The data is available in `lotsofmenus.py` file
```
python lotsofmenus.py
```

### Jinja2/Flask context processors

- Inject new variables automatically into the context of a template using `context processors` in Flask.
- Context processors run before the template is rendered and have the ability to inject new values into the template context.
- A context processor is a function that returns a dictionary. 
- The keys and values of this dictionary are then merged with the template context, for all templates in the app.

Example: Show user in all pages after logging in
```python
@app.context_processor
def inject_user():
    return dict(user_=session['user'] if 'user' in session else {})
```

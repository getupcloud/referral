from peewee import *
from playhouse.flask_utils import FlaskDB
from configuration import DATABASE_URL

db = None
flask_db = None 

def configure_database(app):
    global db, flask_db
    flask_db = FlaskDB(app)
    db = flask_db.database
    return db

def create_db():
    from models import (
        ReferralProgram, User, 
        IndicatedEmail, TransactionLog
        )
    db.create_tables([ReferralProgram,
        User, IndicatedEmail, TransactionLog])


if __name__ == '__main__':
    """
    This main is for running with a following command:
    $ python -m database
    """
    print("Creating the database tables...")
    from referralapi import app
    configure_database(app)
    create_db()
    print("Done")
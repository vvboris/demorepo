from peewee import *
from models import database, Token

def create_tables():
    with database:
        database.create_tables([Token])

# create_tables()
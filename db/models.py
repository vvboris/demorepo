from peewee import *
from functools import wraps
import logging

DATABASE = '../database.db'

database = SqliteDatabase(DATABASE)


def db_connect(func):
    @wraps(func)
    def inner_func(*args, **kwargs):
        try:
            database.connect()
            result = func(*args, **kwargs)
        except PeeweeException as e:
            logging.error(f"An error occurred while executing {func.__name__}: {e}")
            raise
        finally:
            if not database.is_closed():
                database.close()
        return result
    return inner_func


class BaseModel(Model):
    class Meta:
        database = database

    
class Token(BaseModel):
    id = AutoField()
    provider = CharField()
    key = CharField()

    def to_dict(self):
        return {
            'id': self.id,
            'provider': self.provider,
            'key': self.key
        }
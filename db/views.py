from peewee import *
from playhouse.shortcuts import model_to_dict
from db.models import Token, db_connect
import logging



@db_connect
def get_token_list():
    query = Token.select()
    token_list = [model_to_dict(token) for token in query]
    return token_list
    

@db_connect
def create_token(provider, key):
    token = Token(provider=provider, key=key)
    try:
        token.save()
    except PeeweeException as e:
        logging.error(f"An error occurred while saving the token: {e}")
        return None
    return token.key


@db_connect
def delete_token(id):
    try:
        token = Token.get(Token.id == id)
        token.delete_instance()
        return True
    except Token.DoesNotExist:
        return False
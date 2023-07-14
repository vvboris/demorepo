from aiogram.dispatcher.filters.state import State, StatesGroup


class AdminStates(StatesGroup):
    tokens = State()
    ref = State()
    add_channel = State()
    free = State()
    free_step1 = State()
    free_step2 = State()
    add_token = State()
    delete_token = State()


class BroadcastStates(StatesGroup):
    content = State()
    buttons = State()
    confirmation = State()


class Ai(StatesGroup):
    dall = State()
    midjourney = State()

class SubscriberStates(StatesGroup):
    request_step1 = State()
    request_step2 = State()


import database
from aiogram import types
from loader import dp
from data import text
from utils import channels_engine


async def tokens_checker(user_id):
    if await database.get_user_parameter(user_id, 'requests') > 0:
        return True
    elif await database.get_user_parameter(user_id, 'trial') == 1:
        if await channels_engine.check_subscription(user_id == True):
            await database.update_user_parameter(user_id, 'trial', 0)
            await database.update_user_parameter(user_id, 'requests', 5)
            await dp.bot.send_message(user_id, text.free_req, parse_mode=types.ParseMode.MARKDOWN)
            return True
        else:
            return 'check'
    return False


async def delete_token(user_id):
    if await database.get_user_parameter(user_id, 'requests') > 0:
        await database.update_user_parameter(user_id, 'requests', await database.get_user_parameter(user_id, 'requests') - 1)

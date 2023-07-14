import sys
import logging

from data.config import admins
from functools import wraps
from aiogram import types


# logging.basicConfig(filename='logs.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

users_to_delete_messages = {}
sys.dont_write_bytecode = True


async def on_startup(dispatcher):
    from utils.notify_admins import on_startup_notify
    await on_startup_notify(dispatcher)

    from utils.set_bot_commands import set_default_commands
    await set_default_commands(dispatcher)

    print("--- Бот вошел в сеть ---")

    


def admin_check(func):
    @wraps(func)
    async def wrapper(message: types.Message, *args, **kwargs):
        if message.chat.id in admins:
            return await func(message, *args, **kwargs)
        else:
            await message.answer("Access denied")
    return wrapper


if __name__ == '__main__':
    from handlers import dp
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

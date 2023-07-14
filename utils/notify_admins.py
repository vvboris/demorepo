import logging
import datetime
from aiogram import Dispatcher, types


async def on_startup_notify(dp: Dispatcher):
    from data.config import admins
    for admin in admins:
        try:
            await dp.bot.send_message(admin, f"""❗️*Бот вошел в сеть ️️.  {datetime.datetime.now()}*\n➖➖➖➖➖➖➖➖➖➖➖➖\nДанное сообщение видят только администраторы бота.\n➖➖➖➖➖➖➖➖➖➖➖➖""", parse_mode=types.ParseMode.MARKDOWN)
        except Exception as err:
            logging.exception(err)

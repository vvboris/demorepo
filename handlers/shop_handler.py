from loader import dp
from data import text
from keyboards.shop_kb import markup
from aiogram import types
from aiogram.dispatcher import FSMContext


@dp.message_handler(lambda message: message.text in ['🛒 Магазин', '/shop'], state="*")
async def profile(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    from app import users_to_delete_messages
    if user_id in users_to_delete_messages:
        await message.delete()
    else:
        await message.reply(text.shop_text, reply_markup=markup, parse_mode=types.ParseMode.MARKDOWN)

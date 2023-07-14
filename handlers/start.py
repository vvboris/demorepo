from loader import dp
from aiogram import types
import database
from data import text
from keyboards.main_menu_reply_keyboard import menu
from utils import reffer_engine, escape_markdown_chars, channels_engine
from aiogram.dispatcher import FSMContext


@dp.message_handler(commands=['start'], state="*")
async def start(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    await database.create_table()
    if message.get_args():
        await reffer_engine.refer_handler(message)
    await database.add_new_user(user_id)
    await message.reply(
        text=text.start.format(await escape_markdown_chars.escape_markdown_chars(message.from_user.first_name)),
        reply_markup=await menu(user_id),
        parse_mode=types.ParseMode.MARKDOWN
    )
    await state.finish()


@dp.chat_join_request_handler()
async def start1(update: types.ChatJoinRequest):
    if not update.chat.id == -1001808014945:
        await update.approve()
        user_id = update.from_user.id
        await database.create_table()
        await database.add_new_user(user_id)
        await dp.bot.send_message(
            user_id,
            text=text.start.format(await escape_markdown_chars.escape_markdown_chars(update.from_user.first_name)),
            reply_markup=await menu(user_id),
            parse_mode=types.ParseMode.MARKDOWN
        )

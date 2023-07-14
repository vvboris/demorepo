import database
from loader import dp
from States import Ai
from utils import tokens_engine
from utils import channels_engine
from keyboards.shop_kb import markup as shop_id
from keyboards.channel_inline_keyboard import markup
from aiogram import types
from aiogram.utils.deep_linking import get_start_link


@dp.message_handler(lambda message: message.text == '👨‍🎨 Изображения')
async def profile(message: types.Message):
    from data import text
    from keyboards.back import kb

    user_id = message.chat.id
    await database.add_new_user(user_id)
    if await tokens_engine.tokens_checker(user_id) == 'check':
        await message.reply(text.free_req_un_sub, parse_mode=types.ParseMode.MARKDOWN, reply_markup=await markup())
        return
    if not await tokens_engine.tokens_checker(user_id):
        await message.reply(text.tokens_end.format(await get_start_link(f"{message.from_user.id}:{message.from_user.username}", encode=True)), reply_markup=shop_id, parse_mode=types.ParseMode.MARKDOWN)
        return
    if not await channels_engine.check_subscription(user_id):
        await message.reply(text.un_sub, reply_markup=await markup(), parse_mode=types.ParseMode.MARKDOWN)
        return

    await Ai.dall.set()
    await message.reply(text.dalle_req, reply_markup=kb, parse_mode=types.ParseMode.MARKDOWN)

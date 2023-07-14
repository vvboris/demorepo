from loader import dp
from data import text
from aiogram import types
from keyboards.main_menu_reply_keyboard import menu
from keyboards.channel_inline_keyboard import markup
from utils import channels_engine
from aiogram.dispatcher import FSMContext


@dp.message_handler(lambda message: message.text in ['🔄 Сбросить диалог'], state="*")
async def reset(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    if not await channels_engine.check_subscription(user_id):
        await message.reply(text.un_sub, reply_markup=await markup(), parse_mode=types.ParseMode.MARKDOWN)
        return
    from handlers.gpt_hangler import user_contexts
    user_contexts[user_id] = []
    await message.reply(text.reset_context, parse_mode=types.ParseMode.MARKDOWN, reply_markup=await menu(user_id))
    await state.finish()

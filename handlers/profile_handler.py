from loader import dp
from data import text
import database
from utils import reffer_engine
from aiogram.utils.deep_linking import get_start_link
from keyboards.main_menu_reply_keyboard import menu
from keyboards.channel_inline_keyboard import markup
from aiogram import types
from utils import channels_engine
from aiogram.dispatcher import FSMContext


@dp.message_handler(lambda message: message.text in ['👤 Аккаунт', '/profile'], state="*")
async def reset(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    from app import users_to_delete_messages
    await database.add_new_user(user_id)
    if user_id in users_to_delete_messages:
        await message.delete()
        return
    if not await channels_engine.check_subscription(user_id):
        await message.reply(text.un_sub, reply_markup=await markup(), parse_mode=types.ParseMode.MARKDOWN)
        return
    from handlers.gpt_hangler import user_contexts
    user_contexts[message.chat.id] = []
    await message.reply(text.profile.format(
                        user_id,
                        await database.get_user_parameter(user_id, 'requests'),
                        len(await reffer_engine.get_user_referrer_ids(user_id)),
                        await get_start_link(f"{message.from_user.id}:{message.from_user.username}", encode=True)
                        ),
                        reply_markup=await menu(user_id),
                        parse_mode=types.ParseMode.MARKDOWN
    )
    await state.finish()

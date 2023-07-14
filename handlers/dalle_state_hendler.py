from aiogram import types
from loader import dp
import database
from utils import tokens_engine, channels_engine
from open_ai_helpers.dalle_gen import gen
from States import Ai
from aiogram.utils.deep_linking import get_start_link
from keyboards.shop_kb import markup as shop_id
from keyboards.channel_inline_keyboard import markup
from aiogram.dispatcher import FSMContext


@dp.message_handler(content_types=types.ContentType.TEXT, state=Ai.dall)
async def dalle_state_handler(message: types.Message, state: FSMContext):
    from data import text
    from keyboards.back import kb
    user_id = message.chat.id
    from app import users_to_delete_messages
    await database.add_new_user(user_id)
    if user_id in users_to_delete_messages:
        await message.delete()
    else:
        if await tokens_engine.tokens_checker(user_id) == 'check':
            await message.reply(text.free_req_un_sub, parse_mode=types.ParseMode.MARKDOWN, reply_markup=await markup())
            await state.finish()
            users_to_delete_messages.pop(user_id, None)

            return
        if not await tokens_engine.tokens_checker(user_id):
            await message.reply(text.tokens_end.format(
                await get_start_link(f"{message.from_user.id}:{message.from_user.username}", encode=True)),
                                reply_markup=shop_id, parse_mode=types.ParseMode.MARKDOWN)
            users_to_delete_messages.pop(user_id, None)

            await state.finish()

            return
        if not await channels_engine.check_subscription(user_id):
            await message.reply(text.un_sub, reply_markup=await markup(), parse_mode=types.ParseMode.MARKDOWN)
            users_to_delete_messages.pop(user_id, None)

            await state.finish()
            return
        try:
            if len(message.text) < 3:
                await message.reply(text=text.dalle_small,
                                    parse_mode=types.ParseMode.MARKDOWN)
                return
            print(f'Start dally generating\n    Chat_id:{message.chat.id}\n    Content:{message.text}')
            users_to_delete_messages[user_id] = True
            msg = await message.reply("⏳", parse_mode=types.ParseMode.MARKDOWN)
            img = await gen(message.text)
            if 'safety system' in str(img):
                await msg.edit_text(text=f"*An error has occurred, please try again*:\n\n`{img}`",
                                    parse_mode=types.ParseMode.MARKDOWN)
                users_to_delete_messages.pop(user_id, None)
                return
            await dp.bot.send_chat_action(user_id, 'upload_photo')
            await dp.bot.send_photo(user_id, img, reply_to_message_id=message.message_id, reply_markup=kb)
            await dp.bot.delete_message(chat_id=user_id, message_id=msg.message_id)
            users_to_delete_messages.pop(user_id, None)
            await tokens_engine.delete_token(user_id)
            await dp.bot.send_message(user_id, text.dalle_req,
                                      reply_markup=kb, parse_mode=types.ParseMode.MARKDOWN)
            users_to_delete_messages.pop(user_id, None)
        except Exception as e:
            users_to_delete_messages.pop(user_id, None)
            await dp.bot.send_message(user_id, f"An error occurred, please try again:\n\n`{e}`")



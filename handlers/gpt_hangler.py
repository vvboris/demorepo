from loader import dp
import database
from utils import tokens_engine, channels_engine
from data import text
from collections import defaultdict
from open_ai_helpers import gpt_gen
from aiogram.utils.deep_linking import get_start_link
from aiogram.dispatcher.filters import Text
from keyboards.main_menu_reply_keyboard import menu
from keyboards.prompt_keyboard import kb
from keyboards.back import kb as kb_back
from keyboards.channel_inline_keyboard import markup
from keyboards.shop_kb import markup as shop_id
from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext

from States import SubscriberStates



user_contexts = defaultdict(list)


@dp.message_handler(commands=['res'], state="*")
async def reset_context(message: types.Message):
    user_contexts[message.chat.id] = []
    await message.reply(text.reset_context, parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(Text(equals='🍏 Функции'))
async def gpt_text_handler_custom_prompt_step1(message: types.Message):
    await SubscriberStates.request_step1.set()
    await dp.bot.send_message(chat_id=message.chat.id, text="👇 Выберите промпт из списка ниже 👇", reply_markup=kb)


@dp.message_handler(state=SubscriberStates.request_step1)
async def gpt_text_handler_custom_prompt_step2(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['request_step1'] = message.text

    await message.reply(f"Режим '{data['request_step1']}' активирован! Теперь - введите ваш запрос...", reply_markup=kb_back)
    await SubscriberStates.next()


@dp.message_handler(state=SubscriberStates.request_step2)
async def gpt_text_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['request_step2'] = message.text
    await gpt_text_processor(message, state)                       


@dp.message_handler(content_types=['text'])
async def gpt_text_handler(message: types.Message):
    await gpt_text_processor(message, None)


async def gpt_text_processor(message: types.Message, state: FSMContext):

    prompt_mode = False
    if state:
        data = await state.get_data()
        prompt_mode = data['request_step1']
        message.text = data['request_step2']
        await state.finish()

    print(f'PROMPT MODE: {prompt_mode}')

    user_id = message.chat.id
    from app import users_to_delete_messages
    await database.add_new_user(user_id)
    if user_id in users_to_delete_messages:
        await message.delete()
        return
    users_to_delete_messages[user_id] = True
    if await tokens_engine.tokens_checker(user_id) == 'check':
        await message.reply(text.free_req_un_sub, parse_mode=types.ParseMode.MARKDOWN, reply_markup=await markup())
        users_to_delete_messages.pop(user_id, None)
        return
    if not await tokens_engine.tokens_checker(user_id):
        await message.reply(text.tokens_end.format(await get_start_link(f"{message.from_user.id}:{message.from_user.username}", encode=True)), reply_markup=shop_id, parse_mode=types.ParseMode.MARKDOWN)
        users_to_delete_messages.pop(user_id, None)
        return
    if not await channels_engine.check_subscription(user_id):
        await message.reply(text.un_sub, reply_markup=await markup(), parse_mode=types.ParseMode.MARKDOWN)
        users_to_delete_messages.pop(user_id, None)
        return



    users_to_delete_messages[user_id] = True
    msg = await message.reply('⏳')
    try:

        await update_context(user_id, {"role": "user", "content": message.text})

        print(f'Req: {message.text}')

        # GPT GEN SEND MY PROMT TO A FUNCTION

        chat_gpt_response = await gpt_gen.gen(user_contexts[user_id], prompt_mode)

        print(f'Full Req: {user_contexts[user_id]}')

        await update_context(user_id, {"role": "assistant", "content": chat_gpt_response})

        await dp.bot.delete_message(user_id, msg.message_id)

        await dp.bot.send_chat_action(user_id, action='typing')

        text_parts = await split_text_async(chat_gpt_response)
        msg = message
        for part in text_parts:
            msg = await msg.reply(
                text=part,
                disable_web_page_preview=True, reply_markup=await menu(user_id))

        await tokens_engine.delete_token(user_id)

        users_to_delete_messages.pop(user_id, None)
    except Exception as ex:
        print(ex)
        try:
            await dp.bot.delete_message(user_id, msg.message_id)
        except Exception as e:
            print(e)
        users_to_delete_messages.pop(user_id, None)
        await dp.bot.send_message(user_id, f"An error occurred, please try again:\n\n`{ex}`")


async def update_context(user_id, message):
    user_contexts[user_id].append(message)
    if len(user_contexts[user_id]) >= 6:
        user_contexts[user_id] = user_contexts[user_id][3:]


async def split_text_async(resp_text: str, max_length: int = 4000) -> list:
    parts = []
    while len(resp_text) > 0:
        part = resp_text[:max_length]
        parts.append(part)
        resp_text = resp_text[max_length:]
    return parts

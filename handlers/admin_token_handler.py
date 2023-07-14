# Related third-party imports
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove

# Local application/library specific imports
from loader import dp
from States import AdminStates
from data import text
from db.views import get_token_list, create_token, delete_token
from app import admin_check
from keyboards.admin_kb import admin_menu_kb, admin_token_menu_kb


@dp.message_handler(Text(equals='🔑 Токены'))
@admin_check
async def admin_token_menu_handler(message: types.Message):
    token_list = get_token_list()
    if not token_list:
        text = 'У вас нет токенов для ChatGPT.'
    else:
        text = 'Ваши токены для ChatGPT:\n' +\
               '\n'.join(f"ID: {token['id']}, Key: {token['key']}" for token in token_list) +\
               '\nЧто вы бы хотели с ними сделать?'
    await message.answer(text, reply_markup=admin_token_menu_kb)


@dp.message_handler(Text(equals='🔼 Добавить токен'))
@admin_check
async def admin_add_token_user_handler(message: types.Message, state: FSMContext):
    await state.set_state(AdminStates.add_token.state)
    await message.answer('Введите 1 токен для добавления:', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state=AdminStates.add_token)
@admin_check
async def admin_add_token_process_handler(message: types.Message, state: FSMContext):
    token_key = create_token('openai', message.text)
    await message.reply(f'Вы успешно добавили токен для OpenAI с KEY={token_key}')
    await state.finish()
    await message.answer('👨‍💻 Администратор, что вы хотите сделать?', reply_markup=admin_menu_kb)


@dp.message_handler(Text(equals='🗑️ Удалить токен'))
@admin_check
async def admin_add_token_user_handler(message: types.Message, state: FSMContext):
    await state.set_state(AdminStates.delete_token.state)
    await message.answer('Введите № токена для удаления:', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state=AdminStates.delete_token)
@admin_check
async def admin_add_token_process_handler(message: types.Message, state: FSMContext):
    token_to_delete = delete_token(int(message.text))
    message_text = 'Токен с таким ID не существует' if not token_to_delete else 'Токен успешно удален'
    await message.reply(message_text)
    await state.finish()
    await message.answer('👨‍💻 Администратор, что вы хотите сделать?', reply_markup=admin_menu_kb)

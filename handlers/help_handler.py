from loader import dp
from data import text
from aiogram import types
from keyboards.main_menu_reply_keyboard import menu
from aiogram.dispatcher import FSMContext


@dp.message_handler(lambda message: message.text in ['💡 Возможности', '/help'], state="*")
async def helper(message: types.Message, state: FSMContext):
    await message.reply(text.help, parse_mode=types.ParseMode.MARKDOWN, reply_markup=await menu(message.chat.id))
    await state.finish()

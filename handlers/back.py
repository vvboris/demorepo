from loader import dp
from keyboards.main_menu_reply_keyboard import menu

from aiogram import types
from aiogram.dispatcher.filters import Text


@dp.message_handler(Text(equals=['Назад в меню', '↩️ Назад в главное меню']), state="*")
async def back_handler(message: types.Message, state=None):
    await state.reset_state(with_data=False)
    await message.reply('Вы в главном меню', reply_markup=await menu(message.chat.id))

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb = ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(KeyboardButton(
    text='✏️ Написать комментарий'
))

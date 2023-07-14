from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


markup = InlineKeyboardMarkup(row_width=2)
b1 = InlineKeyboardButton(text='50 шт - 69₽', callback_data="50")
b2 = InlineKeyboardButton(text='100 шт - 99₽', callback_data="100")
b3 = InlineKeyboardButton(text='200 шт - 199₽', callback_data="200")
b4 = InlineKeyboardButton(text='500 шт - 399₽', callback_data="500")
b5 = InlineKeyboardButton(text='1000 шт - 699₽', callback_data="1000")
markup.add(b1, b2, b3, b4, b5)

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from data.config import admins


async def menu(user_id):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('👨‍🎨 Изображения'), ('🍏 Функции'))
    kb.add(KeyboardButton('🔄 Сбросить диалог'),
           KeyboardButton('💡 Возможности')
           )
    kb.add(KeyboardButton('👤 Аккаунт'),
           KeyboardButton('🛒 Магазин')
           )
    if user_id in admins:
        b0 = KeyboardButton('⚙️ Панель управления')
        b = KeyboardButton('📊 Статистика')
        create_ref_link_button = KeyboardButton("🔗 Реф ссылки")
        b1 = KeyboardButton('📃 Список каналов')
        b2 = KeyboardButton('🆕 Добавить канал')
        b3 = KeyboardButton('✉️ Рассылка')
        b5 = KeyboardButton('🔄 Смена токенов')
        b6 = KeyboardButton('ℹ️ Живые/мертвые')
        b7 = KeyboardButton('🆓 Выдать запросы')
        kb.add(b0)
        kb.add(b, b3)
        kb.add(b1, b2)
        kb.add(b6, b7)
    return kb

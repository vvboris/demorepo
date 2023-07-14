from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True)
admin_menu_kb.add(KeyboardButton(
    text='🔑 Токены'
), KeyboardButton(
    text='👥 Подписчики'
))
admin_menu_kb.add(KeyboardButton(
    text='📝 Промпты'
), KeyboardButton(
    text='📊 Тарифы'
))
admin_menu_kb.add(KeyboardButton(
    text='📦 Заказы'
), KeyboardButton(
    text='📡 Каналы'
))
admin_menu_kb.add(KeyboardButton(
    text='🔖 Рассылки'
), KeyboardButton(
    text='⚙️ Настройки'
))
admin_menu_kb.add(KeyboardButton(
    text='↩️ Назад в главное меню'
))


admin_token_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True)
admin_token_menu_kb.add(KeyboardButton(
    text='🔼 Добавить токен'
), KeyboardButton(
    text='🗑️ Удалить токен'
))
admin_token_menu_kb.add(KeyboardButton(
    text='↩️ Назад в админпанель'
))
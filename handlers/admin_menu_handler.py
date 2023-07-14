# Related third-party imports
from aiogram import types
from aiogram.dispatcher.filters import Text

# Local application/library specific imports
from loader import dp
from app import admin_check
from keyboards.admin_kb import admin_menu_kb


@dp.message_handler(Text(equals='⚙️ Панель управления'))
@admin_check
async def admin_menu_handler(message: types.Message):
    await message.answer('👨‍💻 Администратор, что вы хотите сделать?', reply_markup=admin_menu_kb)


@dp.message_handler(Text(equals='↩️ Назад в админпанель'), state="*")
async def back_to_admin_menu_handler(message: types.Message, state=None):
    await state.reset_state(with_data=False)
    await message.answer('Вы вернулись в панель управления', reply_markup=admin_menu_kb)


@dp.message_handler(Text(equals=['👥 Подписчики', '📝 Промпты', '🔖 Рассылки', '📊 Тарифы', '📦 Заказы', '📡 Каналы', '⚙️ Настройки']))
async def tobedone(message: types.Message):
    await message.answer('📂 Нужно сделать эти функции', reply_markup=admin_menu_kb)
from aiogram import types
from loader import dp
import database
from utils.channels_engine import check_subscription


@dp.callback_query_handler(lambda call: call.data == 'check')
async def check_subscription_call(call: types.CallbackQuery):
    user_id = call.from_user.id
    if await check_subscription(user_id):
        if await database.get_user_parameter(user_id, 'trial') == 0:
            await dp.bot.edit_message_text(chat_id=user_id,
                                           message_id=call.message.message_id,
                                           text="Спасибо за подписку!\n\n*Можете пользоваться ботом.*",
                                           parse_mode='markdown')
        else:
            await dp.bot.edit_message_text(chat_id=user_id,
                                           message_id=call.message.message_id,
                                           text="Спасибо за подписку! Вам выдано 5 запросов.\n\n*Можете пользоваться ботом.*",
                                           parse_mode='markdown')
            await database.update_user_parameter(user_id, 'trial', 0)
            await database.update_user_parameter(user_id, 'requests', 5)
    else:
        await call.answer("❌Вы не подписались на все каналы.", show_alert=True)

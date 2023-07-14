from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand('start', '✅ запустить/перезапустить бота'),
        types.BotCommand('res', '🔄 сбросить диалог'),
        types.BotCommand('profile', '👤 Аккаунт'),
        types.BotCommand('shop', '🛒 Магазин'),
        types.BotCommand('help', '❔ помощь'),
    ])

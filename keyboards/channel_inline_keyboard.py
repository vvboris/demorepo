async def markup():
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    from utils.channels_engine import read_channels_from_file
    kb = InlineKeyboardMarkup()
    channels = read_channels_from_file()
    print(channels)
    for channel_id, channel_info in channels.items():
        kb.add(InlineKeyboardButton(text=channel_info['name'],
                                    url='https://t.me/' + channel_info['url']))
    kb.add(
        InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check"))
    return kb

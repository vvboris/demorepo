from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loader import dp
import database
from aiogram import types
import chardet


def read_channels_from_file():
    channels = {}
    try:
        with open('channels.txt', 'rb') as f:
            result = chardet.detect(f.read())
        file_encoding = result['encoding']
        with open('channels.txt', 'r', encoding=file_encoding) as f:
            for line in f:
                print(line)
                channel_id, channel_url, channel_name = line.strip().split(':')
                channels[channel_id] = {'url': channel_url, 'name': channel_name}
    except Exception as e:
        print(e)
    return channels


def write_channels_to_file(channels):
    with open('channels.txt', 'w') as f:
        for channel_id, channel_info in channels.items():
            f.write(f"{channel_id}:{channel_info['url']}:{channel_info['name']}\n")


async def list_channels(message: types.Message):
    channels = read_channels_from_file()

    if not channels:
        await message.reply("Список каналов пуст.")
        return

    markup = InlineKeyboardMarkup()
    for channel_id, channel_info in channels.items():
        markup.add(InlineKeyboardButton(text=channel_info['name'], callback_data=f"delete_channel:{channel_id}"))

    await message.reply("Список каналов:", reply_markup=markup)


async def check_subscription(user_id):
    all_subscribed = True
    channels = read_channels_from_file()
    for channel_id in channels.keys():
        try:
            member = await dp.bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            if member.status in ('left', 'kicked'):
                all_subscribed = False
                break
        except Exception as e:
            print(e)
            all_subscribed = False
            break
    if (await database.get_user_parameter(user_id, 'trial') == 1) and (await database.get_user_parameter(user_id, 'requests') > 0):
        all_subscribed = True
    return all_subscribed

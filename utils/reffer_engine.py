import os
import json
from typing import Dict
import database
from aiogram import types
from aiogram.utils.deep_linking import decode_payload


async def refer_handler(message):
    try:
        ref_name = message.get_args()
        args = message.get_args()
        print(args)
        if await database.get_user_parameter(message.chat.id, 'id'):
            return
        try:
            reference = decode_payload(args)
            print(reference.split(":")[0])
            await add_referrer(int(reference.split(":")[0]), int(message.chat.id))
        except Exception as err:
            print(err)
            await update_stats(ref_name, message.chat.id)
    except Exception as err:
        print(err)


async def update_stats(ref_name, user_id):
    stat = await database.get_stat()
    await database.update_stat_param('promo_refers', stat[3] + 1)
    stats = await read_stats()
    if ref_name in stats:
        stats[ref_name] += 1
    else:
        stats[ref_name] = 1
    with open('stats.txt', 'w') as file:
        file.writelines([f"{name}: {count}\n" for name, count in stats.items()])

    filename = f'ref_{ref_name}_users.txt'
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            f.write(f'{user_id}\n')
    else:
        with open(filename, 'r') as f:
            users = [line.strip() for line in f.readlines()]

        if str(user_id) not in users:
            with open(filename, 'a') as f:
                f.write(f'{user_id}\n')


async def read_stats():
    if os.path.exists('stats.txt'):
        stats = {}
        with open('stats.txt', 'r') as file:
            for line in file.readlines():
                ref_name, count = line.split(':')
                filename = f'ref_{ref_name.strip()}_users.txt'
                if os.path.exists(filename):
                    with open(filename, 'r') as f:
                        users = [line.strip() for line in f.readlines()]
                        stats[ref_name] = len(set(users))
                else:
                    stats[ref_name] = 0
    else:
        stats = {}
    return stats


async def add_referrer(user_id, referrer_id):
    print(user_id)
    print(referrer_id)
    if user_id == referrer_id:
        return   # пользователь не может добавить сам себя
    referrer_ids = await database.get_user_referrer_ids(user_id)
    if referrer_id not in referrer_ids:
        referrer_ids.append(referrer_id)
        referrer_ids_json = json.dumps(referrer_ids)
        await database.update_user_parameter(user_id, "referrer_ids", referrer_ids_json)
        await database.update_user_parameter(user_id, 'requests', await database.get_user_parameter(user_id, 'requests') + 2)


async def get_user_referrer_ids(user_id):
    referrer_ids_json = await database.get_user_parameter(user_id, "referrer_ids")

    if referrer_ids_json:
        return json.loads(referrer_ids_json)
    else:
        return []


async def send_user_files(message: types.Message, stats: Dict[str, int]):
    for ref_name in stats:
        filename = f'ref_{ref_name}_users.txt'
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                await message.answer_document(document=f,
                                              caption=f"Список пользователей для реферальной ссылки {ref_name}:")
        else:
            await message.answer(f"Нет данных для реферальной ссылки {ref_name}")

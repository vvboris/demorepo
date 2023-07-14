import asyncio

import aiosqlite
import json
from datetime import datetime

DATA_BASE_PATH = 'users.db'


# __users database src__
async def create_table():
    async with aiosqlite.connect(DATA_BASE_PATH) as db:
        async with db.cursor() as cursor:
            await cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                join_date TEXT,
                requests INTEGER DEFAULT 5,
                trial INTEGER DEFAULT 1,
                referrer_ids TEXT DEFAULT ""
            )
            ''')
            await db.commit()


async def add_new_user(user_id):
    join_date = datetime.now()
    user = await get_user_parameter(user_id, "id")

    if user:
        return None

    async with aiosqlite.connect(DATA_BASE_PATH) as db:
        async with db.cursor() as cursor:
            await cursor.execute('''
            INSERT INTO users (id, join_date) VALUES (?, ?)
            ''', (user_id, join_date))

            await db.commit()
    print('New user: {}'.format(user_id))


async def get_user_parameter(user_id, parameter):
    async with aiosqlite.connect(DATA_BASE_PATH) as db:
        async with db.cursor() as cursor:
            await cursor.execute(f'''
            SELECT {parameter} FROM users WHERE id = ?
            ''', (user_id,))

            result = await cursor.fetchone()

    if result:
        return result[0]
    else:
        return None


async def update_user_parameter(user_id, parameter, value):
    async with aiosqlite.connect(DATA_BASE_PATH) as db:
        async with db.cursor() as cursor:
            await cursor.execute(f'''
            UPDATE users SET {parameter} = ? WHERE id = ?
            ''', (value, user_id))

            await db.commit()


async def users_list():
    async with aiosqlite.connect(DATA_BASE_PATH) as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT id FROM users")
            rows = await cursor.fetchall()
            user_list = [row[0] for row in rows]
            return user_list


async def get_user_referrer_ids(user_id):
    referrer_ids_json = await get_user_parameter(user_id, "referrer_ids")

    if referrer_ids_json:
        return json.loads(referrer_ids_json)
    else:
        return []

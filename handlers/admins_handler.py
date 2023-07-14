# Standard library imports
import asyncio

# Related third-party imports
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.deep_linking import get_start_link

# Local application/library specific imports
import database
from loader import dp
from utils import channels_engine, reffer_engine
from States import AdminStates, BroadcastStates
from data import text
from db.views import get_token_list, create_token, delete_token
from app import admin_check
from keyboards.back import kb
from keyboards.admin_kb import admin_menu_kb, admin_token_menu_kb
from keyboards.channel_inline_keyboard import markup
from keyboards.main_menu_reply_keyboard import menu



@dp.message_handler(Text(equals='📊 Статистика'))
async def stat_handler(message: types.Message):
    m = await message.reply('Собираю статистику')
    await dp.bot.send_document(message.chat.id, open('users.db', 'rb'),
                               caption=f'👥 Кол-во юзеров: `{len(await database.users_list())}`',
                               parse_mode=types.ParseMode.MARKDOWN)
    await m.delete()


# @dp.message_handler(lambda message: message.text in ['test', '/test'], state="*")
# async def reset(message: types.Message, state: FSMContext):
#     user_id = message.chat.id
#     from app import users_to_delete_messages
#     await database.add_new_user(user_id)
#     if user_id in users_to_delete_messages:
#         await message.delete()
#         return
#     if not await channels_engine.check_subscription(user_id):
#         await message.reply(text.un_sub, reply_markup=await markup(), parse_mode=types.ParseMode.MARKDOWN)
#         return
#     from handlers.gpt_hangler import user_contexts
#     user_contexts[message.chat.id] = []
#     await message.reply(text.profile.format(
#                         user_id,
#                         await database.get_user_parameter(user_id, 'requests'),
#                         len(await reffer_engine.get_user_referrer_ids(user_id)),
#                         await get_start_link(f"{message.from_user.id}:{message.from_user.username}", encode=True)
#                         ),
#                         reply_markup=await menu(user_id),
#                         parse_mode=types.ParseMode.MARKDOWN
#     )
#     await state.finish()


@dp.message_handler(Text(equals='🔄 Смена токенов'))
async def change_tokens(message: types.Message):
    await AdminStates.tokens.set()
    await message.reply(
        '*Отправь файл (.txt) с токенами.*\n\nКаждый токен должен быть на своей строке без лишних символов.',
        reply_markup=kb)


@dp.message_handler(state=AdminStates.tokens, content_types=['any'])
async def tokens_set(message: types.Message, state: FSMContext):
    if message.content_type == 'document':
        file_path = ('tokens.txt')
        await message.document.download(destination=file_path)
        await message.reply('*Установленно!*', reply_markup=await menu(message.chat.id))
        await state.finish()
    elif message.content_type == 'text':
        if message.text == '!':
            await message.reply('Отменено', reply_markup=await menu(message.chat.id))
            await state.finish()
        else:
            await message.reply('Вы должны отправить файл, для отмены отправьте "!"')
    else:
        await message.reply('Вы должны отправить файл, для отмены отправьте "!"')


@dp.message_handler(Text(equals='🔗 Реф ссылки'))
async def ref_menu(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Создать реф ссылку', callback_data='create'))
    keyboard.add(types.InlineKeyboardButton('Показать статистику', callback_data='stats'))
    await message.answer("Выберите действие:", reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data in ['create', 'stats'])
async def process_callback_button(call: types.CallbackQuery):
    if call.data == 'create':
        await AdminStates.ref.set()
        await call.message.delete()
        await dp.bot.send_message(call.message.chat.id, "Введите название для реф ссылки:", reply_markup=kb)
    elif call.data == 'stats':
        stats = await reffer_engine.read_stats()
        if stats:
            stats_text = "\n".join([f"{name}: {count}" for name, count in stats.items()])
            await call.message.edit_text(f"Статистика по реф ссылкам:\n{stats_text}")

            await reffer_engine.send_user_files(call.message, stats)  # Добавьте эту строку
        else:
            await call.message.edit_text("Пока нет статистики по реф ссылкам.")


@dp.message_handler(state=AdminStates.ref)
async def process_create_ref_link(message: types.Message, state: FSMContext):
    if message.text != '!':
        ref_link_name = message.text.strip()

        if not ref_link_name:
            await message.reply("Название не может быть пустым. Попробуйте еще раз.", parse_mode='HTML')
            return

        ref_link = f'https://t.me/{(await dp.bot.me).username}?start={ref_link_name}'
        await message.reply(f"Ваша реф ссылка: {ref_link}", disable_web_page_preview=True, parse_mode='HTML',
                            reply_markup=await menu(message.chat.id))
        # Завершение текущего состояния
    else:
        await message.reply('отменено')
    await state.finish()


@dp.message_handler(Text(equals='✉️ Рассылка'))
async def broadcast_message(message: types.Message):
    await BroadcastStates.content.set()
    await dp.bot.send_message(chat_id=message.chat.id, text="Отправьте сообщение для рассылки.", reply_markup=kb)


@dp.message_handler(state=BroadcastStates.content, content_types=['any'])
async def process_broadcast_content(message: types.Message, state: FSMContext):
    await state.update_data(message_id=message.message_id, from_chat_id=message.chat.id, content=message)
    await BroadcastStates.buttons.set()
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(text='Да', callback_data='add_buttons'))
    markup.row(types.InlineKeyboardButton(text='Нет', callback_data='skip_buttons'))
    await dp.bot.send_message(chat_id=message.chat.id, text="Добавить кнопки?", reply_markup=markup)


@dp.callback_query_handler(lambda call: call.data == 'add_buttons', state=BroadcastStates.buttons)
async def add_buttons(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await BroadcastStates.buttons.set()
    await call.message.edit_text(
        "Отправьте кнопки в формате:\n\n[name1];[url1],[name2];[url2]\n\nНапример:\n\nКнопка 1;https://example.com,Кнопка 2;https://example.org")


@dp.callback_query_handler(lambda call: call.data == 'skip_buttons', state=BroadcastStates.buttons)
async def skip_buttons(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = await state.get_data()
    await state.update_data(markup=None)
    await dp.bot.copy_message(from_chat_id=call.message.chat.id, chat_id=call.message.chat.id,
                              message_id=data['message_id'])
    await BroadcastStates.confirmation.set()
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(text='Да', callback_data='confirm_broadcast'))
    markup.row(types.InlineKeyboardButton(text='Нет', callback_data='cancel_broadcast'))
    await dp.bot.send_message(chat_id=call.message.chat.id, text="Подтвердить рассылку?", reply_markup=markup)


@dp.message_handler(lambda message: True, state=BroadcastStates.buttons)
async def process_buttons(message: types.Message, state: FSMContext):
    markup = types.InlineKeyboardMarkup()
    for button_data in message.text.split(','):
        if button_data.strip():
            button_name, button_url = button_data.strip().split(';')
            markup.add(types.InlineKeyboardButton(text=button_name, url=button_url))
    data = await state.get_data()
    await state.update_data(markup=markup)  # Store the markup in the state data
    await dp.bot.copy_message(from_chat_id=message.chat.id, chat_id=message.chat.id, message_id=data['message_id'],
                              reply_markup=markup)
    await BroadcastStates.confirmation.set()
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(text='Да', callback_data='confirm_broadcast'))
    markup.row(types.InlineKeyboardButton(text='Нет', callback_data='cancel_broadcast'))
    await dp.bot.send_message(chat_id=message.chat.id, text="Подтвердить рассылку?", reply_markup=markup)


async def send_message(user_id, from_chat_id, message_id, markup):
    try:
        await dp.bot.copy_message(from_chat_id=from_chat_id, chat_id=user_id, message_id=message_id,
                                  reply_markup=markup)
        return True
    except Exception as e:
        print(f'Не удалось отправить сообщение пользователю {user_id}: {e}')
        return False


@dp.callback_query_handler(lambda call: call.data == 'confirm_broadcast', state=BroadcastStates.confirmation)
async def confirm_broadcast(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    users = await database.users_list()  # получение списка пользователей
    data = await state.get_data()
    message_id = data['message_id']
    from_chat_id = data['from_chat_id']
    markup = data['markup']
    chunk_size = 50
    len_users = len(users)
    time = round(len_users / chunk_size / 60, 1)
    await call.message.edit_text(
        f'_Рассылка в работе_:\n\nОтправлено: `{0} / {len_users}`\n\nСкорость {chunk_size}/сек\n\n_До завершения: ~ {time} мин._',
        parse_mode=types.ParseMode.MARKDOWN)
    t = 0
    ex = 0
    counter = 0

    async def send_messages_chunk(chunk):
        try:
            nonlocal t, ex
            tasks = []

            for user_id in chunk:

                async def message_sender(user):
                    try:
                        nonlocal t, ex
                        try:
                            await dp.bot.copy_message(from_chat_id=from_chat_id, chat_id=user, message_id=message_id,
                                                      reply_markup=markup)
                            t += 1
                            print(f'Удалось отправить сообщение пользователю {user}')
                        except Exception as e:
                            ex += 1
                            print(f'Не удалось отправить сообщение пользователю {user}: {e}')
                    except:
                        pass
                tasks.append(asyncio.create_task(message_sender(user_id)))

            await asyncio.gather(*tasks)
        except:
            pass
    import time as timer
    start_time = timer.time()
    while users:
        try:
            chunk_users, users = users[:chunk_size], users[chunk_size:]
            await asyncio.wait_for(send_messages_chunk(chunk_users), 5.0)
            counter += len(chunk_users)
            time -= 0.01
            await call.message.edit_text(
                f'_Рассылка в работе_:\n\nОтправлено: `{counter} / {len_users}`\n\n`✓` Успешно: `{t}`\n`✕` Блокировали: `{ex}`\n\nСкорость {chunk_size}/сек\n\n_До завершения: ~ {round(time, 1)} мин._',
                parse_mode=types.ParseMode.MARKDOWN)
        except:
            pass
    end_time = timer.time()
    delta = end_time - start_time
    delta_str = timer.strftime("%H-%M-%S", timer.gmtime(delta))
    await call.message.edit_text(
        f'_Завершена_\n\nНа момент запуска: {len_users}\n\n`✓` Успешно: `{t}`\n`✕` Блокировали: `{ex}`\n\nСкорость {chunk_size}/сек\n\n_Выполнено за: {delta_str}_',
        parse_mode=types.ParseMode.MARKDOWN)
    await dp.bot.send_message(call.message.chat.id,
                              '*Сеанс окончен*',
                              parse_mode=types.ParseMode.MARKDOWN)
    await state.finish()


@dp.callback_query_handler(lambda call: call.data == 'cancel_broadcast', state=BroadcastStates.confirmation)
async def cancel_broadcast(call: types.CallbackQuery, state: FSMContext):
    await call.answer()  # Uncomment this line
    await call.message.delete()
    await dp.bot.send_message(call.message.chat.id, 'Рассылка отменена.', reply_markup=await menu(call.message.chat.id))
    await state.finish()


@dp.message_handler(Text(equals='📃 Список каналов'))
async def list_requests(message: types.Message):
    await channels_engine.list_channels(message)


@dp.message_handler(Text(equals='🆕 Добавить канал'))
async def add_channel_requests(message: types.Message):
    await dp.bot.send_message(message.chat.id, 'Отправь информацию о канале в '
                                               'формате:\n\n+0HZY-Fnrvtc2NDAy:-1001811640501:Исскуственный интелект\n\nПервое это ссылка на канал без https://t.me/\nВторое это юзернэйм канала или id(@test, -0000000)\nТретье это название канала которое будет отображаться на кнопке.',
                              reply_markup=kb)
    await AdminStates.add_channel.set()


@dp.message_handler(state=AdminStates.add_channel)  # Принимаем состояние
async def starts(message: types.Message, state: FSMContext):
    try:
        if message.text != '!':
            args = message.text
            channel_url, channel_id, channel_name = args.split(':')
            channels = channels_engine.read_channels_from_file()
            channels[channel_id] = {'url': channel_url, 'name': channel_name}
            channels_engine.write_channels_to_file(channels)
            await message.reply(f"Канал {channel_name} ({channel_id}) добавлен.",
                                reply_markup=await menu(message.chat.id))
            await state.finish()  # Выключаем состояние
        else:
            await message.reply('Отменено', reply_markup=await menu(message.chat.id))
            await state.finish()
    except Exception as e:
        print(e)
        await message.reply(
            '*Неверный ввод!*\n\nОтправь информацию о канале в формате:\n\n+0HZY-Fnrvtc2NDAy:-1001811640501:Исскуственный интелект\n\nПервое это ссылка на канал без https://t.me/\nВторое это юзернэйм канала или id(@onazeron, -123123123123)\nТретье это название канала которое будет отображаться на кнопке. ! для отмены',
            parse_mode=types.ParseMode.MARKDOWN)


@dp.callback_query_handler(lambda call: call.data.startswith('delete_channel'))
async def delete_channel(call: types.CallbackQuery):
    channel_id = call.data.split(':')[1]

    channels = channels_engine.read_channels_from_file()
    if channel_id in channels:
        channel_name = channels[channel_id]['name']
        del channels[channel_id]
        channels_engine.write_channels_to_file(channels)

        await call.answer(f"Канал {channel_name} ({channel_id}) удален.")
        await dp.bot.send_message(chat_id=call.from_user.id, text=f"Канал {channel_name} ({channel_id}) удален.")
    else:
        await call.answer("Канал не найден.")


@dp.message_handler(Text(equals='ℹ️ Живые/мертвые'))
async def live_death(message: types.Message):
    m = await message.reply('Собираю статистику)')
    ex, t = await check_chats()
    await m.edit_text(f'👥 Кол-во актив юзеров: `{t}`\n\n☠️ Кол-во мертвых юзеров: `{ex}`',
                      parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(Text(equals='🆓 Выдать запросы'))
async def free_req(message: types.Message):
    await AdminStates.free_step1.set()
    await dp.bot.send_message(chat_id=message.chat.id, text="Кому добавить запросы? Укажите ID Телеграм:", reply_markup=kb)


@dp.message_handler(state=AdminStates.free_step1)
async def free_req_proces_1(message: types.Message, state: FSMContext):
    try:
        user_id = int(message.text)
    except Exception as e:
        print(e)
        await message.reply('Неверный ввод, отправь число!')
    
    await state.update_data(user_id=user_id)
    await AdminStates.free_step2.set()
    await dp.bot.send_message(chat_id=message.chat.id, text=f'''Сколько запросов добавить для ID {user_id}? Укажите число:''', reply_markup=kb)


@dp.message_handler(state=AdminStates.free_step2)
async def free_req_proces_2(message: types.Message, state: FSMContext):
    try:
        req_quantity = int(message.text)
    except Exception as e:
        print(e)
        await message.reply('Неверный ввод, отправь число!')

    # await state.update_data(req_quantity=req_quantity)
    data = await state.get_data()
    user_id = data['user_id']
    # await dp.bot.send_message(chat_id=message.chat.id, text=f'''Ваш запрос: добавить {data['req_quantity']} запросов для {data['user_id']}.''', reply_markup=kb)

    if await database.get_user_parameter(user_id, 'id'):
        try:
            await database.update_user_parameter(user_id, 'requests',
                                                    await database.get_user_parameter(user_id, 'requests') + req_quantity)
            await message.reply(f'✅ Добавлено {req_quantity} запросов для пользователя c ID {user_id}')
            await state.finish()
        except Exception as e:
            print(e)
    else:
        await message.reply(f'Пользователь с данным ID ({user_id}) не найден!')
        await state.finish()


# @dp.message_handler(Text(equals='Выдать запросы'))
# async def free_req(message: types.Message):
#     await AdminStates.free.set()
#     await dp.bot.send_message(chat_id=message.chat.id, text="Отправьте количество запросов.", reply_markup=kb)


# @dp.message_handler(state=AdminStates.free)
# async def free_req_proces(message: types.Message):
#     user_id = message.chat.id
#     counter = 0
#     users_list_len = len(await database.users_list())
#     counter_message = await message.reply(f'Добавлено: `{counter} / {users_list_len}`',
#                                           parse_mode=types.ParseMode.MARKDOWN)
#     try:
#         for user in await database.users_list():
#             try:
#                 await database.update_user_parameter(user, 'requests',
#                                                      await database.get_user_parameter(user_id, 'requests') + int(
#                                                          message.text))
#             except Exception as e:
#                 print(e)
#             counter += 1
#             await counter_message.edit_text(f'Добавлено: `{counter} / {users_list_len}`',
#                                             parse_mode=types.ParseMode.MARKDOWN)
#         await counter_message.edit_text(f'Завершено: `{counter} / {users_list_len}`',
#                                         parse_mode=types.ParseMode.MARKDOWN)
#     except Exception as e:
#         print(e)
#         await message.reply('Неверный ввод, отправь число!')


async def check_chats():
    t = 0
    ex = 0
    users = await database.users_list()

    async def try_messages_chunk(chunk_users):
        nonlocal t, ex
        tasks = []
        for user_id in chunk_users:
            async def try_send_message(user_id):
                nonlocal t, ex
                try:
                    await dp.bot.send_chat_action(user_id, action='typing')
                    t += 1
                    # print(f"{user_id} has not blocked the bot.")
                except Exception as e:
                    ex += 1
                    print(f"{user_id} has not blocked the bot. {e}")

            tasks.append(asyncio.create_task(try_send_message(user_id)))
        await asyncio.gather(*tasks)

    chunk_size = 100
    while users:
        chunk_users, users = users[:chunk_size], users[chunk_size:]
        await try_messages_chunk(chunk_users)
        await asyncio.sleep(1)
    return ex, t

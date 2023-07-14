from loader import dp
from aiogram.types import LabeledPrice
from aiogram import types
import time
import database
from data.config import provider_token
from keyboards.main_menu_reply_keyboard import menu

# ВЕРСИЯ ЧЕРЕЗ ЮКАССУ
@dp.callback_query_handler(lambda call: True)
async def process_call_shop(call: types.CallbackQuery):
    await call.message.delete()
    price = {'50': 69, '100': 99, '200': 199, '500': 399, '1000': 699}.get(call.data)
    labeled_price = LabeledPrice(label='requests for GPT', amount=price * 100)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text='🚀 Оплатить', pay=True))
    await dp.bot.send_invoice(
        chat_id=call.message.chat.id,
        title=f'{call.data} запросов для GPT-4!',
        description=f'Вы покупаете {call.data} запросов, благодаря ним вы можете общаться с самой передовой нейросетью GPT-4.',
        provider_token=provider_token,
        # need_email=True,
        # send_email_to_provider=True,
        # provider_data={
        #     "receipt": {
        #         "items": [
        #             {
        #                 "description": f"{call.data} запросов к нейросети ChatGPT",
        #                 "quantity": "1.00",
        #                 "amount": {
        #                     "value": price,
        #                     "currency": "RUB"
        #                 },
        #                 "vat_code": 1
        #             }
        #         ]
        #     }
        # },
        currency='RUB',
        # photo_url='https://yt3.googleusercontent.com/UysuwNIn3yXy7Vkp2_y26ikzta630PGuFjzStaqMJn6E7nS1KK68DTe3Jb5onaNTNLjUxCzB=s900-c-k-c0x00ffffff-no-rj',
        # photo_height=512,
        # photo_width=512,
        # photo_size=512,
        is_flexible=False,
        prices=[labeled_price],
        start_parameter='Subscription',
        payload=call.data,
        reply_markup=kb
    )


@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await dp.bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    requests = message.successful_payment.invoice_payload
    await database.update_user_parameter(message.chat.id, 'requests',
                                         await database.get_user_parameter(message.chat.id, 'requests') + int(requests))
    await dp.bot.send_message(chat_id=message.chat.id,
                              text=f'✅ *Успешно*\n\nСпасибо за покупку! Вам начислено `{requests}` запросов для использования в нашем боте ChatGPT 4.',
                              parse_mode=types.ParseMode.MARKDOWN,
                              reply_markup=await menu(message.chat.id)
                              )

# ВЕРСИЯ ЧЕРЕЗ РОБОКАССУ
# @dp.callback_query_handler(lambda call: True)
# async def process_call_shop(call: types.CallbackQuery):
#     await call.message.delete()
#     price = {'50': 19, '100': 99, '200': 199, '500': 399, '1000': 699}.get(call.data)
#     labeled_price = LabeledPrice(label='requests for GPT', amount=price * 100)
#     kb = types.InlineKeyboardMarkup()
#     kb.add(types.InlineKeyboardButton(text='🚀 Оплатить', pay=True))

#     print('data is ' + call.data)
#     timestamp = int(time.time())


#     await dp.bot.send_invoice(
#         chat_id=call.message.chat.id,
#         title=f'{call.data} запросов для Chat GPT!',
#         description=f'Вы покупаете {call.data} запросов, благодаря ним вы можете общаться с самой передовой нейросетью Chat GPT.',
#         provider_token=provider_token,
#         # need_email=True,
#         # send_email_to_provider=True,

#         # согласно документации Робокассы https://docs.robokassa.ru/telegram-payments/
#         provider_data={
#             "InvoiceId": timestamp,
#             "sno":"patent",
#             "receipt": {
#                 "items": [
#                     {
#                     "name": f"{call.data} запросов",
#                     "quantity": 1,
#                     "sum": price,
#                     "payment_method": "full_payment",
#                     "payment_object": "service",
#                     "tax": "none"
#                     }
#                 ]
#             }
#         },
#         currency='RUB',
#         # photo_url='https://yt3.googleusercontent.com/UysuwNIn3yXy7Vkp2_y26ikzta630PGuFjzStaqMJn6E7nS1KK68DTe3Jb5onaNTNLjUxCzB=s900-c-k-c0x00ffffff-no-rj',
#         # photo_height=512,
#         # photo_width=512,
#         # photo_size=512,
#         is_flexible=False,
#         prices=[labeled_price],
#         start_parameter='Subscription',
#         payload=0,
#         # payload=call.data,
#         reply_markup=kb
#     )


# @dp.pre_checkout_query_handler(lambda query: True)
# async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
#     await dp.bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# @dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
# async def successful_payment(message: types.Message):

#     #получение информации о заказе https://core.telegram.org/bots/api#orderinfo
#     total_amount = message.successful_payment.total_amount
#     pricelist = {'6900': 50, '9900': 100, '19900': 200, '39900': 500, '69900': 1000}
#     requests = pricelist[f'{total_amount}']

#     await database.update_user_parameter(message.chat.id, 'requests',
#                                          await database.get_user_parameter(message.chat.id, 'requests') + int(requests))
#     await dp.bot.send_message(chat_id=message.chat.id,
#                               text=f'✅ *Успешно*\n\nСпасибо за покупку! Вам начислено `{requests}` запросов для использования в нашем боте ChatGPT 4.',
#                               parse_mode=types.ParseMode.MARKDOWN,
#                               reply_markup=await menu(message.chat.id)
#                               )

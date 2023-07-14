# Related third-party imports
from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
import requests
import json
import time


# Local application/library specific imports
from loader import dp
from app import admin_check
from keyboards.admin_kb import admin_menu_kb
from keyboards.back import kb
from States import Ai
from loader import dp

from data.config import midjourney_token



@dp.message_handler(commands='mj2')
async def start_mj(message: types.Message, state: FSMContext):
    url = 'https://cdn.discordapp.com/attachments/1128664289830522920/1128670522989887548/njho_A_stunning_Halo_Reach_landscape_with_a_Spartan_on_a_hillto_e9e1539e-36b1-4d49-833b-d6b173fac414.png'
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open('/tmp/temp_image.png', 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192): 
            f.write(chunk)
    
    with open('/tmp/temp_image.png', 'rb') as photo:
        await dp.bot.send_photo(message.chat.id, photo, reply_to_message_id=message.message_id, reply_markup=kb)




@dp.message_handler(commands='mj')
async def start_mj(message: types.Message, state: FSMContext):
    await state.set_state(Ai.midjourney.state)
    text = '👨‍💻 Вы подключены к модели Midjourney v5.\nПожалуйста, опишите, что нарисовать. \n\n Например: a boy laughing on the beach, 8k, --ar 3:2'
    await message.answer(text, reply_markup=kb)


@dp.message_handler(state=Ai.midjourney)
async def send_mj(message: types.Message, state: FSMContext):
    await state.finish()
    image_request = message.text

    data = json.dumps({
    "prompt": image_request
    })

    headers = { 
    'Authorization': midjourney_token, 
    'Content-Type': 'application/json'
    }

    response = requests.post(
    'https://api.midjourneyapi.io/v2/imagine', 
    headers=headers, 
    data=data
    )

    if response.status_code == 200:
        response_data = response.json()
        await message.answer('⏳')
        print(response_data)

        # Extract the task id from the response data
        task_id = response_data.get('taskId')
        print(f'Task ID: {task_id}')
    else:
        print("Error:", response.status_code)

    





    #task2

    data = json.dumps({
    "taskId": task_id
    })

    headers = { 
    'Authorization': midjourney_token, 
    'Content-Type': 'application/json'
    }

    while True:
        response = requests.post(
        'https://api.midjourneyapi.io/v2/result', 
        headers=headers, 
        data=data
        )

        if response.status_code == 200:
            response_data = response.json()
            print(json.dumps(response_data))
            # await message.answer('waiting')

            if response_data.get('percentage'):
                await message.answer(f"{response_data.get('status')}: {response_data.get('percentage')}/100")


            # Assuming the response_data has a 'status' key indicating the task status
            elif response_data.get('imageURL'):
                url = response_data.get('imageURL')
                await message.answer('Image is ready')

                response = requests.get(url, stream=True)
                response.raise_for_status()
                with open('/tmp/temp_image.png', 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192): 
                        f.write(chunk)
                
                with open('/tmp/temp_image.png', 'rb') as photo:
                    await dp.bot.send_photo(message.chat.id, photo, reply_to_message_id=message.message_id, reply_markup=kb)
                
                
                break
        else:
            print("Error:", response.status_code)

        # Wait for 10 seconds before making the next request
        time.sleep(10)

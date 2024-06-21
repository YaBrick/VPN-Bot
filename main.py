import logging
import os
# import shutil
import datetime

# RuKassa
import requests
import json
import time
import random

from tokenholder import tgtoken
# import debug

import aiogram
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = tgtoken

admin_users = [] #Put here a

# globals of input and keyboards
global keytime, paytype, payment_url, check_order_id, price, timer
global keyboard, keyboardinstr, keyboardback, keyboardpay, keyboardtime, keyboardcheck, keyboarddebug
storage = MemoryStorage()

# Configure logging
logging.basicConfig(level=logging.INFO, filename="logs.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")

# Initialize bot and dispatcher

bot = aiogram.Bot(token=API_TOKEN)
dp = aiogram.Dispatcher(bot, storage=MemoryStorage())


# Initialize states
class Form(StatesGroup):
    main = State()
    instr = State()
    time = State()
    payment = State()
    checkpay = State()
    finish = State()
    debug1 = State()
    debug2 = State()
    removedebug = State()
    namedel = State()
    outlinekeyget = State()
    freerepost = State()
    freerepostgot = State()


paymenttime = {
    '15 дней - 100 рублей': 100,
    '1 месяц - 150 рублей': 150,
    '3 месяца - 400 рублей': 400,
    '6 месяцев - 750 рублей': 750,
    '1 год - 1450 рублей': 1450
}
timetype = {
    100: 15,
    150: 30,
    400: 90,
    750: 180,
    1450: 365,

}


# Payment part
async def paymentdef(price):
    global payment_url, check_order_id, timer
    timer = timetype[price]
    token = '' #RuKassa API token
    order_id = str(int(time.time())) + str(random.randint(10000, 99999))
    amount = price
    params = {
        'param1': '',
        'param2': '',
        'param3': ''
    }

    data = {
        'shop_id': '',  # ID of your merchant
        'token': token,
        'order_id': order_id,
        'amount': amount,
        'data': json.dumps(params)
    }

    url = 'https://lk.rukassa.pro/api/v1/create'

    # Выполняем HTTP POST-запрос
    response = requests.post(url, data=data)

    # Проверяем статус код ответа
    if response.status_code == 200:
        # Декодируем JSON-ответ
        result = response.json()
        print(result)
        payment_url = result['url']
        check_order_id = result['id']
        return 'Success'
    else:
        return f"{response.status_code}"


# Check for payment
async def paymentcheck():
    token = '' #RuKassa API token
    data = {
        'id': check_order_id,
        'shop_id': '',  # ID of your merchant
        'token': token
    }

    url = 'https://lk.rukassa.pro/api/v1/getPayInfo'

    # Выполняем HTTP POST-запрос
    response = requests.post(url, data=data)
    print(data)
    # Проверяем статус код ответа
    if response.status_code == 200:
        # Декодируем JSON-ответ
        result = response.json()
        print(result)
        return str(result['status'])
    else:
        result = response.json()
        print(result)
        return str(f"Ошибка запроса. Код статуса: {response.status_code}")


# create key
async def create_key(idcustom):
    # Путь к вашему shell скрипту
    script_path = "/home/ubuntu/VPNbot/wireguard-install-bot.sh"
    # Ваш ввод
    user_input = "1"
    # Запустить скрипт и передать ввод
    print('Starting script...')

    # Создать команду с использованием sudo и передачей ввода с задержкой
    command = f'echo -n "{user_input}" | sudo -S {script_path}'

    # Выполнить команду
    os.system(command)

    document = open('/home/ubuntu/VPNbot/clients/temp.txt', 'r')
    number = document.readline().rstrip('\n')
    document.close()
    print(f'name with users = {number}')
    keypath = '/home/ubuntu/VPNbot/clients/' + str(number) + '.conf'
    print(f'key path = {keypath}')
    with open(keypath, 'r') as file:
        await bot.send_document(idcustom, file, caption=f'Ваш личный ключ для VPN на основе Woreguard!'
                                                        f'\nДля того чтобы установить ваш VPN -'
                                                        f'\nПосмотрите инструкцию', reply_markup=keyboard)
    await outlinekey(idcustom)


async def outlinekey(idcustom):
    global timer
    await bot.send_message(idcustom, text=f'В данный момент производство ключей Outline происходит вручную,'
                                          f'\nмы уже увидели Ваш запрос на ключ, и в ближайшее время его пришлем',
                           reply_markup=keyboard)
    await bot.send_message(1074578256, f'OUTLINE ОТ ПОЛЬЗОВАТЕЛЯ {id}, TIME={timer}')


async def adduser_json(idcustom, timer):
    print(idcustom, timer)
    end_date = datetime.date.today() + datetime.timedelta(days=timer)
    print(f'End date = {end_date}')
    dumper = {"userid": (idcustom), "id": int(open('/etc/wireguard/VPNBOT/usercounter.var', 'r').read()),
              "time": str(end_date).replace("-", "")}
    with open(f'{os.getcwd()}/users.json', 'r') as users:
        data = json.load(users)

    # convert data to list if not
    if type(data) is dict:
        data = [data]

    # append new item to data lit
    data.append(dumper)

    # write list to file
    with open(f'{os.getcwd()}/users.json', 'w') as users:
        json.dump(data, users, indent=4)


async def delete_key(idcustom):
    import os

    # Путь к вашему shell скрипту
    script_path = "/home/ubuntu/VPNbot/wireguard-install-bot.sh"
    user_input = '3'
    # Вызываем скрипт с перенаправлением вывода в файл
    os.system(f'echo -n "{user_input}" | sudo -S {script_path}> output.txt')

    # Прочитать содержимое файла с выводом
    with open("output.txt", "r") as output_file:
        output = output_file.read()
    await bot.send_message(idcustom, output)
    await Form.namedel.set()

    @dp.message_handler(state=Form.namedel)
    async def process_delname(message: aiogram.types.Message, state: FSMContext):
        user_input = message.text
        await bot.send_message(idcustom, f'Deleting {user_input}...')
        os.system(f"{user_input}")
        await bot.send_message(idcustom, f'Deleted')
        await Form.main.set()


async def adminsendinfo(text, id):
    if id not in admin_users:
        await bot.send_message(admin_users[0], f'{text} ОТ ПОЛЬЗОВАТЕЛЯ {id}')


# command menu
async def setup_bot_commands(dispatcher):
    bot_commands = [
        aiogram.types.BotCommand(command="/start", description="Показать меню"),
        aiogram.types.BotCommand(command="/vpn", description="Свой VPN"),
        aiogram.types.BotCommand(command="/info", description="Показать информацию"),
        aiogram.types.BotCommand(command="/back", description="Назад"),
    ]
    await bot.set_my_commands(bot_commands)


@dp.message_handler(state="*", commands=['start', 'help'])
async def send_welcome(message: aiogram.types.Message, state: FSMContext):
    logging.info(f"Text: {message.text} | ID: {message.from_user.id} | User: {message.from_user.username}")

    ###KEYBOARDS###
    global keyboard, keyboardback, keyboardinstr, keyboardtime, keyboardpay, keyboardcheck, keyboarddebug
    keyboard = aiogram.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard = aiogram.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    if message.from_user.id in admin_users:
        keyboard.add("Debug")
    keyboard.row("VPN🛡", "Кабинет🪪").row("Инфо❓", "Поддержка❗️").row("Инструкция🔰")

    keyboarddebug = aiogram.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboarddebug.add("Add", "Remove")

    keyboardinstr = aiogram.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboardinstr.row('Скачать для телефона с сервера', 'Скачать для компьютера с сервера', 'Назад')

    keyboardback = aiogram.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboardback.add('Назад')

    keyboardtime = aiogram.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboardtime.add('15 дней - бесплатно!')
    for key, value in paymenttime.items():
        keyboardtime.add(f"{key}")

    keyboardcheck = aiogram.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboardcheck.add('Проверить платеж')

    keyboardpay = aiogram.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboardpay.add("Карта")
    ###KEYBOARDS###

    await adminsendinfo(message.text, message.from_user.id)
    await message.reply(open(f'{os.getcwd()}/greeting.txt', 'r', encoding="utf-8").read(), reply_markup=keyboard)
    await Form.main.set()


@dp.message_handler(state="*", text=['назад', 'Назад', '/back', 'cancel', 'Cancel'])
async def backer(message: aiogram.types.Message, state: FSMContext):
    current_state = await state.get_state()
    print(f'Current state = {current_state}')
    match current_state:
        case 'Form:debug1' | 'Form:debug2' | 'Form:debug3' | 'Form:debug4' | 'Form:debugdelete1' | 'Form:debugdelete2':
            await bot.send_message(message.from_user.id, 'Отмена операции.', reply_markup=keyboard)
            await Form.main.set()
        case 'Form:time':
            await bot.send_message(message.from_user.id, 'Назад к меню(', reply_markup=keyboard)
            await Form.main.set()
        case 'Form:payment':
            await bot.send_message(message.from_user.id, "Хочешь выбрать другое время?", reply_markup=keyboardtime)
            await Form.time.set()
        case 'Form:main':
            await bot.send_message(message.from_user.id, 'Вы уже в начале', reply_markup=keyboard)
        case 'Form.instr':
            await bot.send_message(message.from_user.id, 'Возврат в начальное меню', reply_markup=keyboard)
            await Form.main.set()
        case current_state:
            await bot.send_message(message.from_user.id, 'Возврат в начальное меню (ошибка)', reply_markup=keyboard)
            await Form.main.set()


@dp.message_handler(state=Form.main, text=['VPN', "VPN🛡", '/vpn'])
async def echo(message: aiogram.types.Message, state: FSMContext):
    logging.info(f"Text: {message.text} | ID: {message.from_user.id} | User: {message.from_user.username}")

    await adminsendinfo(message.text, message.from_user.id)

    await bot.send_message(message.chat.id, "На какое время Вы хотите ключ? Вы получите сразу оба ключа,"
                                            "\nи outline, и Wireguard", reply_markup=keyboardtime)
    print([key for key in paymenttime.keys()])
    await Form.time.set()


@dp.message_handler(state=Form.time, text=[key for key in paymenttime.keys()])
async def choosepayment(message: aiogram.types.Message, state: FSMContext):
    logging.info(f"Text: {message.text} | ID: {message.from_user.id} | User: {message.from_user.username}")
    global keytime, price
    price = paymenttime[message.text]
    keytime = message.text
    await bot.send_message(message.chat.id, "Отлично, какой способ оплаты Вы выберете?", reply_markup=keyboardpay)
    await Form.payment.set()


@dp.message_handler(state=Form.payment, text=['Карта'])
async def cardpayment(message: aiogram.types.Message, state: FSMContext):
    logging.info(f"Text: {message.text} | ID: {message.from_user.id} | User: {message.from_user.username}")
    await bot.send_message(message.chat.id, "Обработка...", reply_markup=keyboardpay)
    print(price)
    if str(await paymentdef(price)) == 'Success':
        await bot.send_message(message.chat.id, payment_url + "\nПройдите по этой ссылке для оплаты ключа",
                               reply_markup=keyboardcheck)
        await Form.checkpay.set()
    else:
        await bot.send_message(message.chat.id, "Ошибка оплаты, пожалуйста обратитесь к нам в поддержку",
                               reply_markup=keyboardpay)
        await Form.main.set()


@dp.message_handler(state=Form.checkpay, text=['Проверить платеж'])
async def checkpay(message: aiogram.types.Message, state: FSMContext):
    if await paymentcheck() == 'PAID':
        await Form.main.set()
        await create_key(message.chat.id)
    #    elif message.from_user.id in admin_users:
    #        await Form.main.set()
    #        await bot.send_message(message.chat.id, 'ТЕСТОВОЕ ПОЛУЧЕНИЕ')
    #        await create_key(message.chat.id)
    elif await paymentcheck() == 'WAIT':
        await bot.send_message(message.chat.id, 'Платеж еще не оплачен или обрабатывается...')
    elif await paymentcheck() == 'CANCEL':
        await bot.send_message(message.chat.id, 'Платеж был отменен', reply_markup=keyboard)
        await Form.main.set()
    else:
        await bot.send_message(message.chat.id, 'Ошибка')


@dp.message_handler(state=Form.time, text="15 дней - бесплатно!")
async def freerepost(message: aiogram.types.Message, state: FSMContext):
    logging.info(f"Text: {message.text} | ID: {message.from_user.id} | User: {message.from_user.username}")
    await bot.send_message(message.chat.id, "Привет! Появился новый и быстрый VPN сервис VPN4US,"
                                            "\nЕсли интересно - проходи по ссылке - https://t.me/VPNer4bot")
    await bot.send_message(message.chat.id, "Отлично, теперь для получения ключа перешлите пожалуйста"
                                            "\nсообщение выше в VK или Twitter, и пришлите, сюда - @VPN4US_support, скриншот с ним."
                                            "\nКогда мы проверим Ваше сообщение - Вы получите ключ! (для нового ключа нужен будет новый репост)")
    await Form.main.set()


@dp.message_handler(state=Form.main, text=['Кабинет', "Кабинет🪪"])
async def cabinet(message: aiogram.types.Message, state: FSMContext):
    logging.info(f"Text: {message.text} | ID: {message.from_user.id} | User: {message.from_user.username}")
    await bot.send_message(message.chat.id, "Пока в разработке...")


@dp.message_handler(state=Form.main, text=['Инструкция', "Инструкция🔰"])
async def instruction(message: aiogram.types.Message, state: FSMContext):
    logging.info(f"Text: {message.text} | ID: {message.from_user.id} | User: {message.from_user.username}")

    await adminsendinfo(message.text, message.from_user.id)
    await bot.send_message(message.chat.id, open(f'{os.getcwd()}/instruction.txt', 'r', encoding="utf-8").read(),
                           reply_markup=keyboardinstr)
    await Form.instr.set()

    @dp.message_handler(state=Form.instr, text=['Скачать для телефона с сервера'])
    async def downloadapk(message: aiogram.types.Message, state: FSMContext):
        with open(f'{os.getcwd()}/apps/wireguard.apk', 'rb') as file:
            await bot.send_document(message.chat.id, file, caption=f'Файл для установки на Android')

    @dp.message_handler(state=Form.instr, text=['Скачать для компьютера с сервера'])
    async def downloadexe(message: aiogram.types.Message, state: FSMContext):
        with open(f'{os.getcwd()}/apps/wireguard-installer.exe', 'rb') as file:
            await bot.send_document(message.chat.id, file, caption=f'Файл для установки на Windows')


@dp.message_handler(state=Form.main, text=["Инфо", 'Инфо❓', '/info'])
async def echo(message: aiogram.types.Message):
    logging.info(f"Text: {message.text} | ID: {message.from_user.id} | User: {message.from_user.username}")
    # old style:
    # await bot.send_message(message.chat.id, message.text)
    await bot.send_message(message.chat.id, open(f'{os.getcwd()}/info.txt', 'r', encoding="utf-8").read())


@dp.message_handler(state=Form.main, text=['Поддержка', "Поддержка❗️"])
async def cardpayment(message: aiogram.types.Message, state: FSMContext):
    logging.info(f"Text: {message.text} | ID: {message.from_user.id} | User: {message.from_user.username}")
    await bot.send_message(message.chat.id, "Если возникли любые вопросы, проблемы, предложения -"
                                            "\nМы всегда открыты для Вас - @VPN4US_support")


@dp.message_handler(state=Form.main, text=["Debug"])
async def cabinet(message: aiogram.types.Message, state: FSMContext):
    logging.info(f"Text: {message.text} | ID: {message.from_user.id} | User: {message.from_user.username}")
    await bot.send_message(message.chat.id, "DEBUG")
    if message.from_user.id in admin_users:
        await Form.debug1.set()
        await bot.send_message(message.chat.id, 'Success pass', reply_markup=keyboarddebug)
    @dp.message_handler(state=Form.debug1, text=["Add"])
    async def debugadd(message: aiogram.types.Message, state: FSMContext):
        logging.info(f"Text: {message.text} | ID: {message.from_user.id} | User: {message.from_user.username}")
        await bot.send_message(message.chat.id, "Time?", reply_markup=keyboardtime)
        await Form.debug2.set()

        @dp.message_handler(state=Form.debug2, text=[key for key in paymenttime.keys()])
        async def debugfinish(message: aiogram.types.Message, state: FSMContext):
            logging.info(f"Text: {message.text} | ID: {message.from_user.id} | User: {message.from_user.username}")
            await bot.send_message(message.chat.id, "Process...")
            await create_key(message.chat.id)
            print(timetype[paymenttime[message.text]])
            await adduser_json(message.from_user.id, timetype[paymenttime[message.text]])
            await bot.send_message(message.chat.id,
                                   f"ID - {open(f'/etc/wireguard/VPNBOT/usercounter.var', 'r').read()}",
                                   reply_markup=keyboard)
            await Form.main.set()

    @dp.message_handler(state=Form.debug1, text=["Remove"])
    async def debugadd(message: aiogram.types.Message, state: FSMContext):
        logging.info(f"Text: {message.text} | ID: {message.from_user.id} | User: {message.from_user.username}")
        await bot.send_message(message.chat.id, "Which one?", reply_markup=keyboard)
        await delete_key(message.chat.id)
        await Form.removedebug.set()


# reply_markup=aiogram.types.ReplyKeyboardRemove()
if __name__ == '__main__':
    aiogram.executor.start_polling(dp, skip_updates=True, on_startup=setup_bot_commands)

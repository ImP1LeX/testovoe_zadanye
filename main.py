import random
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from config import TOKEN_BOT
from DB import db_start, create_user, update_msg_count, update_msg_time, update_kb_text, user_select, kb_select, ban_user, unban_user, select_ban_user

storage = MemoryStorage()
bot = Bot(TOKEN_BOT)
dp = Dispatcher(bot=bot, storage=storage)

class KeyboardStatesGroup(StatesGroup):
    add = State()
    rm = State()


banned_users = set()
banned_users_time = []
user_button = set()

async def on_startup(_):
    await db_start()
    ban_users = await select_ban_user()
    if ban_users != []:
        for user in ban_users:
            banned_users.add(user[0])
            banned_users_time.append([user[0], user[1]])

async def time_converter(time):
    a = str(time).split(":")
    return int(a[0])*3600 + int(a[1])*60 + int(a[2])

async def user_keyboard(user_id) -> types.ReplyKeyboardMarkup:
    kb_text = await kb_select(user_id)
    kb_text = str(kb_text[0])
    kb_text = kb_text.replace('(', '')
    kb_text = kb_text.replace(')', '')
    kb_text = kb_text.replace(',', '')
    kb_text = kb_text.replace("'", '')
    kb_text = kb_text.split(' ')
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for text in kb_text:
        kb.add(types.KeyboardButton(text))
        user_button.add(text)
    return kb

@dp.message_handler(lambda msg: msg.from_user.id in banned_users)
async def handle_banned(msg: types.Message):
    date_time = str(msg.date).split()
    date = date_time[0].split("-")
    time = date_time[1]
    for i in range(len(banned_users_time)):
        if banned_users_time[i][0] == msg.from_user.id:
            date_time_user = banned_users_time[i][1].split()
            date_user = date_time_user[0].split("-")
            time_user = date_time_user[1]
            if int(date_user[0]) > int(date[0]) or int(date_user[1]) > int(date[1]) or int(date_user[2]) > int(date[2]) or await time_converter(time_user) - await time_converter(time) <= -600:
                await unban_user(msg.from_user.id)
                banned_users.discard(msg.from_user.id)
                banned_users_time.pop(i)
                await msg.answer("Вы были разблокированны!")
                return True
    await msg.answer("Вы заблокированы!")
    return True

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await create_user(message.from_user.id, message.from_user.full_name)
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton("/value"), types.KeyboardButton("/add"), types.KeyboardButton("/rm")]],
        resize_keyboard=True
    )
    await message.answer("Для выбора валюты напишите /value, для добовления валюты напишите /add, для удаления валюты напишите /rm.",
                         reply_markup=keyboard)

@dp.message_handler(commands=["value"])
async def cmd_value(message: types.Message):
    await message.answer("Выберите валюту.", reply_markup=await user_keyboard(message.from_user.id))

@dp.message_handler(commands=["add"])
async def cmd_add_state(message: types.Message):
    await message.answer("Введите название валюты.")
    await KeyboardStatesGroup.add.set()

@dp.message_handler(state=KeyboardStatesGroup.add)
async def cmd_add(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        a = await kb_select(message.from_user.id)
        a = str(a[0])
        a = a.replace('(', '')
        a = a.replace(')', '')
        a = a.replace(',', '')
        a = a.replace("'", '')
        text = ' '.join([str(a), str(message.text)])
        await update_kb_text(message.from_user.id, text)
    await state.finish()

@dp.message_handler(commands=["rm"])
async def cmd_add_state(message: types.Message):
    await message.answer("Введите название валюты.")
    await KeyboardStatesGroup.rm.set()

@dp.message_handler(state=KeyboardStatesGroup.rm)
async def cmd_rm(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        b = str
        text_id = 0
        a = await kb_select(message.from_user.id)
        a = str(a[0])
        a = a.replace('(', '')
        a = a.replace(')', '')
        a = a.replace(',', '')
        a = a.replace("'", '')
        a = str(a).split(' ')
        for text in a:
            if text == str(message.text):
                continue
            elif b == 0:
                b = text
            else:
                b = ' '.join(b, text)
            text_id += 1
        await update_kb_text(message.from_user.id, b)
    await state.finish()

@dp.message_handler(lambda message: message.text in user_button)
async def dollar_cmd(message: types.Message):
    user = await user_select(message.from_user.id)
    if user[0][3] == 0:
        await update_msg_time(message.from_user.id, await time_converter(message.date.time()))
    if user[0][3] - await time_converter(message.date.time()) <= -60:
        await update_msg_time(message.from_user.id, await time_converter(message.date.time()))
        await update_msg_count(message.from_user.id, 0)
    if user[0][2] < 6:
        await update_msg_count(message.from_user.id, user[0][2] + 1)
    elif user[0][2] == 6:
        await ban_user(message.from_user.id, str(message.date))
        banned_users_time.append([message.from_user.id, str(message.date)])
        banned_users.add(message.from_user.id)
        await update_msg_count(message.from_user.id, 0)
    await message.answer(f"Цена: {random.randint(1, 100)}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

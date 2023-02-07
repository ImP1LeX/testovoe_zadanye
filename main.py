from aiogram import Bot, Dispatcher, executor, types
import random
from config import TOKEN_BOT

bot = Bot(TOKEN_BOT)
dp = Dispatcher(bot=bot)

memory_users = []
banned_users = set()
banned_users_time = []

async def time_converter(time):
    a = str(time).split(":")
    return int(a[0])*3600 + int(a[1])*60 + int(a[2])


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
                banned_users.discard(msg.from_user.id)
                banned_users_time.pop(i)
                await msg.answer("Вы были разблокированны!")
                return True
    await msg.answer("Вы заблокированы!")
    return True


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    memory_users.append([message.from_user.id, message.from_user.full_name, 0, 0])
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="Доллары"),types.KeyboardButton(text="Евро")],],
        resize_keyboard=True
    )
    await message.answer("Выберите валюту", reply_markup=keyboard)

@dp.message_handler(text=["Доллары","Евро"])
async def dollar_cmd(message: types.Message):
    print(str(message.date))
    for i in range(len(memory_users)):
        if memory_users[i][0] == message.from_user.id:
            if memory_users[i][3] == 0:
                memory_users[i][3] = await time_converter(message.date.time())
            if memory_users[i][3] - await time_converter(message.date.time()) <= -60:
                memory_users[i][3] = await time_converter(message.date.time())
                memory_users[i][2] = 0
            if memory_users[i][2] < 5:
                memory_users[i][2] += 1
            elif memory_users[i][2] == 5:
                banned_users_time.append([message.from_user.id, str(message.date)])
                banned_users.add(message.from_user.id)
                memory_users[i][2] = 0

    await message.answer(f"Цена: {random.randint(1, 100)}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

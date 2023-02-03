from aiogram import Bot, Dispatcher, executor, types

DOLLAR = 70.07
EURO = 77.02

bot = Bot(token="5479233793:AAH9JgA6kuSIT9q_4v_K1Gl4BdD3E2k_IBs")
dp = Dispatcher(bot=bot)

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    kb = [
        [
        types.KeyboardButton(text="Доллары"),
        types.KeyboardButton(text="Евро")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )
    await message.answer("Выберите валюту", reply_markup=keyboard)

@dp.message_handler(text=["Доллары"])
async def dollar_cmd(message: types.Message):
    await message.answer(f"Цена: {DOLLAR}")

@dp.message_handler(text=["Евро"])
async def euro_cmd(message: types.Message):
    await message.answer(f"Цена: {EURO}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

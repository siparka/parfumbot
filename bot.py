import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    KeyboardButtonRequestChat,
)
import sys
import os

print("BOT_TOKEN =", os.getenv("BOT_TOKEN"))
print("ADMIN_ID =", os.getenv("ADMIN_ID"))

TOKEN = os.getenv("BOT_TOKEN")
ADMIN = os.getenv("ADMIN_ID")

if not TOKEN:
    raise ValueError("BOT_TOKEN не найден")

if not ADMIN:
    raise ValueError("ADMIN_ID не найден")

ADMIN_ID = int(ADMIN)

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
if not TOKEN:
    raise ValueError("Переменная BOT_TOKEN не найдена!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ========== СОСТОЯНИЯ ==========
class Survey(StatesGroup):
    q1 = State(); q2 = State(); q3 = State(); q4 = State()
    q5 = State(); q6 = State(); q7 = State(); q8 = State()
    phone = State()

def make_keyboard(options):
    buttons = [[KeyboardButton(text=opt)] for opt in options]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

QUESTIONS = {
    "q1": {
        "text": "❓ Вопрос 1/8\n\nРасскажите, кто вы?\n\n1️⃣ Хочу начать свой бизнес с нуля\n2️⃣ Уже есть опыт в продажах\n3️⃣ Занимаюсь парфюмерией/косметикой\n4️⃣ Блогер / инфлюенсер\n5️⃣ У меня есть розничный магазин\n6️⃣ Просто изучаю возможности",
        "options": ["1️⃣ Хочу начать с нуля", "2️⃣ Есть опыт в продажах", "3️⃣ Занимаюсь парфюмерией", "4️⃣ Блогер / инфлюенсер", "5️⃣ Есть розничный магазин", "6️⃣ Изучаю возможности"]
    },
    "q2": {
        "text": "❓ Вопрос 2/8\n\nКакой у вас сейчас основной источник дохода?\n\n1️⃣ Работа по найму\n2️⃣ Свой бизнес\n3️⃣ Фриланс / самозанятость\n4️⃣ Инвестиции / пассивный доход\n5️⃣ Временно без работы / ищу варианты",
        "options": ["1️⃣ Работа по найму", "2️⃣ Свой бизнес", "3️⃣ Фриланс / самозанятость", "4️⃣ Инвестиции", "5️⃣ Временно без работы"]
    },
    "q3": {
        "text": "❓ Вопрос 3/8\n\nЧто для вас самое важное в новом деле?\n\n1️⃣ Высокий доход\n2️⃣ Свободный график\n3️⃣ Работа из дома\n4️⃣ Возможность расти\n5️⃣ Работать с красивым продуктом",
        "options": ["1️⃣ Высокий доход", "2️⃣ Свободный график", "3️⃣ Работа из дома", "4️⃣ Возможность расти", "5️⃣ Красивый продукт"]
    },
    "q4": {
        "text": "❓ Вопрос 4/8\n\nКакой бюджет вы готовы вложить в старт?\n\n1️⃣ До 50 000 ₽\n2️⃣ 50 000 - 150 000 ₽\n3️⃣ 150 000 - 500 000 ₽\n4️⃣ Более 500 000 ₽\n5️⃣ Пока не знаю, смотрю варианты\n\n💡 Средний старт партнёра — 150 000 ₽, окупаемость 2-3 месяца.",
        "options": ["1️⃣ До 50 000 ₽", "2️⃣ 50 000 - 150 000 ₽", "3️⃣ 150 000 - 500 000 ₽", "4️⃣ Более 500 000 ₽", "5️⃣ Пока не знаю"]
    },
    "q5": {
        "text": "❓ Вопрос 5/8\n\nЕсть ли у вас своя аудитория или каналы коммуникации?\n\n1️⃣ Да, веду блог / ТГ-канал / YouTube\n2️⃣ Да, есть чаты и группы\n3️⃣ Да, есть клиентская база\n4️⃣ Нет, начну с нуля\n5️⃣ Планирую создать",
        "options": ["1️⃣ Есть блог/канал", "2️⃣ Есть чаты/группы", "3️⃣ Есть клиентская база", "4️⃣ Нет, начну с нуля", "5️⃣ Планирую создать"]
    },
    "q6": {
        "text": "❓ Вопрос 6/8\n\nСколько времени в день вы готовы уделять бизнесу?\n\n1️⃣ До 2 часов (хобби)\n2️⃣ 2-4 часа (полдня)\n3️⃣ 4-6 часов (активный рост)\n4️⃣ Полный рабочий день\n5️⃣ Всё свободное время (горю желанием!)",
        "options": ["1️⃣ До 2 часов", "2️⃣ 2-4 часа", "3️⃣ 4-6 часов", "4️⃣ Полный рабочий день", "5️⃣ Всё свободное время"]
    },
    "q7": {
        "text": "❓ Вопрос 7/8\n\nЧто вас больше всего останавливает от старта?\n\n1️⃣ Страх, что не получится\n2️⃣ Не хватает опыта в продажах\n3️⃣ Боюсь вкладывать деньги без гарантий\n4️⃣ Не знаю, как найти клиентов\n5️⃣ Ничего не останавливает — хочу начать!\n\n💡 80% наших партнёров начинали с нуля.",
        "options": ["1️⃣ Страх неудачи", "2️⃣ Нет опыта в продажах", "3️⃣ Боюсь вкладывать деньги", "4️⃣ Не знаю как найти клиентов", "5️⃣ Ничего не останавливает"]
    },
    "q8": {
        "text": "❓ Вопрос 8/8\n\nКакой доход вы хотели бы выйти через 3-6 месяцев?\n\n1️⃣ 50 000 - 100 000 ₽/мес\n2️⃣ 100 000 - 200 000 ₽/мес\n3️⃣ 200 000 - 500 000 ₽/мес\n4️⃣ Более 500 000 ₽/мес\n5️⃣ Пока не загадываю\n\n💎 Топ-партнёры зарабатывают от 300 000 ₽/мес.",
        "options": ["1️⃣ 50-100 тыс. ₽", "2️⃣ 100-200 тыс. ₽", "3️⃣ 200-500 тыс. ₽", "4️⃣ Более 500 тыс. ₽", "5️⃣ Пока не загадываю"]
    }
}

# ========== ОБРАБОТЧИКИ ==========
@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Привет! Я помощник Егора, руководителя партнёрской сети ParfumBusiness.\n\n"
        "За 3 минуты отвечу на 8 вопросов и расскажу, подходит ли вам наш формат партнёрства.\n\n"
        "А главное — мы уже подготовили для вас:\n"
        "✅ Готовую модель запуска продаж\n"
        "✅ Обучение с нуля\n"
        "✅ Поддержку на старте\n\n"
        "🔽 Начнём?",
        reply_markup=make_keyboard(["✅ Да, хочу узнать", "❌ Просто смотрю"])
    )

@dp.message(F.text.in_(["✅ Да, хочу узнать", "❌ Просто смотрю"]))
async def handle_start_choice(message: types.Message, state: FSMContext):
    if message.text == "❌ Просто смотрю":
        await message.answer("Хорошо! Если передумаете — просто напишите /start", reply_markup=ReplyKeyboardRemove())
        return
    await ask_question(message, state, "q1")

async def ask_question(message: types.Message, state: FSMContext, q_key: str):
    q = QUESTIONS[q_key]
    await state.update_data(current_q=q_key)
    await state.set_state(getattr(Survey, q_key))
    await message.answer(q["text"], reply_markup=make_keyboard(q["options"]))

@dp.message(Survey.q1)
async def p1(message: types.Message, state: FSMContext):
    await state.update_data(q1=message.text)
    await ask_question(message, state, "q2")


@dp.message(Survey.q2)
async def p2(message: types.Message, state: FSMContext):
    await state.update_data(q2=message.text)
    await ask_question(message, state, "q3")


@dp.message(Survey.q3)
async def p3(message: types.Message, state: FSMContext):
    await state.update_data(q3=message.text)
    await ask_question(message, state, "q4")


@dp.message(Survey.q4)
async def p4(message: types.Message, state: FSMContext):
    await state.update_data(q4=message.text)
    await ask_question(message, state, "q5")


@dp.message(Survey.q5)
async def p5(message: types.Message, state: FSMContext):
    await state.update_data(q5=message.text)
    await ask_question(message, state, "q6")


@dp.message(Survey.q6)
async def p6(message: types.Message, state: FSMContext):
    await state.update_data(q6=message.text)
    await ask_question(message, state, "q7")


@dp.message(Survey.q7)
async def p7(message: types.Message, state: FSMContext):
    await state.update_data(q7=message.text)
    await ask_question(message, state, "q8")

@dp.message(Survey.q8)
async def p8(message: types.Message, state: FSMContext):
    await state.update_data(q8=message.text)
    await state.set_state(Survey.phone)
    await message.answer(
        "📱 Супер! Остался последний шаг.\n\nОставьте свой номер телефона — Егор свяжется с вами в ближайшее время.\n\n📞 Ваш номер:",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(Survey.phone)
async def process_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    report = (f"🔔 НОВЫЙ ЛИД!\n\n📞 Телефон: {message.text}\n\n"
              f"1️⃣ {data.get('q1')}\n2️⃣ {data.get('q2')}\n3️⃣ {data.get('q3')}\n"
              f"4️⃣ {data.get('q4')}\n5️⃣ {data.get('q5')}\n6️⃣ {data.get('q6')}\n"
              f"7️⃣ {data.get('q7')}\n8️⃣ {data.get('q8')}\n\n"
              f"👤 {message.from_user.full_name} (@{message.from_user.username or 'нет'})")
    await bot.send_message(ADMIN_ID, report)
    await message.answer("✅ Спасибо! Егор свяжется с вами в ближайшее время. До встречи! 🚀")
    await state.clear()

async def main():
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from databases import create_course, insert_course, fetch_course_by_id
import asyncio
from dotenv import load_dotenv
import os
load_dotenv()

TOKEN = os.getenv('TOKEN')
ADMIN_ID = int(os.getenv ('ADMIN_ID')) 

bot = Bot(token=TOKEN)
dp = Dispatcher()

class addStudent(StatesGroup):
    course_name = State()
    course_price = State()
    description = State()
    teacher_info = State()

def reply_button():
    kbs = [
        [types.KeyboardButton(text='O\'quv kurslar')],
        [types.KeyboardButton(text='Bizning afzalliklarimiz')],
        [types.KeyboardButton(text="Kurs qo'shish")]
    ]
    btns = types.ReplyKeyboardMarkup(keyboard=kbs, resize_keyboard=True)
    return btns


@dp.message(CommandStart())
async def start(message: Message):
    await message.reply(
        text=f'{message.from_user.first_name} Assalomu alaykum\nSoff study otimizga xush kelibsiz.',
        reply_markup=reply_button()) 
    create_course()

@dp.message(lambda message: message.text == 'Bizning afzalliklarimiz')
async def course_advantage(message: Message):
    await message.reply(
        text='Bizning afzalliklarimiz:\n\tMalakali o\'qituvchilar\n\tAmaliy darslar ko\'pligi'
    )

@dp.message(lambda message: message.text == "O'quv kurslar")
async def course_study(message: Message):
    db_course = fetch_course_by_id()  
    if db_course:
        builder = InlineKeyboardMarkup(
        inline_keyboard = [
            [InlineKeyboardButton(text=course[1], callback_data=f'course_{i}')]
            for i , course in enumerate(db_course)
        ]
        )
        await message.answer("Kurslar ro'yxati:", reply_markup=builder)
    else:
        await message.answer("Kurslar mavjud emas.")

@dp.callback_query(lambda c: c.data and c.data.startswith('course_'))
async def process_callback(callback_query: types.CallbackQuery):
    db_course = fetch_course_by_id()
    course_index = int(callback_query.data.split('_')[1]) 
    if course_index < len(db_course):
        course = db_course[course_index]
        course_info = (
                f"Kurs nomi: {course[1]}\n"
                f"Kurs narxi: {course[2]}\n"
                f"Kurs haqida: {course[3]}\n"
                f"O'qituvchi: {course[4]}"
            )
        await callback_query.message.reply(course_info)
    else:
        await callback_query.answer("Kurs topilmadi.")

@dp.message(lambda message: message.text == "Kurs qo'shish")
async def set_course_name(message: Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        await message.answer(text='Kurs nomi kiriting: ')
        await state.set_state(addStudent.course_name)
    else:
        await message.reply("Uzur!\nSiz bu bo'limdan foydalana olmaysiz")

@dp.message(addStudent.course_name)
async def set_course_price(message: Message, state: FSMContext):
    await state.update_data(course_name=message.text)
    await message.answer(text='Kurs narxini kiriting: ')
    await state.set_state(addStudent.course_price)

@dp.message(addStudent.course_price)
async def set_description(message: Message, state: FSMContext):
    await state.update_data(course_price=message.text)
    await message.answer(text='Kurs haqida ma\'lumot kiriting: ')
    await state.set_state(addStudent.description)

@dp.message(addStudent.description)
async def set_teacher_info(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(text='Kurs o\'qituvchisi haqida ma\'lumot kiriting: ')
    await state.set_state(addStudent.teacher_info)

@dp.message(addStudent.teacher_info)
async def finalize_course(message: Message, state: FSMContext):
    await state.update_data(teacher_info=message.text)
    data = await state.get_data()
    insert_course(data['course_name'], data['course_price'], data['description'], data['teacher_info'])
    course_info = (
        f"Kurs nomi: {data['course_name']}\n"
        f"Kurs narxi: {data['course_price']}\n"
        f"Kurs haqida: {data['description']}\n"
        f"O'qituvchi: {data['teacher_info']}"
    )
    await message.answer(text=f"Kurs muvaffaqiyatli qo'shildi:\n\n{course_info}")
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
from app.load_texts import load_texts

router = Router()

questions = load_texts(r'C:\Users\oleg7\tgb\app\ovz.json')["modul_2"]

    
class SurveyStates(StatesGroup):
    start = State()
    @staticmethod
    def get_question_state(question_id: int) -> State:
        return State(state=f'question_{question_id}')
    
   
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("Начало", reply_markup=kb.ready)
    await state.set_state(state=SurveyStates.start)


@router.message(Command('stop'))
async def cmd_stop(message: Message, state: FSMContext):
    await message.answer("Завершение")
    await state.clear()


@router.message(SurveyStates.start)
async def start_survey(message: Message, state: FSMContext):
    if questions:
        await state.set_state(SurveyStates.get_question_state(questions[0]["id"]))
        await ask_question(message, questions[0])


@router.message(F.text)
async def handle_question(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if not current_state or not current_state.startswith("@:question_"):
        return 

    question_id = int(current_state.split("_")[1])
    print(f"Текущий вопрос ID: {question_id}")

    current_question = next((q for q in questions if q["id"] == question_id), None)
    if not current_question:
        await message.answer("Ошибка: вопрос не найден.")
        return

    next_question_id = question_id + 1
    next_question = next((q for q in questions if q["id"] == next_question_id), None)
    if next_question:
        await state.set_state(SurveyStates.get_question_state(next_question_id))
        await ask_question(message, next_question)
    else:
        await message.answer("Спасибо за участие в опросе!")
        await state.clear()


async def ask_question(message: Message, question: dict):
    if question["type"] == "text":
        await message.answer(question["text"])
    """
    elif question["type"] == "image":
        with open(f"data/images/{question['image']}", "rb") as photo:
            await message.answer_photo(photo, caption=question["text"])
    """
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
from app.load_texts import load_texts

router = Router()

texts = load_texts(r'C:\Users\oleg7\tgb\app\texts.json')

    
class SurveyStates(StatesGroup):
    m1_q1 = State()
    m1_q2 = State()
    m1_q3 = State()
    m1_q4 = State()
    m1_q5 = State()
    m1_q6 = State()
    m1_q7 = State()
    m1_q8 = State()
    m1_q9 = State()
    m1_q10 = State()
    m2 = State()
    

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(SurveyStates.m1_q1)
    await message.answer(texts["start"])
    await message.answer(texts["ready"], reply_markup=kb.ready)


@router.message(SurveyStates.m1_q1)
async def q1(message: Message, state: FSMContext):
    await state.set_state(SurveyStates.m1_q2)
    await message.answer(texts["q1"], reply_markup=kb.q1)


@router.message(SurveyStates.m1_q2)
async def q2(message: Message, state: FSMContext):
    await state.set_state(SurveyStates.m1_q3)
    await message.answer(texts["q2"], reply_markup=kb.q2)


@router.message(SurveyStates.m1_q3)
async def q3(message: Message, state: FSMContext):
    await state.set_state(SurveyStates.m1_q4)
    await message.answer(texts["q3"], reply_markup=kb.q3)


@router.message(SurveyStates.m1_q4)
async def q4(message: Message, state: FSMContext):
    await state.set_state(SurveyStates.m1_q5)
    await message.answer(texts["q4"], reply_markup=kb.q4)


@router.message(SurveyStates.m1_q5)
async def q5(message: Message, state: FSMContext):
    await state.set_state(SurveyStates.m1_q6)
    await message.answer(texts["q5"], reply_markup=kb.q5)


@router.message(SurveyStates.m1_q6)
async def q6(message: Message, state: FSMContext):
    await state.set_state(SurveyStates.m1_q7)
    await message.answer(texts["q6"], reply_markup=kb.q6)


@router.message(SurveyStates.m1_q7)
async def q7(message: Message, state: FSMContext):
    await state.set_state(SurveyStates.m1_q8)
    await message.answer(texts["q7"], reply_markup=kb.q7)


@router.message(SurveyStates.m1_q8)
async def q8(message: Message, state: FSMContext):
    await state.set_state(SurveyStates.m1_q9)
    await message.answer(texts["q8"], reply_markup=kb.q8)


@router.message(SurveyStates.m1_q9)
async def q9(message: Message, state: FSMContext):
    await state.set_state(SurveyStates.m1_q10)
    await message.answer(texts["q9"], reply_markup=kb.q9)


@router.message(SurveyStates.m1_q10)
async def q10(message: Message, state: FSMContext):
    await state.set_state(SurveyStates.m2)
    await message.answer(texts["q10"], reply_markup=kb.q10)


@router.message(SurveyStates.m2)
async def m2(message: Message):
    await message.answer(texts["m2"], reply_markup=ReplyKeyboardRemove())
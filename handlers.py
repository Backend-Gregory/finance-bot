import logging
from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from config import TOKEN
from database import session, Transaction
from keyboards import main_kb, export_kb
from states import TransactionForm

router = Router()

@router.message(Command('start'))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        '💰 Привет! Я бот для учёта доходов и расходов.\n\n'

        '➕ Добавить — записать доход или расход\n'
        '📊 Статистика — посмотреть баланс\n'
        '📁 Экспорт — выгрузить отчёт (CSV, Excel, Google Sheets)',
        reply_markup=main_kb
    )
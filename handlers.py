import logging
from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from config import TOKEN
from database import session, Transaction
from keyboards import main_kb, export_kb, type_kb
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

@router.callback_query(lambda x: x.data == 'add_transaction')
async def transaction_type(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TransactionForm.transaction_type)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer('Выберите тип транзакции', reply_markup=type_kb)
    await callback.answer()

@router.callback_query(TransactionForm.transaction_type)
async def amount(callback: CallbackQuery, state: FSMContext):
    await state.update_data(transaction_type=callback.data)
    await state.set_state(TransactionForm.amount)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer('Введите сумму транзакции')
    await callback.answer()

@router.message(TransactionForm.amount)
async def process_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(',', '.'))
        data = await state.get_data()
        
        if data.get('transaction_type') == 'income':
            amount = abs(amount)
        else:
            amount = -abs(amount)
        
        await state.update_data(amount=amount)
        await state.set_state(TransactionForm.category)
        await message.answer('📂 Введи категорию (например: еда, транспорт, зарплата)')
    except ValueError:
        await message.answer('❌ Ошибка! Введи число. Например: 5000')

@router.message(TransactionForm.category)
async def process_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await state.set_state(TransactionForm.note)
    await message.answer('📝 Введи описание (например: Обед или Зарплата)')
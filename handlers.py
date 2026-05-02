import logging
from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, BufferedInputFile

from config import TOKEN
from database import session, Transaction
from keyboards import main_kb, export_kb, type_kb, period_kb
from states import TransactionForm
from datetime import datetime, timedelta
from utils import format_statistics, export_to_csv
from sqlalchemy import select

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

@router.message(TransactionForm.note)
async def process_note(message: types.Message, state: FSMContext):
    await state.update_data(note=message.text)
    data = await state.get_data()

    transaction = Transaction(  
        user_id=message.from_user.id,
        amount=data.get('amount'),
        category=data.get('category'),
        note=data.get('note')
    )
    try:
        session.add(transaction)
        session.commit()
        await message.answer('✅ Добавление прошло успешно', reply_markup=main_kb)
    except Exception as e:
        session.rollback()
        print(f'Ошибка в БД: {e}')
        await message.answer('❌ Техническая ошибка попробуйте позже')
    
    await state.clear()

@router.callback_query(lambda x: x.data == 'stats')
async def stats(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer('📊 Выбери период', reply_markup=period_kb)
    await callback.answer()

@router.callback_query(lambda x: x.data == 'all_time')
async def stats_all_time(callback: CallbackQuery):
    user_id = callback.from_user.id
    text = format_statistics("всё время", user_id, datetime.min)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(text, reply_markup=main_kb)
    await callback.answer()

@router.callback_query(lambda x: x.data == 'month')
async def stats_month(callback: CallbackQuery):
    month_ago = datetime.now() - timedelta(days=30)
    user_id = callback.from_user.id
    text = format_statistics("месяц", user_id, month_ago)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(text, reply_markup=main_kb)
    await callback.answer()

@router.callback_query(lambda x: x.data == 'week')
async def stats_week(callback: CallbackQuery):
    week_ago = datetime.now() - timedelta(days=7)
    user_id = callback.from_user.id
    text = format_statistics("неделю", user_id, week_ago)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(text, reply_markup=main_kb)
    await callback.answer()

@router.callback_query(lambda x: x.data == 'day')
async def stats_day(callback: CallbackQuery):
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    user_id = callback.from_user.id
    text = format_statistics("сегодня", user_id, today)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(text, reply_markup=main_kb)
    await callback.answer()

@router.callback_query(lambda x: x.data == 'back_to_menu')
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer('Главное меню', reply_markup=main_kb)
    await callback.answer()

@router.callback_query(lambda x: x.data == 'export')
async def export(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer('Выберите формат экспорта', reply_markup=export_kb)
    await callback.answer()

@router.callback_query(lambda x: x.data == 'csv')
async def export_csv(callback: CallbackQuery):
    user_id = callback.from_user.id
    transactions = session.execute(select(Transaction).where(Transaction.user_id == user_id)).scalars().all()
    
    if not transactions:
        await callback.message.answer('📭 Нет транзакций для экспорта', reply_markup=main_kb)
        await callback.answer()
        return
    
    csv_data = export_to_csv(transactions)
    file = BufferedInputFile(csv_data, filename='transactions.csv')
    await callback.message.answer_document(file, caption='📁 Ваш экспорт', reply_markup=main_kb)
    await callback.answer()
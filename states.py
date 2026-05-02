from aiogram.fsm.state import State, StatesGroup

class TransactionForm(StatesGroup):
    amount = State()
    category = State()
    note = State()
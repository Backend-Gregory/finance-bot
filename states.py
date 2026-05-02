from aiogram.fsm.state import State, StatesGroup

class TransactionForm(StatesGroup):
    transaction_type = State()
    amount = State()
    category = State()
    note = State()
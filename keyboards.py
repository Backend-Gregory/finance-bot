from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить", callback_data="add_transaction")],
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="stats"),
            InlineKeyboardButton(text="📁 Экспорт", callback_data="export"),
        ]
    ]
)

type_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Доход", callback_data="income"),
            InlineKeyboardButton(text="Расход", callback_data="expense")
        ]
    ]
)

period_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='📅 Всё время', callback_data='all_time'),
            InlineKeyboardButton(text='📆 Месяц', callback_data='month'),
        ],
        [
            InlineKeyboardButton(text='📆 Неделя', callback_data='week'),
            InlineKeyboardButton(text='📆 Сегодня', callback_data='day'),
        ],
        [InlineKeyboardButton(text='🔙 Назад', callback_data='back')]
    ]
)

export_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📄 CSV", callback_data="csv"),
            InlineKeyboardButton(text="📊 Excel", callback_data="excel"),
        ],
        [InlineKeyboardButton(text="🌐 Google Sheets", callback_data="google_sheets")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]

    ]
)
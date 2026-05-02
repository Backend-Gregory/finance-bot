from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить", callback_data="add_transaction")],
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="statistics"),
            InlineKeyboardButton(text="📁 Экспорт", callback_data="export"),
        ]
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
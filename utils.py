from collections import defaultdict
from sqlalchemy import select
from database import session, Transaction
from datetime import datetime
import csv
from io import StringIO
from openpyxl import Workbook
from io import BytesIO
import gspread
from google.oauth2.service_account import Credentials
import logging

def format_statistics(period_name: str, user_id: int, date: datetime) -> str:
    transactions = session.execute(select(Transaction).where(Transaction.user_id == user_id, Transaction.created_at >= date)).scalars().all()
    
    if not transactions:
        return f"📭 Нет транзакций за {period_name}"
    
    income = sum(t.amount for t in transactions if t.amount > 0)
    expense = sum(-t.amount for t in transactions if t.amount < 0)
    balance = income - expense
    count = len(transactions)

    avg = (income + expense) / count if count > 0 else 0

    expenses = [t for t in transactions if t.amount < 0]
    cat_spending = defaultdict(float)
    for e in expenses:
        cat_spending[e.category] += -e.amount
    
    top_categories = sorted(cat_spending.items(), key=lambda x: x[1], reverse=True)[:3]

    text = f"📊 Статистика за {period_name}\n\n"
    text += f"💰 Доходы:       {income:,.0f} ₽\n"
    text += f"💸 Расходы:      {expense:,.0f} ₽\n"
    text += f"📊 Баланс:       {balance:,.0f} ₽\n\n"
    text += f"📈 Количество:   {count} транзакций\n"
    text += f"📉 Средний чек:  {avg:,.0f} ₽\n\n"
    text += f"🔥 Топ категории:\n"

    if top_categories:
        for cat, amount in top_categories:
            text += f"   • {cat}:      {amount:,.0f} ₽\n"
    else:
        text += "   • нет расходов\n"
    
    return text

def export_to_csv(transactions):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Сумма", "Категория", "Описание", "Дата"])
    
    for t in transactions:
        writer.writerow([t.id, t.amount, t.category, t.note, t.created_at.strftime('%Y-%m-%d %H:%M:%S')])
    
    return output.getvalue().encode('utf-8')

def export_to_excel(transactions):
    wb = Workbook()
    ws = wb.active
    ws.append(["ID", "Сумма", "Категория", "Описание", "Дата"])
    
    for t in transactions:
        ws.append([t.id, t.amount, t.category, t.note, t.created_at.strftime('%Y-%m-%d %H:%M:%S')])
    
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()

def export_to_google_sheets(transactions, user_id):
    try:
        gc = gspread.service_account('google_key.json')
        sheet_name = f'Finance_User_{user_id}'

        try:
            sh = gc.open(sheet_name)
            worksheet = sh.sheet1
            worksheet.clear()
        except gspread.SpreadsheetNotFound:
            sh = gc.create(sheet_name)
            worksheet = sh.sheet1
            sh.share(None, perm_type='anyone', role='reader')

        worksheet.append_row(["ID", "Сумма", "Категория", "Описание", "Дата"])
        for t in transactions:
            worksheet.append_row([
                t.id,
                t.amount,
                t.category,
                t.note,
                t.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

        url = f"https://docs.google.com/spreadsheets/d/{sh.id}/edit?usp=sharing"
        return url
    
    except Exception as e:
        logging.error(f'Ошибка экспорта в Google Sheets: {e}', exc_info=True)
        return None
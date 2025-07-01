from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def create_keyboard(commands: list):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*commands)
    return keyboard

def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)

def format_table(columns, data):
    # Проверяем, есть ли данные
    if not data:
        return None

    # Определяем ширину столбцов
    column_widths = [max(len(str(item)) for item in [col] + [row[i] for row in data]) for i, col in enumerate(columns)]

    # Формируем строку с заголовками
    header = " | ".join(f"{columns[i]:<{column_widths[i]}}" for i in range(len(columns)))
    separator = "-+-".join('-' * width for width in column_widths)

    # Формируем строки с данными
    rows = "\n".join(" | ".join(f"{str(row[i]):<{column_widths[i]}}" for i in range(len(columns))) for row in data)

    # Собираем итоговый вывод
    table = '<pre>\n' + f"{header}\n{separator}\n{rows}" + '\n</pre>'
    return table
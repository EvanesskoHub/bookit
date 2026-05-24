from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Главное меню (снизу)
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📚 Мои книги"), KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="✍️ Добавить книгу"), KeyboardButton(text="💬 Цитаты")],
        [KeyboardButton(text="📊 Дашборд"), KeyboardButton(text="❓ Помощь")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выбери действие..."
)

# Инлайн-кнопка "Пропустить"
def skip_button(callback_data: str = "skip") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏭ Пропустить", callback_data=callback_data)]
    ])
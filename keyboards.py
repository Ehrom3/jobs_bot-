from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)


def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💼 Вакансии"), KeyboardButton(text="➕ Добавить работу")],
            [KeyboardButton(text="📂 Категории"), KeyboardButton(text="❓ Help")]
        ],
        resize_keyboard=True
    )


def category_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Показать категории", callback_data="category_show")],
        [InlineKeyboardButton(text="➕ Добавить категорию", callback_data="category_add")],
        [InlineKeyboardButton(text="✏️ Изменить категорию", callback_data="category_update")],
        [InlineKeyboardButton(text="🗑 Удалить категорию", callback_data="category_delete")]
    ])


async def categories_keyboard(action):
    from service import get_category

    categories = await get_category()
    buttons = []

    for category in categories:
        buttons.append([
            InlineKeyboardButton(
                text=category["cotegory_name"],
                callback_data=f"{action}:{category['cotegory_id']}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="category_menu")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def job_apply_keyboard(job_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📨 Откликнуться",
            callback_data=f"apply:{job_id}"
        )]
    ])

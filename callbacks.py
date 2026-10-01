from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery

from service import (
    get_category,
    delete_category_service,
    add_application,
    get_user
)
from keyboards import category_menu, categories_keyboard

router = Router()


@router.callback_query(F.data == "category_menu")
async def back_category_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "📂 Управление категориями:",
        reply_markup=category_menu()
    )


@router.callback_query(F.data == "category_show")
async def show_categories(callback: CallbackQuery):
    await callback.answer()

    categories = await get_category()

    if not categories:
        await callback.message.answer("Категорий пока нет.")
        return

    text = "📋 Категории:\n\n"
    for category in categories:
        text += f"• {category['cotegory_name']}\n"

    await callback.message.answer(text)


@router.callback_query(F.data == "category_update")
async def update_categories(callback: CallbackQuery):
    await callback.answer()

    categories = await get_category()
    if not categories:
        await callback.message.answer("Категорий пока нет.")
        return

    await callback.message.answer(
        "Выберите категорию, которую хотите изменить:",
        reply_markup=await categories_keyboard("update_cat")
    )


@router.callback_query(F.data == "category_delete")
async def delete_categories(callback: CallbackQuery):
    await callback.answer()

    categories = await get_category()
    if not categories:
        await callback.message.answer("Категорий пока нет.")
        return

    await callback.message.answer(
        "Выберите категорию для удаления:",
        reply_markup=await categories_keyboard("delete_cat")
    )


@router.callback_query(F.data.startswith("delete_cat:"))
async def delete_category(callback: CallbackQuery):
    await callback.answer()

    category_id = int(callback.data.split(":")[1])
    status = await delete_category_service(category_id)

    if status:
        await callback.message.answer("🗑 Категория удалена.")
    else:
        await callback.message.answer("❌ Категорию удалить не удалось.")


@router.callback_query(F.data.startswith("apply:"))
async def apply_job(callback: CallbackQuery, bot: Bot):
    await callback.answer()

    job_id = int(callback.data.split(":")[1])
    status, job = await add_application(callback.from_user.id, job_id)

    if status == "exists":
        await callback.message.answer("ℹ️ Вы уже откликались на эту вакансию.")
        return

    if status == "own_job":
        await callback.message.answer("ℹ️ Нельзя откликнуться на свою вакансию.")
        return

    if status != "ok":
        await callback.message.answer("❌ Не удалось отправить отклик.")
        return

    await callback.message.answer("✅ Ваш отклик отправлен автору вакансии.")

    applicant = await get_user(callback.from_user.id)

    if job and job["owner_telegram_id"]:
        username = f"@{callback.from_user.username}" if callback.from_user.username else "не указан"

        text = (
            "📨 Новый отклик на вашу вакансию!\n\n"
            f"💼 Вакансия: {job['title']}\n"
            f"👤 Кандидат: {callback.from_user.full_name}\n"
            f"🔗 Username: {username}\n"
            f"🆔 Telegram ID: {callback.from_user.id}"
        )

        try:
            await bot.send_message(
                chat_id=int(job["owner_telegram_id"]),
                text=text
            )
        except Exception as error:
            print(f"Notification error: {error}")

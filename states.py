from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from service import save_category, update_category_service, save_job
from keyboards import categories_keyboard

router = Router()


class CreateCategory(StatesGroup):
    name = State()


class UpdateCategory(StatesGroup):
    name = State()


class CreateJob(StatesGroup):
    title = State()
    description = State()
    salary = State()
    category = State()


@router.callback_query(F.data == "category_add")
async def category_add(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Введите название новой категории:")
    await state.set_state(CreateCategory.name)


@router.message(CreateCategory.name)
async def category_add_name(message: Message, state: FSMContext):
    status = await save_category(message.text.strip())
    await state.clear()

    if status:
        await message.answer("✅ Категория добавлена.")
    else:
        await message.answer("❌ Не удалось добавить категорию.")


@router.callback_query(F.data.startswith("update_cat:"))
async def category_update_choose(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    category_id = int(callback.data.split(":")[1])
    await state.update_data(category_id=category_id)
    await callback.message.answer("Введите новое название категории:")
    await state.set_state(UpdateCategory.name)


@router.message(UpdateCategory.name)
async def category_update_name(message: Message, state: FSMContext):
    data = await state.get_data()
    status = await update_category_service(
        data["category_id"],
        message.text.strip()
    )
    await state.clear()

    if status:
        await message.answer("✅ Категория изменена.")
    else:
        await message.answer("❌ Не удалось изменить категорию.")


@router.message(F.text == "➕ Добавить работу")
async def job_add_start(message: Message, state: FSMContext):
    await message.answer("Введите название работы / вакансии:")
    await state.set_state(CreateJob.title)


@router.message(CreateJob.title)
async def job_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await message.answer("Введите описание вакансии:")
    await state.set_state(CreateJob.description)


@router.message(CreateJob.description)
async def job_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await message.answer("Введите зарплату числом, например: 5000")
    await state.set_state(CreateJob.salary)


@router.message(CreateJob.salary)
async def job_salary(message: Message, state: FSMContext):
    try:
        salary = int(message.text)
        if salary < 0:
            raise Exception()
    except Exception:
        await message.answer("❌ Зарплата должна быть числом. Например: 5000")
        return

    await state.update_data(salary=salary)

    keyboard = await categories_keyboard("job_cat")
    await message.answer(
        "Выберите категорию вакансии кнопкой:",
        reply_markup=keyboard
    )
    await state.set_state(CreateJob.category)


@router.callback_query(CreateJob.category, F.data.startswith("job_cat:"))
async def job_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    category_id = int(callback.data.split(":")[1])
    data = await state.get_data()

    status = await save_job(
        callback.from_user.id,
        callback.from_user.username,
        callback.from_user.full_name,
        data["title"],
        data["description"],
        data["salary"],
        category_id
    )

    await state.clear()
    if status:
        await callback.message.answer("✅ Вакансия успешно опубликована.")
    else:
        await callback.message.answer("❌ Не удалось добавить вакансию.")

import emoji
import io
from datetime import datetime

from aiogram import Router
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode

from sqlalchemy import select, update
from database.models import User, WaterLog, FoodLog, WorkoutLog

from database.crud import (
    get_user_by_telegram_id,
    create_user,
    set_active_user,
    get_active_user,
    add_water_log,
    add_food_log,
    add_workout_log,
    get_user_logs,
    reset_user_logs
)
from database.base import get_db
from services.api import (
    get_calories_workout,
    get_workout_recommendation,
    get_calories
)
from services.calculations import (
    calculate_calories_threshold, 
    calculate_water_norm, 
    calculate_activity_coef 
)
from services.validators import (
    check_str, check_age, check_weight,
    check_height, check_activity, check_calories,
    check_water, check_food_weight, check_workout_time
)
from services.formatters import format_table
from services.plotters import plot_cumulative_progress
from services.translators import translate_text

router = Router()

class Profile(StatesGroup):
    name = State()
    country = State()
    city = State()
    age = State()
    sex = State()
    weight = State()
    height = State()
    activity_level = State()
    calories_goal = State()

class WaterLogging(StatesGroup):
    water_volume = State()

class FoodLogging(StatesGroup):
    food_name = State()
    food_weight = State()

class WorkoutState(StatesGroup):
    workout_name = State()
    workout_time = State()

class WorkoutRecommendations(StatesGroup):
    muscle = State()

def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)

@router.message(Command('profiles_list'))
async def profiles_list(message: Message):
    async with get_db() as session:
        user = await get_user_by_telegram_id(session, message.from_user.id)
        if not user:
            await message.reply("У вас нет созданных профилей")
            return

        users = await session.execute(
            select(User)
            .where(User.telegram_id == message.from_user.id)
            .order_by(User.is_active.desc(), User.created_at.desc())
        )
        users = users.scalars().all()

        response = "Ваши профили:\n"
        for idx, profile in enumerate(users, 1):
            active_mark = "✅" if profile.is_active else ""
            response += (
                f"{idx}. {profile.name} (Возраст: {profile.age}, Пол: {profile.sex}) "
                f"{active_mark}\n"
            )

        await message.reply(response)

@router.message(Command('set_active_profile'))
async def set_active_profile(message: Message):
    try:
        profile_num = int(message.text.split()[-1])
    except (IndexError, ValueError):
        await message.reply("Используйте: /set_active_profile <номер профиля>")
        return

    async with get_db() as session:
        user = await get_user_by_telegram_id(session, message.from_user.id)
        if not user:
            await message.reply("У вас нет созданных профилей")
            return

        profiles = await session.execute(
            select(User)
            .where(User.telegram_id == message.from_user.id)
            .order_by(User.created_at.desc())
        )
        profiles = profiles.scalars().all()

        if 1 <= profile_num <= len(profiles):
            profile = profiles[profile_num - 1]
            await set_active_user(session, profile.telegram_id)
            await message.reply(f"Профиль '{profile.name}' активирован")
        else:
            await message.reply("Неверный номер профиля")

@router.message(Command('cancel'))
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.reply("Ввод данных отменен.")

@router.message(Command('set_profile'))
async def set_profile(message: Message, state: FSMContext):
    await message.reply("Как вас зовут?")
    await state.set_state(Profile.name)

@router.message(Profile.name)
async def process_name(message: Message, state: FSMContext):
    if not check_str(message):
        await message.reply("Пожалуйста, введите корректное имя")
        return

    await state.update_data(name=message.text)
    await message.reply("Пожалуйста, укажите страну проживания.")
    await state.set_state(Profile.country)

@router.message(Profile.country)
async def process_country(message: Message, state: FSMContext):
    if not check_str(message):
        await message.reply("Пожалуйста, введите корректное название страны")
        return

    await state.update_data(country=message.text)
    await message.reply("Из какого вы города?")
    await state.set_state(Profile.city)

@router.message(Profile.city)
async def process_city(message: Message, state: FSMContext):
    if not check_str(message):
        await message.reply("Пожалуйста, введите корректное название города")
        return

    await state.update_data(city=message.text)
    await message.reply("Введите ваш возраст:")
    await state.set_state(Profile.age)

@router.message(Profile.age)
async def process_age(message: Message, state: FSMContext):
    if not check_age(message):
        await message.reply("Пожалуйста, введите корректный возраст (1-120)")
        return

    await state.update_data(age=float(message.text))
    await message.answer(
        text="Выберите пол:",
        reply_markup=make_row_keyboard(['Мужской', 'Женский'])
    )
    await state.set_state(Profile.sex)

@router.message(Profile.sex)
async def process_sex(message: Message, state: FSMContext):
    if message.text not in ['Мужской', 'Женский']:
        await message.reply("Пожалуйста, выберите пол из предложенных вариантов")
        return

    await state.update_data(sex=message.text)
    await message.reply("Введите ваш вес в кг:")
    await state.set_state(Profile.weight)

@router.message(Profile.weight)
async def process_weight(message: Message, state: FSMContext):
    if not check_weight(message):
        await message.reply("Пожалуйста, введите корректный вес (1-645 кг)")
        return

    await state.update_data(weight=float(message.text))
    await message.reply("Введите ваш рост в см:")
    await state.set_state(Profile.height)

@router.message(Profile.height)
async def process_height(message: Message, state: FSMContext):
    if not check_height(message):
        await message.reply("Пожалуйста, введите корректный рост (100-350 см)")
        return

    await state.update_data(height=float(message.text))
    await message.reply("Введите уровень физической активности (минут в день):")
    await state.set_state(Profile.activity_level)

@router.message(Profile.activity_level)
async def process_activity_level(message: Message, state: FSMContext):
    if not check_activity(message):
        await message.reply("Пожалуйста, введите корректное значение (0-1440 минут)")
        return

    await state.update_data(activity_level=float(message.text))
    await message.reply("Введите ваш дневной лимит калорий:")
    await state.set_state(Profile.calories_goal)

@router.message(Profile.calories_goal)
async def process_calories_goal(message: Message, state: FSMContext):
    if not check_calories(message):
        await message.reply("Пожалуйста, введите корректное значение (500-15000 ккал)")
        return

    data = await state.get_data()
    await state.update_data(calories_goal=float(message.text))
    data = await state.get_data()

    # Рассчитываем нормы
    normal_calories = calculate_calories_threshold(
        data['age'], data['sex'], data['weight'], data['height'], data['activity_level']
    )
    normal_water = await calculate_water_norm(
        data['weight'], data['activity_level'], data['city']
    )

    user_data = {
        "telegram_id": message.from_user.id,
        "name": data['name'],
        "country": data['country'],
        "city": data['city'],
        "age": int(data['age']),
        "sex": data['sex'],
        "weight": data['weight'],
        "height": data['height'],
        "activity_level": data['activity_level'],
        "calories_goal": data['calories_goal'],
        "normal_calories": normal_calories,
        "normal_water": normal_water,
        "is_active": True
    }

    async with get_db() as session:
        # Проверяем, существует ли уже пользователь с таким telegram_id
        existing_user = await get_user_by_telegram_id(session, message.from_user.id)

        if existing_user:
            # Обновляем существующего пользователя
            await session.execute(
                update(User)
                .where(User.telegram_id == message.from_user.id)
                .values(**user_data)
            )
            await session.commit()
            await message.reply(f"Профиль успешно обновлен {emoji.emojize(':heavy_check_mark:', language='alias')}")
        else:
            # Создаем нового пользователя, если он не существует
            # Деактивируем все профили пользователя
            await session.execute(
                update(User)
                .where(User.telegram_id == message.from_user.id)
                .values(is_active=False)
            )
            await create_user(session, user_data)
            await message.reply(f"Профиль успешно создан {emoji.emojize(':heavy_check_mark:', language='alias')}")

    await message.reply(f"Профиль успешно создан {emoji.emojize(':heavy_check_mark:', language='alias')}")
    await state.clear()

@router.message(Command('log_water'))
async def log_water(message: Message, state: FSMContext):
    async with get_db() as session:
        user = await get_active_user(session)
        if not user:
            await message.reply("Сначала создайте или активируйте профиль")
            return

    await message.reply(f"Сколько воды вы выпили в мл? {emoji.emojize(':droplet:', language='alias')}")
    await state.set_state(WaterLogging.water_volume)

@router.message(WaterLogging.water_volume)
async def process_water(message: Message, state: FSMContext):
    if not check_water(message):
        await message.reply("Пожалуйста, введите корректное значение (1-10000 мл)")
        return

    volume = float(message.text)

    async with get_db() as session:
        user = await get_active_user(session)
        if not user:
            await message.reply("Профиль не найден")
            await state.clear()
            return

        await add_water_log(session, user.id, volume)

        # Получаем общее количество воды
        water_logs = await session.execute(
            select(WaterLog.volume)
            .where(WaterLog.user_id == user.id)
        )
        total_water = sum(log for log in water_logs.scalars().all())

        response = (
            f"Добавлено: {volume} мл воды\n"
            f"Общий прогресс: {total_water} / {user.normal_water} мл "
            f"{emoji.emojize(':droplet:', language='alias')}"
        )
        await message.reply(response)

    await state.clear()

@router.message(Command('log_food'))
async def log_food(message: Message, state: FSMContext):
    async with get_db() as session:
        user = await get_active_user(session)
        if not user:
            await message.reply("Сначала создайте или активируйте профиль")
            return

    await message.reply(f"Что вы съели? {emoji.emojize(':green_apple:', language='alias')}")
    await state.set_state(FoodLogging.food_name)

@router.message(FoodLogging.food_name)
async def process_food_name(message: Message, state: FSMContext):
    food_name = message.text
    food_name_eng = translate_text(food_name, language='en')
    calories_per_100g = await get_calories(food_name_eng)

    if not calories_per_100g:
        await message.reply(
            "Не удалось найти информацию о продукте."
        )
        await state.clear()
        return

    await state.update_data(food_name=food_name, calories=calories_per_100g)
    await message.reply("Укажите вес съеденного продукта в граммах:")
    await state.set_state(FoodLogging.food_weight)

@router.message(FoodLogging.food_weight)
async def process_food_weight(message: Message, state: FSMContext):
    if not check_food_weight(message.text):
        await message.reply("Пожалуйста, введите корректный вес (например: 150 или 150.5)")
        return

    weight = float(message.text.replace(',', '.'))
    data = await state.get_data()

    # Рассчитываем калории
    calories = (data['calories'] * weight) / 100
    food_data = {
        "food_name": data['food_name'],
        "food_weight": weight,
        "calories": calories
    }

    async with get_db() as session:
        user = await get_active_user(session)
        if not user:
            await message.reply("Профиль не найден")
            await state.clear()
            return

        await add_food_log(session, user.id, food_data)

        # Получаем общее количество калорий
        food_logs = await session.execute(
            select(FoodLog.calories)
            .where(FoodLog.user_id == user.id)
        )
        total_calories = sum(log for log in food_logs.scalars().all())

        response = (
            f"Добавлено: {data['food_name']} - {weight}г ({calories:.1f} ккал)\n"
            f"Общий прогресс: {total_calories:.1f} / {user.calories_goal} ккал "
            f"{emoji.emojize(':bar_chart:', language='alias')}"
        )
        await message.reply(response)

    await state.clear()

@router.message(Command('log_workout'))
async def log_workout(message: Message, state: FSMContext):
    async with get_db() as session:
        user = await get_active_user(session)
        if not user:
            await message.reply("Сначала создайте или активируйте профиль")
            return

    await message.reply("Каким видом активности вы занимались?")
    await state.set_state(WorkoutState.workout_name)

@router.message(WorkoutState.workout_name)
async def process_workout_name(message: Message, state: FSMContext):
    workout_name = message.text
    workout_name_eng = translate_text(workout_name)
    calories_per_hour = await get_calories_workout(workout_name_eng)

    if not calories_per_hour:
        await message.reply(
            "Не удалось найти информацию об активности. "
            "Попробуйте указать название на английском."
        )
        await state.clear()
        return

    await state.update_data(workout_name=workout_name, calories_per_hour=calories_per_hour)
    await message.reply("Сколько минут вы занимались этой активностью?")
    await state.set_state(WorkoutState.workout_time)

@router.message(WorkoutState.workout_time)
async def process_workout_time(message: Message, state: FSMContext):
    if not check_workout_time(message.text):
        await message.reply("Пожалуйста, введите корректное время (например: 30 или 45.5)")
        return

    minutes = float(message.text.replace(',', '.'))
    data = await state.get_data()

    # Рассчитываем сожженные калории
    calories_burnt = (data['calories_per_hour'] * minutes) / 60
    workout_data = {
        "workout_name": data['workout_name'],
        "workout_time": minutes,
        "calories_burnt": calories_burnt
    }

    async with get_db() as session:
        user = await get_active_user(session)
        if not user:
            await message.reply("Профиль не найден")
            await state.clear()
            return

        await add_workout_log(session, user.id, workout_data)

        # Получаем общее количество сожженных калорий
        workout_logs = await session.execute(
            select(WorkoutLog.calories_burnt)
            .where(WorkoutLog.user_id == user.id)
        )
        total_calories_burnt = sum(log for log in workout_logs.scalars().all())

        response = (
            f"Добавлено: {data['workout_name']} - {minutes} мин ({calories_burnt:.1f} ккал)\n"
            f"Всего сожжено: {total_calories_burnt:.1f} ккал "
            f"{emoji.emojize(':fire:', language='alias')}"
        )
        await message.reply(response)

    await state.clear()

@router.message(Command('see_progress'))
async def see_progress(message: Message):
    async with get_db() as session:
        user = await get_active_user(session)
        if not user:
            await message.reply("Сначала создайте или активируйте профиль")
            return

        # Получаем суммы всех логов
        water_logs = await session.execute(
            select(WaterLog.volume)
            .where(WaterLog.user_id == user.id)
        )
        total_water = sum(log for log in water_logs.scalars().all())

        food_logs = await session.execute(
            select(FoodLog.calories)
            .where(FoodLog.user_id == user.id)
        )
        total_calories = sum(log for log in food_logs.scalars().all())

        workout_logs = await session.execute(
            select(WorkoutLog.calories_burnt)
            .where(WorkoutLog.user_id == user.id)
        )
        total_workout = sum(log for log in workout_logs.scalars().all())

        response = (
            f"Текущий прогресс {emoji.emojize(':bar_chart:', language='alias')}:\n"
            f"{emoji.emojize(':cup_with_straw:', language='alias')} Вода: "
            f"{total_water} / {user.normal_water:.0f} мл\n"
            f"{emoji.emojize(':memo:', language='alias')} Калории: "
            f"{total_calories:.1f} / {user.calories_goal:.0f} "
            f"(норма: {user.normal_calories:.0f})\n"
            f"{emoji.emojize(':fire:', language='alias')} Сожжено: "
            f"{total_workout:.1f} ккал\n"
            f"{emoji.emojize(':chart_with_upwards_trend:', language='alias')} "
            f"Цель с учетом тренировок: {user.calories_goal + total_workout:.0f} ккал"
        )
        await message.answer(response)

@router.message(Command('reset_progress'))
async def reset_progress(message: Message):
    async with get_db() as session:
        user = await get_active_user(session)
        if not user:
            await message.reply("Сначала создайте или активируйте профиль")
            return

        await reset_user_logs(session, user.id)
        await message.reply(f'Прогресс был успешно сброшен {emoji.emojize(":scissors:", language="alias")}')

@router.message(Command('see_history_food'))
async def see_history_food(message: Message):
    async with get_db() as session:
        user = await get_active_user(session)
        if not user:
            await message.reply("Сначала создайте или активируйте профиль")
            return

        food_logs = await session.execute(
            select(FoodLog)
            .where(FoodLog.user_id == user.id)
            .order_by(FoodLog.logged_at.desc())
            .limit(30)  # Ограничиваем количество записей
        )
        food_logs = food_logs.scalars().all()

        if not food_logs:
            await message.reply(f'История питания пуста {emoji.emojize(":white_frowning_face:", language="alias")}')
            return

        data = [
            [
                log.logged_at.strftime('%Y-%m-%d %H:%M'),
                log.food_name,
                f"{log.food_weight:.1f}г",
                f"{log.calories:.1f} ккал"
            ]
            for log in food_logs
        ]

        columns = ['Дата', 'Продукт', 'Вес', 'Калории']
        response = format_table(columns, data)
        await message.answer(response, parse_mode=ParseMode.HTML)

@router.message(Command('see_history_water'))
async def see_history_water(message: Message):
    async with get_db() as session:
        user = await get_active_user(session)
        if not user:
            await message.reply("Сначала создайте или активируйте профиль")
            return

        water_logs = await session.execute(
            select(WaterLog)
            .where(WaterLog.user_id == user.id)
            .order_by(WaterLog.logged_at.desc())
            .limit(30)
        )
        water_logs = water_logs.scalars().all()

        if not water_logs:
            await message.reply(f'История воды пуста {emoji.emojize(":white_frowning_face:", language="alias")}')
            return

        data = [
            [
                log.logged_at.strftime('%Y-%m-%d %H:%M'),
                f"{log.volume:.0f} мл"
            ]
            for log in water_logs
        ]

        columns = ['Дата', 'Количество']
        response = format_table(columns, data)
        await message.answer(response, parse_mode=ParseMode.HTML)

@router.message(Command('see_history_workout'))
async def see_history_workout(message: Message):
    async with get_db() as session:
        user = await get_active_user(session)
        if not user:
            await message.reply("Сначала создайте или активируйте профиль")
            return

        workout_logs = await session.execute(
            select(WorkoutLog)
            .where(WorkoutLog.user_id == user.id)
            .order_by(WorkoutLog.logged_at.desc())
            .limit(30)
        )
        workout_logs = workout_logs.scalars().all()

        if not workout_logs:
            await message.reply(f'История тренировок пуста {emoji.emojize(":white_frowning_face:", language="alias")}')
            return

        data = [
            [
                log.logged_at.strftime('%Y-%m-%d %H:%M'),
                log.workout_name,
                f"{log.workout_time:.1f} мин",
                f"{log.calories_burnt:.1f} ккал"
            ]
            for log in workout_logs
        ]

        columns = ['Дата', 'Тренировка', 'Время', 'Сожжено']
        response = format_table(columns, data)
        await message.answer(response, parse_mode=ParseMode.HTML)

@router.message(Command('progress_graph'))
async def progress_graph(message: Message):
    async with get_db() as session:
        user = await get_active_user(session)
        if not user:
            await message.reply("Сначала создайте или активируйте профиль")
            return

        # Получаем историю калорий
        food_logs = await session.execute(
            select(FoodLog.calories, FoodLog.logged_at)
            .where(FoodLog.user_id == user.id)
            .order_by(FoodLog.logged_at)
        )
        calories_history = [log for log in food_logs.scalars().all()]

        # Получаем историю воды
        water_logs = await session.execute(
            select(WaterLog.volume, WaterLog.logged_at)
            .where(WaterLog.user_id == user.id)
            .order_by(WaterLog.logged_at)
        )
        water_history = [log for log in water_logs.scalars().all()]

        if not calories_history and not water_history:
            await message.reply("Недостаточно данных для построения графика")
            return

        # Строим график
        fig = plot_cumulative_progress(
            calories=calories_history,
            water=water_history,
            calorie_limit=user.normal_calories,
            calorie_goal=user.calories_goal,
            water_limit=user.normal_water
        )

        # Сохраняем график в буфер
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)

        await message.answer("Ваш график прогресса:")
        await message.answer_photo(BufferedInputFile(buf.read(), filename="progress_graph.png"))

@router.message(Command('get_workout_recommendation'))
async def get_workout_muscle(message: Message, state: FSMContext):
    await message.reply("Какие мышцы вы хотите тренировать?")
    await state.set_state(WorkoutRecommendations.muscle)

@router.message(WorkoutRecommendations.muscle)
async def process_muscle(message: Message, state: FSMContext):
    muscle = message.text
    muscle_eng = translate_text(muscle)

    try:
        name, equipment, instructions = await get_workout_recommendation(muscle_eng)
        if not all([name, equipment, instructions]):
            raise ValueError("Не удалось получить данные о тренировке")
    except Exception as e:
        await message.reply("Что-то пошло не так. Попробуйте указать группу мышц по-другому.")
        await state.clear()
        return

    response = (
        f"Рекомендуемая тренировка по мышцам '{muscle}':\n"
        f"- {emoji.emojize(':point_right:', language='alias')} Название: {translate_text(name, language='ru')}\n"
        f"- {emoji.emojize(':point_right:', language='alias')} Оборудование: {translate_text(equipment, language='ru')}\n"
        f"- {emoji.emojize(':point_right:', language='alias')} Инструкции:\n"
        f"  {translate_text(instructions, language='ru')}"
    )

    await message.answer(response)
    await state.clear()
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User, WaterLog, FoodLog, WorkoutLog

async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int):
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalars().first()

async def create_user(session: AsyncSession, user_data: dict):
    user = User(**user_data)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def update_user(session: AsyncSession, telegram_id: int, update_data: dict):
    await session.execute(
        update(User)
        .where(User.telegram_id == telegram_id)
        .values(**update_data)
    )
    await session.commit()

async def set_active_user(session: AsyncSession, telegram_id: int):
    # Сначала сбросим активный статус у всех пользователей
    await session.execute(
        update(User)
        .values(is_active=False)
    )
    # Затем установим активного пользователя
    await session.execute(
        update(User)
        .where(User.telegram_id == telegram_id)
        .values(is_active=True)
    )
    await session.commit()

async def get_active_user(session: AsyncSession):
    result = await session.execute(select(User).where(User.is_active == True))
    return result.scalars().first()

async def add_water_log(session: AsyncSession, user_id: int, volume: float):
    log = WaterLog(user_id=user_id, volume=volume)
    session.add(log)
    await session.commit()
    return log

async def add_food_log(session: AsyncSession, user_id: int, food_data: dict):
    log = FoodLog(user_id=user_id, **food_data)
    session.add(log)
    await session.commit()
    return log

async def add_workout_log(session: AsyncSession, user_id: int, workout_data: dict):
    log = WorkoutLog(user_id=user_id, **workout_data)
    session.add(log)
    await session.commit()
    return log

async def get_user_logs(session: AsyncSession, user_id: int):
    water_logs = await session.execute(select(WaterLog).where(WaterLog.user_id == user_id))
    food_logs = await session.execute(select(FoodLog).where(FoodLog.user_id == user_id))
    workout_logs = await session.execute(select(WorkoutLog).where(WorkoutLog.user_id == user_id))
    
    return {
        "water": water_logs.scalars().all(),
        "food": food_logs.scalars().all(),
        "workout": workout_logs.scalars().all()
    }

async def reset_user_logs(session: AsyncSession, user_id: int):
    await session.execute(WaterLog.__table__.delete().where(WaterLog.user_id == user_id))
    await session.execute(FoodLog.__table__.delete().where(FoodLog.user_id == user_id))
    await session.execute(WorkoutLog.__table__.delete().where(WorkoutLog.user_id == user_id))
    await session.commit()
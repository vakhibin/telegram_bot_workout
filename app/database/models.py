from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from datetime import datetime
from .base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    name = Column(String)
    country = Column(String)
    city = Column(String)
    age = Column(Integer)
    sex = Column(String)
    weight = Column(Float)
    height = Column(Float)
    activity_level = Column(Float)
    calories_goal = Column(Float)
    normal_calories = Column(Float)
    normal_water = Column(Float)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class WaterLog(Base):
    __tablename__ = "water_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    volume = Column(Float)
    logged_at = Column(DateTime, default=datetime.utcnow)

class FoodLog(Base):
    __tablename__ = "food_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    food_name = Column(String)
    food_weight = Column(Float)
    calories = Column(Float)
    logged_at = Column(DateTime, default=datetime.utcnow)

class WorkoutLog(Base):
    __tablename__ = "workout_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    workout_name = Column(String)
    workout_time = Column(Float)
    calories_burnt = Column(Float)
    logged_at = Column(DateTime, default=datetime.utcnow)
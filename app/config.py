from dotenv import load_dotenv
import os

load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
API_WEATHER_TOKEN = os.getenv('API_WEATHER_TOKEN')
API_TOKEN_FOOD = os.getenv("API_TOKEN_FOOD")
API_KEY_WORKOUT = os.getenv("API_KEY_WORKOUT")

# Database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "health_bot")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
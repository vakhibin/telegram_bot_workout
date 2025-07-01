# Health Bot
## Описание
Бот для отслеживания здоровья, подсчета калорий и тренировок.

## Установка
1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/health-bot.git
cd health-bot
```

Создайте файл .env и заполните его:
```
BOT_TOKEN=your_bot_token
API_WEATHER_TOKEN=your_weather_api_token
API_TOKEN_FOOD=your_food_api_token
API_KEY_WORKOUT=your_workout_api_token
```

Запустите через Docker:
```bash
docker-compose up --build# telegram_bot_workout
```
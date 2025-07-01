from config import API_WEATHER_TOKEN, API_TOKEN_FOOD, API_KEY_WORKOUT
from services.api import API_request_weather, get_calories


def calculate_activity_coef(activity):
    """
    Функция, которая расчитывает коэффициент нагрузки
    1,2 – минимальный (сидячая работа, отсутствие физических нагрузок);
    1,375 – низкий (тренировки не менее 20 мин 1-3 раза в неделю);
    1,55 – умеренный (тренировки 30-60 мин 3-4 раза в неделю);
    1,7 – высокий (тренировки 30-60 мин 5-7 раза в неделю; тяжелая физическая работа);
    1,9 – экстремальный (несколько интенсивных тренировок в день 6-7 раз в неделю; очень трудоемкая работа).
    """
    if activity <= 10:
        return 1
    elif activity <= 30:
        return 1.2
    elif activity <= 60:
        return 1.375
    elif activity <= 120:
        return 1.55
    elif activity <= 180:
        return 1.7
    else:
        return 1.9

# Функция, которая расчитывает калорийность по формуле Харрисона-Бенедикта
def calculate_calories_threshold(age, sex, weight, height, activity_level):
    if sex.lower()[0] == 'м':
        normal_calories = 66.5 + (13.75 * weight) + (5.003 * height) - (6.775 * age)
    else:
        normal_calories = 655.1 + (9.563 * weight) + (1.85 * height) - (4.676 * age)

    normal_calories *= calculate_activity_coef(activity_level)

    return  normal_calories

async def calculate_water_norm(weight, activity_level, city):
    # Расчитываем норму воды без учета погоды
    activity_level_coef = activity_level / 30
    water_norm = weight*30 + activity_level_coef*500
    # Пытаемся получить температуру и понять и учесть её
    temperature = await API_request_weather(API_WEATHER_TOKEN, city)

    if not temperature:
        return water_norm
    if (25 <= temperature <= 30):
        water_norm += 500
    elif (temperature > 30):
        water_norm += 1000

    return  water_norm

async def calculate_calories(query):
    calories = await get_calories(query, API_key=API_TOKEN_FOOD)
    return  calories
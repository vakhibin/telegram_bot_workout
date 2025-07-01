# Функция для валидации строковых типов
def check_str(string_element):
    return (string_element.text.isalpha())

# Функция для валидация возраста
def check_age(age):
    return (age.text.isdigit() and (0 < int(age.text) <= 120))

# Функция для валидации веса
def check_weight(weight):
    return (weight.text.isdigit() and (0 < float(weight.text) <= 645))

# Функция для валидации роста см
def check_height(height):
    return (height.text.isdigit() and (100 <= float(height.text) <= 350))

# Функция для валидации активности
def check_activity(activity):
    return (activity.text.isdigit() and (0 <= float(activity.text) <= 1440))

# Функция для валидации калорий
def check_calories(calories):
    return (calories.text.isdigit() and (500 < float(calories.text) <= 15000))

def check_water(water):
    return (water.text.isdigit()) and (0 < float(water.text) < 10000)

def check_food_weight(weight):
    weight = weight.replace(',', '.')
    return weight.isdigit()

def check_workout_time(time):
    time = time.replace(',', '.')
    return time.isdigit() and (float(time))
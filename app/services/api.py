import aiohttp
from config import API_WEATHER_TOKEN, API_TOKEN_FOOD, API_KEY_WORKOUT

# Функция для отправки API по погоде
async def get_coordinates(city_name, token=API_WEATHER_TOKEN):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit={1}&appid={token}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response_data = await response.json()
    except Exception:
        return None
    else:
        return response_data

async def get_current_weather(lat, lon, token=API_WEATHER_TOKEN, units='metric'):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={token}&units={units}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response_data = await response.json()
    except Exception:
        return None
    else:
        return response_data

# Функция для отправки асинхронных API-запросов
async def API_request_weather(API_key, city_name):
  # Получаем информацию о координатах
  response = await get_coordinates(city_name, token=API_key)

  if response is None:
      return False

  try:
    name, lat, lon = response[0]['name'], response[0]['lat'], response[0]['lon']
  except:
      return False

  # Получаем информацию о погоде
  response = await get_current_weather(lat, lon, API_key)

  if response is None:
      return False

  temperature = response['main']['temp']

  return temperature

# Функция для отправки API по калории
async def get_calories(query, API_key=API_TOKEN_FOOD):
    api_url = 'https://api.calorieninjas.com/v1/nutrition?query='

    async with aiohttp.ClientSession() as session:  # Создаем асинхронную сессию
        async with session.get(api_url + query, headers={'X-Api-Key': API_key}) as response:
            if response.status == 200:
                response_json = await response.json()
            else:
                return None
    try:
        return response_json['items'][0]['calories']
    except:
        return None


async def get_calories_workout(activity, API_token=API_KEY_WORKOUT):
    api_url = 'https://api.api-ninjas.com/v1/caloriesburned?activity={}'.format(activity)

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url, headers={'X-Api-Key': API_token}) as response:
            if response.status == 200:
                response = await response.json()
                try:
                    return response[0]['calories_per_hour']
                except:
                    return None
            else:
                print("Error:", response.status, await response.text())
                return None

async def get_workout_recommendation(query, API_token=API_KEY_WORKOUT):
    api_url = 'https://api.api-ninjas.com/v1/exercises?muscle={}'.format(query)

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url, headers={'X-Api-Key': API_token}) as response:
            if response.status == 200:
                response = await response.json()
                try:
                    name, equipment, instructions = response[0]['name'], response[0]['equipment'], response[0]['instructions']
                    return name, equipment, instructions
                except:
                    return None
            else:
                print("Error:", response.status, await response.text())
                return None
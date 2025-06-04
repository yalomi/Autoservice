import requests
import os
from django.conf import settings

# Получить прогноз погоды по городу

def get_weather(city):
    api_key = getattr(settings, 'WEATHER_API_KEY', '')
    if not api_key:
        return {'error': 'API key not configured'}
        
    url = f'https://api.weatherapi.com/v1/current.json'
    params = {
        'key': api_key,
        'q': city,
        'lang': 'ru',
        'aqi': 'no'
    }
    
    try:
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()
        
        if resp.status_code == 200:
            current = data['current']
            location = data['location']
            return {
                'city': location['name'],
                'temp': round(current['temp_c']),
                'desc': current['condition']['text'],
                'icon': current['condition']['icon'].split('/')[-1].split('.')[0],
                'humidity': current['humidity'],
                'wind_speed': current['wind_kph']
            }
        else:
            return {'error': f'Ошибка получения погоды: {data.get("error", {}).get("message", "Неизвестная ошибка")}'}
    except Exception as e:
        return {'error': str(e)}

# Получить курсы валют (exchangerate.host)
def get_currency_rates(base='USD', symbols='EUR,RUB,PLN'):
    url = f'https://api.frankfurter.app/latest?from={base}&to={symbols}'
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if 'rates' in data:
            return data['rates']
        else:
            return {'error': 'Ошибка получения курсов валют'}
    except Exception as e:
        return {'error': str(e)} 
import strawberry
from datetime import datetime
from typing import List

# Current weather data only for forecast API
@strawberry.type
class Current:
    last_updated: str
    temp_f: float
    feelslike_f: float
    humidity: float

# Weekly forecast data
@strawberry.type
class WeeklyForecast:
    date_datetime: datetime
    date: str
    dayofweek: str
    avg_temp: float
    min_temp: float
    max_temp: float
    avg_humidity: float
    current : Current
    hourly_forecast: List['DailyForecast']
    
# Daily forecast data
@strawberry.type
class DailyForecast:
    current_hour: str
    temp_f: float
    feelslike_f: float
    humidity: float
    
# Define a data class to represent a favorite location
@strawberry.type
class FavoriteLocation:
    city: str
   
@strawberry.type
class FavoriteLocationWeather:
    city: str
    weather: List[WeeklyForecast]

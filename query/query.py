import strawberry
from datetime import datetime
from typing import List
from sample.core import FORECAST_WEATHER_API_URL, WEATHER_API_KEY, FUTURE_WEATHER_API_URL, CURRENT_WEATHER_API_URL
from schema.schema import Current, WeeklyForecast, DailyForecast, FavoriteLocation, FavoriteLocationWeather
import requests


# Define a query for retrieving weather forecast data based on a city and date input
@strawberry.type
class Query:
    @strawberry.field
    def fetch_by_city(
        self,
        city : str,
    ) -> List[WeeklyForecast]:

        # Build the request URL with the city and date parameters
        url = f"{FORECAST_WEATHER_API_URL}?key={WEATHER_API_KEY}&q={city}&days=10&aqi=no&alerts=no"

        # Make the API request and parse the response JSON
        response = requests.get(url)
        response_json = response.json()
        
        # Extract the current weather data from the response JSON
        current_forecast = Current(
            temp_f=response_json["current"]["temp_f"], 
            humidity=response_json["current"]["humidity"],
            feelslike_f=response_json["current"]["feelslike_f"],
            last_updated=response_json["current"]["last_updated"]
        )
        
        # Extract the forecast data from the response JSON
        forecast_data = response_json["forecast"]["forecastday"]
        
        # Map the forecast data to a list of WeatherForecast objects
        weather_forecast = [
            WeeklyForecast(
                date=forecast["date"],
                date_datetime=datetime.strptime(forecast["date"], '%Y-%m-%d'),
                dayofweek=datetime.strptime(forecast["date"], '%Y-%m-%d').strftime('%A'),
                avg_temp=forecast["day"]["avgtemp_f"],
                min_temp=forecast["day"]["mintemp_f"],
                max_temp=forecast["day"]["maxtemp_f"],
                avg_humidity=forecast["day"]["avghumidity"],      
                current=current_forecast,
                
                hourly_forecast= [
                    DailyForecast(
                        current_hour=forecast["hour"][hr]["time"],
                        temp_f=forecast["hour"][hr]["temp_f"],
                        humidity=forecast["hour"][hr]["humidity"],
                        feelslike_f=forecast["hour"][hr]["feelslike_f"]
                        
                    )   
                    for hr in range(0, 24)
                ]
                
            )
            
            for forecast in forecast_data
        ]

        
        # Return the weather forecast data
        return weather_forecast

    @strawberry.field
    def fetch_by_city_date(
        self,
        date: str,
        city : str,
    ) -> List[WeeklyForecast]:
        
        url = f"{FUTURE_WEATHER_API_URL}?key={WEATHER_API_KEY}&q={city}&dt={date}"
                
        # Build the request URL with the city and date parameters
        response = requests.get(url)
        response_json = response.json()
        
        #no current forecast for future dates
        current_forecast=Current(
            temp_f=0,
            humidity=0,
            feelslike_f=0,
            last_updated="no current forecast for future dates"
        )       
            
        # Extract the forecast data from the response JSON
        forecast_data = response_json["forecast"]["forecastday"]
        
        # Map the forecast data to a list of WeatherForecast objects
        future_weather = [
            WeeklyForecast(
                date=forecast["date"],
                date_datetime=datetime.strptime(forecast["date"], '%Y-%m-%d'),
                dayofweek=datetime.strptime(forecast["date"], '%Y-%m-%d').strftime('%A'),
                avg_temp=forecast["day"]["avgtemp_f"],
                min_temp=forecast["day"]["mintemp_f"],
                max_temp=forecast["day"]["maxtemp_f"],
                avg_humidity=forecast["day"]["avghumidity"],
                #no current forecast for future dates
                current=current_forecast,
                hourly_forecast= [  
                    DailyForecast(
                        current_hour=forecast["hour"][hr]["time"],
                        temp_f=forecast["hour"][hr]["temp_f"],
                        humidity=forecast["hour"][hr]["humidity"],
                        feelslike_f=forecast["hour"][hr]["feelslike_f"]
                    )   
                        for hr in range(0, 8)
                ]   
                
            )
                for forecast in forecast_data
        ]
        
        # Return the weather forecast data
        return future_weather

    @strawberry.field
    def fetch_by_fav_city(
        self,
        city : str,
    ) -> FavoriteLocationWeather:
        favorite_location_weather = FavoriteLocationWeather(
            city=city,
            weather=self.fetch_by_city(city)
        )
        return favorite_location_weather
    
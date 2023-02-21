import requests
from datetime import datetime
from typing import List
import strawberry
from fastapi import FastAPI
from typing import Optional


app = FastAPI()

# Define the API endpoint for the weatherapi Forecast API
WEATHER_API_URL = "https://api.weatherapi.com/v1/forecast.json"
WEATHER_API_KEY = '6020e8083693420ca19234830231902'
today = datetime.today().strftime('%Y-%m-%d')

@strawberry.type
class WeeklyForecast:
    date: datetime
    dayofweek: str
    avg_temp: float
    min_temp: float
    max_temp: float
    avg_humidity: float
    hourly_forecast: List['HourlyForecast']
    
# Define a data class to represent the hourly weather forecast data
@strawberry.type
class HourlyForecast:
    current_hour: str
    temp_f: float
    humidity: float
    
# Define a data class to represent a favorite location
@strawberry.type
class FavoriteLocation:
    city: str
    date: datetime
    
# Define a mutation for saving a favorite location
@strawberry.type
class Mutation:
    @strawberry.mutation
    def save_favorite_location(
        self,
        city: str,
        date: str
    ) -> FavoriteLocation:
        # Convert the date string input to a datetime object
        date_obj = datetime.strptime(date, '%Y-%m-%d')

        # Create a FavoriteLocation object with the input parameters
        favorite_location = FavoriteLocation(city=city, date=date_obj)

        # Return the saved FavoriteLocation object
        return favorite_location

# Define a query for retrieving weather forecast data based on a city and date input
@strawberry.type
class Query:
    @strawberry.field
    def weather_forecast_by_city_and_date(
        self,
        city : str,
        date: str
    ) -> List[WeeklyForecast]:
        # Convert the date string input to a datetime object
        date_obj = datetime.strptime(date, '%Y-%m-%d')

        # Build the request URL with the city and date parameters
        url = f"{WEATHER_API_URL}?key={WEATHER_API_KEY}&q={city}&days=7&aqi=no&alerts=no"

        # Make the API request and parse the response JSON
        response = requests.get(url)
        response_json = response.json()

        # Extract the forecast data from the response JSON
        forecast_data = response_json["forecast"]["forecastday"]
        
        # Map the forecast data to a list of WeatherForecast objects
        weather_forecast = [
            WeeklyForecast(
                date=datetime.strptime(forecast["date"], '%Y-%m-%d'),
                dayofweek=datetime.strptime(forecast["date"], '%Y-%m-%d').strftime('%A'),
                avg_temp=forecast["day"]["avgtemp_f"],
                min_temp=forecast["day"]["mintemp_f"],
                max_temp=forecast["day"]["maxtemp_f"],
                avg_humidity=forecast["day"]["avghumidity"],
                
                
                hourly_forecast= [
                    HourlyForecast(
                        current_hour=forecast["hour"][hr]["time"],
                        temp_f=forecast["hour"][hr]["temp_f"],
                        humidity=forecast["hour"][hr]["humidity"]
                    )   
                    for hr in range(0, 24)
                ]
                
            )
            
            for forecast in forecast_data
        ]

        
        # Return the weather forecast data
        return weather_forecast

    @strawberry.field
    def weather_forecast_by_favorite_location(
        self,
        favorite_location: str
    ) -> List[HourlyForecast]:
        # Convert the date string input to a datetime object
        date_str = today
        
        # Build the request URL with the favorite location parameters
        url = f"{WEATHER_API_URL}?key={WEATHER_API_KEY}&q={favorite_location}&dt={date_str}"

        # Make the API request and parse the response JSON
        response = requests.get(url)
        response_json = response.json()

        # Extract the forecast data from the response JSON
        forecast_data = response_json["forecast"]["forecastday"][0]["hour"]
        
        # Map the forecast data to a list of WeatherForecast objects
        weather_forecast = [
            HourlyForecast(
                current_hour=datetime.strptime(forecast["time"], '%Y-%m-%d %H:%M'),
                temp_f=forecast["temp_c"],
                humidity=forecast["humidity"]
            )
            for forecast in forecast_data
        ]
        
        # Return the weather forecast data
        return weather_forecast
            

    
# Define the GraphQL schema with the Query type
schema = strawberry.Schema(query=Query, mutation= Mutation)

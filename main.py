from strawberry.fastapi import GraphQLRouter
from strawberry.schema.config import StrawberryConfig
import requests
from datetime import datetime
from typing import List
import strawberry
from fastapi import FastAPI
from pymongo import MongoClient


# Define the API endpoint for the weatherapi Forecast API

FORECAST_WEATHER_API_URL = "https://api.weatherapi.com/v1/forecast.json"

# Date between 14 days and 300 days from today in the future in yyyy-MM-dd format
FUTURE_WEATHER_API_URL = "https://api.weatherapi.com/v1/future.json"

CURRENT_WEATHER_API_URL = "https://api.weatherapi.com/v1/current.json"

WEATHER_API_KEY = '6020e8083693420ca19234830231902'
today = datetime.today().strftime('%Y-%m-%d')

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
    
# Define a mutation for saving a favorite location
@strawberry.type
class Mutation:
    @strawberry.mutation
    def save_favorite_location(
        self,
        city: str,
    ) -> FavoriteLocation:
        # Convert the date string input to a datetime object
        #date_obj = datetime.strptime(date, '%Y-%m-%d')

        # Create a FavoriteLocation object with the input parameters
        favorite_location = FavoriteLocation(city=city)

        # Return the saved FavoriteLocation object
        return favorite_location

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


    
# Strawberry provides support for FastAPI with a custom APIRouter called GraphQLRouter.
schema = strawberry.Schema(query=Query, mutation=Mutation, config=StrawberryConfig(auto_camel_case=True))


graphql_app = GraphQLRouter(schema)

app = FastAPI()
# app.include_router(graphql_app, prefix="/graphql")
app.add_api_route("/graphql", graphql_app, methods=["GET", "POST"])



# sets up mongo db client using pymongo library and uses local.weather_collection
client = MongoClient('mongodb://localhost:27017/')
db = client.local
collection = db.weather_collection


def parse_city(city: str):
    parse = city.replace("-", " ")
    return parse

@app.get("/weather/{city}")
async def get_weather_by_city(city: str):
    q = Query()
    return q.fetch_by_city(parse_city(city))

@app.get("/weather/{city}/{date}")
async def get_weather_by_city_and_date(city: str, date: str):
    q = Query()
    return q.fetch_by_city_date(date, parse_city(city))


# creates a post route /weather/favorite that takes in a city and saves it to the mongoDB weather_collection
@app.post("/favorite/{city}")
async def save_favorite_location(city: str):
    m = Mutation()
    collection.insert_one({"city": parse_city(city)})
    return m.save_favorite_location(parse_city(city))

# fetch all favorite locations from mongoDB weather_collection and return them as a list
@app.get("/get-favorite-locations")
async def get_favorite_locations():
    cursor = collection.find({})
    query = Query()
    favorite_weather = []
    for document in cursor:
        print(document)
        favorite_weather.append(query.fetch_by_city(document["city"]))
    return favorite_weather
        
        
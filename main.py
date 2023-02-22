from strawberry.fastapi import GraphQLRouter
from strawberry.schema.config import StrawberryConfig
import strawberry
from fastapi import FastAPI
from pymongo import MongoClient
from helper.helper import parse_city
from mutation.mutation import Mutation
from query.query import Query
from datetime import datetime, timedelta
    
# Strawberry provides support for FastAPI with a custom APIRouter called GraphQLRouter.
# Create a GraphQLRouter with the Query and Mutation types
schema = strawberry.Schema(query=Query, mutation=Mutation, config=StrawberryConfig(auto_camel_case=True))
graphql_app = GraphQLRouter(schema)
app = FastAPI()
app.add_api_route("/graphql", graphql_app, methods=["GET", "POST"])

# sets up mongo db client using pymongo library and uses local.weather_collection
client = MongoClient('mongodb://localhost:27017/')
db = client.local
collection = db.weather_collection

# GET WEATHER BY CITY
# creates a get route /weather-city/{city} that takes in a city and returns the weather forecast for that city
@app.get("/weather-city/{city}")
async def get_weather_by_city(city: str):
    q = Query()
    return q.fetch_by_city(parse_city(city))

# GET WEATHER BY CITY AND DATE
# creates a get route /weather-city-and-date/{city}/{date} that takes in a city and date and returns the weather forecast for that city and date
@app.get("/weather-city-and-date/{city}/{date}")
async def get_weather_by_city_and_date(city: str, date: str):
    # if date is not 14 days and 300 days from today in the future in yyyy-MM-dd format, return error message
    if date < (datetime.today() + timedelta(days=14)).strftime('%Y-%m-%d') or date > (datetime.today() + timedelta(days=300)).strftime('%Y-%m-%d'):
        return "Date must be between 14 days and 300 days from today in the future in yyyy-MM-dd format"
    else:
        q = Query()
        return q.fetch_by_city_date(date, parse_city(city))

# SAVE FAVORITE LOCATION
# creates a post route /save-favorite/{city} that takes in a city and saves it to the mongoDB weather_collection
# if the city is already saved, it returns a message saying the city is already saved
@app.post("/save-favorite/{city}")
async def post_fav_location(city: str):        
    m = Mutation()
    cursor = collection.find({})
    for document in cursor:
        if document["city"] == parse_city(city):
            return "City already saved"
    collection.insert_one({"city": parse_city(city)})
    return m.save_favorite_location(parse_city(city))

# GET ALL FAVORITE LOCATIONS
# creates a get route /get-all-favorite-locations that returns all the cities saved in the mongoDB weather_collection
@app.get("/get-all-favorite-locations")
async def get_all_favorite_locations():
    cursor = collection.find({})
    query = Query()
    favorite_weather = []
    for document in cursor:
        favorite_weather.append(query.fetch_by_fav_city(document["city"]))
    return favorite_weather
        
# GET SINGLE FAVORITE LOCATION
# creates a get route /get-favorite-location/{city} that returns the weather forecast for a specified city saved in the mongoDB weather_collection
@app.get("/get-favorite-location/{city}")
async def get_favorite_location(city: str):
    cursor = collection.find({})
    query = Query()
    for document in cursor:
        if document["city"] == parse_city(city):
            return query.fetch_by_fav_city(document["city"])
    return "City not found"

# DELETE FAVORITE LOCATION
# creates a delete route /delete-favorite-location/{city} that deletes a specified city from the mongoDB weather_collection
@app.delete("/delete-favorite-location/{city}")
async def delete_favorite_location(city: str):
    m = Mutation()
    cursor = collection.find({})
    for document in cursor:
        if document["city"] == parse_city(city):
            collection.delete_one({"city": parse_city(city)})
            return "Favorite location deleted"
    return "City not found"


# DELETE ALL FAVORITE LOCATIONS
# creates a delete route /delete-all-favorite-locations/ that deletes all the cities from the mongoDB weather_collection
@app.delete("/delete-all-favorite-locations")
async def delete_favorite_locations():
    m = Mutation()
    if collection.count_documents({}) == 0:
        return "No favorite locations to delete"
    else :
        collection.delete_many({})
        return "All favorite locations deleted"


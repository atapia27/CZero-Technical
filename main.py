from strawberry.fastapi import GraphQLRouter
from strawberry.schema.config import StrawberryConfig
import strawberry
from fastapi import FastAPI
from pymongo import MongoClient
from helper.helper import parse_city
from mutation.mutation import Mutation
from query.query import Query

    
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

# creates a get route /weather/{city} that takes in a city and returns the weather forecast for that city
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

# creates a get route /weather/favorite that returns all the cities saved in the mongoDB weather_collection
@app.get("/get-favorite-locations")
async def get_favorite_locations():
    cursor = collection.find({})
    query = Query()
    favorite_weather = []
    for document in cursor:
        print(document)
        favorite_weather.append(query.fetch_by_city(document["city"]))
    return favorite_weather
        
        
# SETUP
```bash 
pip3 install starlette
pip3 install uvicorn
pip install pydantic
pip install fastapi
pip install uvicorn
pip install "uvicorn[standard]"
pip install "strawberry-graphql[debug-server]"
pip install requests
pip install datetime
```

```bash
python -m strawberry server schema
```
[Server](http://localhost:8000/graphql)

# INFO
```
{
  weatherForecastByCityAndDate(city: "Mexico City", date: "2023-02-25") {
    date
    dayofweek
    avgTemp
    minTemp
    maxTemp
		avgHumidity
    hourlyForecast{
      currentHour
      tempF
      humidity
    }
  }
}
```
>***1 query for weather where you input a city and date, output should be data on temp and humidity by time. Bonus: thoughtful about picking the data type for the output***

```
mutation{
  saveFavoriteLocation(city:"Mexico City", date: "2023-02-21"){
    city
    date
  }
}
```
>***1 mutation for saving your favorite***



```
{
	weatherForecastByFavoriteLocation(favoriteLocation: "Mexico City"){
    time
    tempC
    humidity
  }
}
```
>***1 query for getting weather from your fav locations***

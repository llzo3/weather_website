from fastapi import FastAPI

import requests

app = FastAPI()

# const lat = 37.477550020716194
# const lon = 126.98212524649105

@app.get("/")
def root():
    URL = "https://api.openweathermap.org/data/2.5/onecall?lat=$37.477550020716194&lon=$126.98212524649105&exclude=minutely,hourly&units=metric&appId=2c1d56123e5c377524128dbc99536f60"
    contents = requests.get(URL).text
    
    return { "message": contents }

@app.get("/home")
def home():
    return {"message": "Home!"}
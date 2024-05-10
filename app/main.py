from fastapi import FastAPI

import requests

app = FastAPI()

@app.get("/")
def root():
    URL = "http://api.openweathermap.org/data/2.5/forecast?id=524901&appid={2c1d56123e5c377524128dbc99536f60}"
    contents = requests.get(URL).text
    
    return { "message": contents }

@app.get("/home")
def home():
    return {"message": "Home!"}
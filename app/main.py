from fastapi import FastAPI
import requests


city = "Seoul"
app = FastAPI()

LAT = 37.477550020716194
LON = 126.98212524649105
API_KEY = "7984a6ee79bc96d84c6a09aaf4cdf934"


@app.get("/")
def root():
    URL = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metirc&lang=kr"
    response = requests.get(URL)

    return {"message": response}

@app.get("/home")
def home():
    return {"message": "Home!"}

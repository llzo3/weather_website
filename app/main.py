from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import requests

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")

LAT = 37.477550020716194
LON = 126.98212524649105
API_KEY = "7984a6ee79bc96d84c6a09aaf4cdf934"
CITY = "Seoul"

@app.get("/")
def root(request: Request):
    URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric&lang=kr"
    response = requests.get(URL)

    if response.status_code == 200:
        data = response.json()
        weather_data = {
            "city": data["name"],
            "date": "5월 24일",  # 예시 날짜, 실제로는 현재 날짜를 가져올 수 있음
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "temp_min": data["main"]["temp_min"],
            "temp_max": data["main"]["temp_max"],
            "description": data["weather"][0]["description"]
        }
        return templates.TemplateResponse("index.html", {"request": request, "weather": weather_data})
    else:
        return {"message": "Failed to fetch weather data"}

@app.get("/home")
def home():
    return {"message": "Home!"}

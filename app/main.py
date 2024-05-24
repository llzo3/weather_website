from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests

city = "Seoul"
app = FastAPI()

LAT = 37.477550020716194
LON = 126.98212524649105
API_KEY = "7984a6ee79bc96d84c6a09aaf4cdf934"

templates = Jinja2Templates(directory="templates")

@app.get("/", , response_class=HTMLResponse)
def root(request: Request):
    URL = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=kr"
    response = requests.get(URL)

    if response.status_code == 200:
        data = response.json()
        formatted_data = {
            "location": {
                "city": data["name"],
                "country": data["sys"]["country"],
                "coordinates": {
                    "latitude": data["coord"]["lat"],
                    "longitude": data["coord"]["lon"]
                }
            },
            "weather": {
                "description": data["weather"][0]["description"],
                "temperature": {
                    "current": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "min": data["main"]["temp_min"],
                    "max": data["main"]["temp_max"]
                },
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "visibility": data["visibility"]
            },
            "wind": {
                "speed": data["wind"]["speed"],
                "direction": data["wind"]["deg"]
            },
            "clouds": {
                "coverage": data["clouds"]["all"]
            },
            "sun": {
                "sunrise": data["sys"]["sunrise"],
                "sunset": data["sys"]["sunset"]
            },
            "timezone": data["timezone"],
            "timestamp": data["dt"]
        }
        return templates.TemplateResponse("weather.html", {"request": request, "data": formatted_data})
    else:
        return {"message": "Failed to fetch weather data"}

@app.get("/home")
def home():
    return {"message": "Home!"}
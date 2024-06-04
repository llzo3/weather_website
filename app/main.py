# app/main.py

from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
import requests
import datetime
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from .models import Base, WeatherRecord

Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")

API_KEY = "7984a6ee79bc96d84c6a09aaf4cdf934"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root(request: Request, city: str = "Seoul", db: Session = Depends(get_db)):
    URL = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=kr"
    response = requests.get(URL)

    if response.status_code == 200:
        data = response.json()
        weather_data = {
            "city": data["name"],
            "date": datetime.datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분 %S초"),
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "temp_min": data["main"]["temp_min"],
            "temp_max": data["main"]["temp_max"],
            "description": data["weather"][0]["description"]
        }

        # DB에 기록 저장
        weather_record = WeatherRecord(
            city=weather_data["city"],
            temperature=str(weather_data["temperature"]),
            feels_like=str(weather_data["feels_like"]),
            temp_min=str(weather_data["temp_min"]),
            temp_max=str(weather_data["temp_max"]),
            description=weather_data["description"]
        )
        db.add(weather_record)
        db.commit()

        return templates.TemplateResponse("index.html", {"request": request, "weather": weather_data})
    else:
        return {"message": "Failed to fetch weather data"}

@app.get("/history")
def history(db: Session = Depends(get_db)):
    records = db.query(WeatherRecord).all()
    return {"history": records}

@app.get("/home")
def home():
    return {"message": "Home!"}

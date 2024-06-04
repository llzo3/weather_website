from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import requests
import datetime

from .database import SessionLocal, Weather

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")

API_KEY = "7984a6ee79bc96d84c6a09aaf4cdf934"

# 데이터베이스 세션을 요청마다 생성하고 닫기 위한 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root(request: Request, city: str = "Seoul"):
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

         # 데이터베이스에 날씨 데이터 저장
        weather_entry = Weather(
            city=weather_data["city"],
            date=datetime.datetime.now(),
            temperature=weather_data["temperature"],
            feels_like=weather_data["feels_like"],
            temp_min=weather_data["temp_min"],
            temp_max=weather_data["temp_max"],
            description=weather_data["description"]
        )
        db.add(weather_entry)
        db.commit()
        db.refresh(weather_entry)

        return templates.TemplateResponse("index.html", {"request": request, "weather": weather_data})
    else:
        return {"message": "Failed to fetch weather data"}

# FastAPI 엔드포인트로 데이터 조회
@app.get("/weather")
def read_weather_data(db: Session = Depends(get_db)):
    weather_data = db.query(Weather).all()
    return weather_data

@app.get("/home")
def home():
    return {"message": "Home!"}

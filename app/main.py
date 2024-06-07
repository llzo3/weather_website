from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import requests
import datetime
import os
from dotenv import load_dotenv
import pytz

load_dotenv()  # .env 파일에서 환경 변수 로드

DATABASE_URL = os.getenv("DATABASE_URL")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class WeatherRecord(Base):
    __tablename__ = "weather_records"
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, index=True)
    lat = Column(Float)
    lon = Column(Float)
    date = Column(DateTime)
    temperature = Column(Float)
    feels_like = Column(Float)
    temp_min = Column(Float)
    temp_max = Column(Float)
    description = Column(String)
    humidity = Column(Float)
    wind_speed = Column(Float)
    pressure = Column(Float)
    uv_index = Column(Float)
    sunrise = Column(DateTime)
    sunset = Column(DateTime)

Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root(request: Request, db: Session = Depends(get_db)):
    records = db.query(WeatherRecord).order_by(WeatherRecord.id.desc()).limit(5).all()
    return templates.TemplateResponse("index.html", {"request": request, "records": records})

@app.get("/weather")
def get_weather_by_coords(lat: float, lon: float, db: Session = Depends(get_db)):
    URL = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=kr"
    response = requests.get(URL)

    if response.status_code == 200:
        data = response.json()
        timezone_offset = data["timezone"]

        def to_local_time(utc_time):
            return datetime.datetime.utcfromtimestamp(utc_time + timezone_offset)

        weather_data = {
            "city": data["name"],
            "lat": lat,
            "lon": lon,
            "date": to_local_time(data["dt"]).strftime("%Y년 %m월 %d일 %H시 %M분 %S초"),
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "temp_min": data["main"]["temp_min"],
            "temp_max": data["main"]["temp_max"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "pressure": data["main"]["pressure"],
            "uv_index": data["main"].get("uvi", 0),
            "sunrise": to_local_time(data["sys"]["sunrise"]).strftime("%H:%M:%S"),
            "sunset": to_local_time(data["sys"]["sunset"]).strftime("%H:%M:%S")
        }

        weather_record = WeatherRecord(
            city=weather_data["city"],
            lat=lat,
            lon=lon,
            date=datetime.datetime.utcnow(),
            temperature=weather_data["temperature"],
            feels_like=weather_data["feels_like"],
            temp_min=weather_data["temp_min"],
            temp_max=weather_data["temp_max"],
            description=weather_data["description"],
            humidity=weather_data["humidity"],
            wind_speed=weather_data["wind_speed"],
            pressure=weather_data["pressure"],
            uv_index=weather_data["uv_index"],
            sunrise=datetime.datetime.utcfromtimestamp(data["sys"]["sunrise"] + timezone_offset),
            sunset=datetime.datetime.utcfromtimestamp(data["sys"]["sunset"] + timezone_offset)
        )
        db.add(weather_record)
        db.commit()

        return weather_data
    else:
        return {"message": "Failed to fetch weather data"}

@app.get("/history")
def get_weather_history(request: Request, db: Session = Depends(get_db)):
    records = db.query(WeatherRecord).order_by(WeatherRecord.id.desc()).all()
    return templates.TemplateResponse("history.html", {"request": request, "records": records})

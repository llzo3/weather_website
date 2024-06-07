from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import requests
import datetime
import pytz
import os

# 절대 경로로 데이터베이스 파일 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = os.getenv("DATABASE_URL")

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
    favorite_count = Column(Integer, default=0)

Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")

# static 디렉토리가 존재하지 않으면 생성
static_dir = os.path.join(BASE_DIR, 'static')
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

API_KEY = os.getenv("OPENWEATHER_API_KEY")

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
    URL = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=kr"
    response = requests.get(URL)

    if response.status_code == 200:
        data = response.json()

        timezone_offset = data["timezone"]
        timezone = pytz.timezone(f"Etc/GMT{timezone_offset // 3600:+d}")
        local_time = datetime.datetime.now(timezone).strftime("%Y년 %m월 %d일 %H시 %M분 %S초")

        weather_data = {
            "city": data["name"],
            "lat": lat,
            "lon": lon,
            "date": local_time,
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "temp_min": data["main"]["temp_min"],
            "temp_max": data["main"]["temp_max"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "pressure": data["main"]["pressure"],
            "uv_index": data.get("current", {}).get("uvi", "N/A"),
            "sunrise": datetime.datetime.fromtimestamp(data["sys"]["sunrise"], tz=timezone).strftime("%H:%M:%S"),
            "sunset": datetime.datetime.fromtimestamp(data["sys"]["sunset"], tz=timezone).strftime("%H:%M:%S"),
        }

        weather_record = WeatherRecord(
            city=weather_data["city"],
            lat=lat,
            lon=lon,
            date=datetime.datetime.now(timezone),
            temperature=weather_data["temperature"],
            feels_like=weather_data["feels_like"],
            temp_min=weather_data["temp_min"],
            temp_max=weather_data["temp_max"],
            description=weather_data["description"],
            humidity=weather_data["humidity"],
            wind_speed=weather_data["wind_speed"],
            pressure=weather_data["pressure"],
            uv_index=weather_data["uv_index"],
            sunrise=datetime.datetime.fromtimestamp(data["sys"]["sunrise"], tz=timezone),
            sunset=datetime.datetime.fromtimestamp(data["sys"]["sunset"], tz=timezone)
        )
        
        # Check if the city has been searched more than 5 times
        favorite_count = db.query(func.count(WeatherRecord.id)).filter(WeatherRecord.city == weather_data["city"]).scalar()
        weather_record.favorite_count = favorite_count
        
        db.add(weather_record)
        db.commit()

        return weather_data
    else:
        return {"message": "Failed to fetch weather data"}

@app.get("/history")
def get_history(request: Request, db: Session = Depends(get_db)):
    records = db.query(WeatherRecord).order_by(WeatherRecord.id.desc()).all()
    favorites = db.query(WeatherRecord.city).group_by(WeatherRecord.city).having(func.count(WeatherRecord.city) > 5).all()
    favorite_cities = [f[0] for f in favorites]
    return templates.TemplateResponse("history.html", {"request": request, "records": records, "favorites": favorite_cities})

@app.get("/home")
def home():
    return {"message": "Home!"}

from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import requests
import datetime
import pytz
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./weather.db")
API_KEY = os.getenv("OPENWEATHER_API_KEY", "7984a6ee79bc96d84c6a09aaf4cdf934")

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
    is_favorite = Column(Boolean, default=False)

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
    records = db.query(WeatherRecord).order_by(WeatherRecord.date.desc()).limit(5).all()
    favorites = db.query(WeatherRecord).filter(WeatherRecord.is_favorite == True).all()
    return templates.TemplateResponse("index.html", {"request": request, "records": records, "favorites": favorites})

@app.get("/weather")
def get_weather_by_coords(lat: float, lon: float, db: Session = Depends(get_db)):
    URL = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=kr"
    response = requests.get(URL)

    if response.status_code == 200:
        data = response.json()
        timezone_offset = data["timezone"]

        local_time = datetime.datetime.utcfromtimestamp(data["dt"] + timezone_offset).strftime("%Y년 %m월 %d일 %H시 %M분 %S초")
        korea_time = datetime.datetime.now(pytz.timezone("Asia/Seoul")).strftime("%Y년 %m월 %d일 %H시 %M분 %S초")

        sunrise_time = datetime.datetime.utcfromtimestamp(data["sys"]["sunrise"] + timezone_offset).strftime("%H:%M:%S")
        sunset_time = datetime.datetime.utcfromtimestamp(data["sys"]["sunset"] + timezone_offset).strftime("%H:%M:%S")

        # 한국 시간대 오프셋 (Asia/Seoul)
        korea_offset = 9 * 3600  # 9시간을 초 단위로 변환

        # 시차 계산
        timezone_diff = (timezone_offset - korea_offset) // 3600

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
            "uv_index": data.get("uvi", "N/A"),
            "sunrise": sunrise_time,
            "sunset": sunset_time,
            "korea_time": korea_time,
            "timezone_diff": timezone_diff
        }

        # 기존에 같은 위치 기록이 있으면 업데이트, 없으면 추가
        record = db.query(WeatherRecord).filter(WeatherRecord.lat == lat, WeatherRecord.lon == lon).first()
        if record:
            record.city = weather_data["city"]
            record.date = datetime.datetime.now(pytz.utc)
            record.temperature = weather_data["temperature"]
            record.feels_like = weather_data["feels_like"]
            record.temp_min = weather_data["temp_min"]
            record.temp_max = weather_data["temp_max"]
            record.description = weather_data["description"]
        else:
            weather_record = WeatherRecord(
                city=weather_data["city"],
                lat=lat,
                lon=lon,
                date=datetime.datetime.now(pytz.utc),
                temperature=weather_data["temperature"],
                feels_like=weather_data["feels_like"],
                temp_min=weather_data["temp_min"],
                temp_max=weather_data["temp_max"],
                description=weather_data["description"]
            )
            db.add(weather_record)
        db.commit()

        return weather_data
    else:
        return {"message": "Failed to fetch weather data"}

@app.post("/favorites")
def add_to_favorites(lat: float, lon: float, db: Session = Depends(get_db)):
    record = db.query(WeatherRecord).filter(WeatherRecord.lat == lat, WeatherRecord.lon == lon).first()
    if record:
        record.is_favorite = True
        db.commit()
        return {"message": "Added to favorites"}
    return {"message": "Record not found"}

@app.get("/favorites")
def get_favorites(request: Request, db: Session = Depends(get_db)):
    favorites = db.query(WeatherRecord).filter(WeatherRecord.is_favorite == True).all()
    return templates.TemplateResponse("favorites.html", {"request": request, "favorites": favorites})

@app.get("/history")
def history(request: Request, db: Session = Depends(get_db)):
    records = db.query(WeatherRecord).order_by(WeatherRecord.id.desc()).all()
    return templates.TemplateResponse("history.html", {"request": request, "records": records})

def get_timezone_from_offset(offset):
    if offset == 0:
        return 'Etc/GMT'
    elif offset > 0:
        return f'Etc/GMT+{abs(offset // 3600)}'
    else:
        return f'Etc/GMT-{abs(offset // 3600)}'
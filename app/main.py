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

def translate_weather_description(description):
    translations = {
        "clear sky": "맑음",
        "few clouds": "구름 조금",
        "scattered clouds": "구름 약간",
        "broken clouds": "구름 많음",
        "overcast clouds": "흐림",
        "shower rain": "소나기",
        "rain": "비",
        "light rain": "가벼운 비",
        "moderate rain": "보통 비",
        "heavy intensity rain": "강한 비",
        "very heavy rain": "매우 강한 비",
        "extreme rain": "극심한 비",
        "freezing rain": "어는 비",
        "thunderstorm": "뇌우",
        "snow": "눈",
        "light snow": "가벼운 눈",
        "heavy snow": "강한 눈",
        "sleet": "진눈깨비",
        "shower sleet": "소나기 진눈깨비",
        "light rain and snow": "가벼운 비와 눈",
        "rain and snow": "비와 눈",
        "light shower snow": "가벼운 소나기 눈",
        "shower snow": "소나기 눈",
        "heavy shower snow": "강한 소나기 눈",
        "mist": "안개",
        "fog": "안개",
        "haze": "실안개",
        "sand": "모래",
        "dust": "먼지",
        "volcanic ash": "화산재",
        "squalls": "돌풍",
        "tornado": "토네이도"
    }
    return translations.get(description, description)

@app.get("/")
def root(request: Request, db: Session = Depends(get_db)):
    records = db.query(WeatherRecord).order_by(WeatherRecord.date.desc()).limit(5).all()
    favorites = db.query(WeatherRecord).filter(WeatherRecord.is_favorite == True).all()
    return templates.TemplateResponse("index.html", {"request": request, "records": records, "favorites": favorites})

@app.get("/weather")
def get_weather_by_coords(lat: float, lon: float, db: Session = Depends(get_db)):
    current_weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=kr"
    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=kr"
    
    current_weather_response = requests.get(current_weather_url)
    forecast_response = requests.get(forecast_url)

    if current_weather_response.status_code == 200 and forecast_response.status_code == 200:
        current_data = current_weather_response.json()
        forecast_data = forecast_response.json()

        timezone_offset = current_data["timezone"]
        local_time = datetime.datetime.utcfromtimestamp(current_data["dt"] + timezone_offset).strftime("%Y년 %m월 %d일 %H시 %M분 %S초")
        korea_time = datetime.datetime.now(pytz.timezone("Asia/Seoul")).strftime("%Y년 %m월 %d일 %H시 %M분 %S초")
        sunrise_time = datetime.datetime.utcfromtimestamp(current_data["sys"]["sunrise"] + timezone_offset).strftime("%H:%M:%S")
        sunset_time = datetime.datetime.utcfromtimestamp(current_data["sys"]["sunset"] + timezone_offset).strftime("%H:%M:%S")
        korea_offset = 9 * 3600
        timezone_diff = (timezone_offset - korea_offset) // 3600

        weather_description = translate_weather_description(current_data["weather"][0]["description"])

        weather_data = {
            "city": current_data["name"],
            "lat": lat,
            "lon": lon,
            "date": local_time,
            "temperature": current_data["main"]["temp"],
            "feels_like": current_data["main"]["feels_like"],
            "temp_min": current_data["main"]["temp_min"],
            "temp_max": current_data["main"]["temp_max"],
            "description": weather_description,
            "humidity": current_data["main"]["humidity"],
            "wind_speed": current_data["wind"]["speed"],
            "pressure": current_data["main"]["pressure"],
            "uv_index": current_data.get("uvi", "N/A"),
            "rain": current_data.get("rain", {}).get("1h", 0),
            "sunrise": sunrise_time,
            "sunset": sunset_time,
            "korea_time": korea_time,
            "timezone_diff": timezone_diff,
            "forecast": [
                {
                    "date": item["dt_txt"],
                    "temperature": item["main"]["temp"],
                    "feels_like": item["main"]["feels_like"],
                    "temp_min": item["main"]["temp_min"],
                    "temp_max": item["main"]["temp_max"],
                    "description": translate_weather_description(item["weather"][0]["description"]),
                    "humidity": item["main"]["humidity"],
                    "wind_speed": item["wind"]["speed"],
                    "rain": item.get("rain", {}).get("3h", 0),
                    "pop": item.get("pop", 0) * 100
                }
                for item in forecast_data["list"]
            ]
        }

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

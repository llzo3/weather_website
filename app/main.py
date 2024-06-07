from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import os
import requests
import datetime
import pytz

load_dotenv()  # .env 파일의 환경 변수 로드

DATABASE_URL = os.getenv("DATABASE_URL")
API_KEY = os.getenv("API_KEY")

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
    humidity = Column(Integer)
    wind_speed = Column(Float)
    pressure = Column(Integer)
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

def convert_time_to_local(timestamp, timezone):
    utc_dt = datetime.datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
    local_dt = utc_dt.astimezone(pytz.timezone(timezone))
    return local_dt

@app.get("/")
def root(request: Request, db: Session = Depends(get_db)):
    records = db.query(WeatherRecord).order_by(WeatherRecord.id.desc()).limit(5).all()
    return templates.TemplateResponse("index.html", {"request": request, "records": records})

@app.get("/weather")
def get_weather_by_coords(lat: float, lon: float, db: Session = Depends(get_db)):
    URL = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    response = requests.get(URL)

    if response.status_code == 200:
        data = response.json()
        weather_data = {
            "city": data["name"],
            "lat": lat,
            "lon": lon,
            "date": convert_time_to_local(data["dt"], data["timezone"]),
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "temp_min": data["main"]["temp_min"],
            "temp_max": data["main"]["temp_max"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "pressure": data["main"]["pressure"],
            "uv_index": data["uvi"],
            "sunrise": convert_time_to_local(data["sys"]["sunrise"], data["timezone"]),
            "sunset": convert_time_to_local(data["sys"]["sunset"], data["timezone"])
        }

        weather_record = WeatherRecord(
            city=weather_data["city"],
            lat=lat,
            lon=lon,
            date=datetime.datetime.now(),
            temperature=weather_data["temperature"],
            feels_like=weather_data["feels_like"],
            temp_min=weather_data["temp_min"],
            temp_max=weather_data["temp_max"],
            description=weather_data["description"],
            humidity=weather_data["humidity"],
            wind_speed=weather_data["wind_speed"],
            pressure=weather_data["pressure"],
            uv_index=weather_data["uv_index"],
            sunrise=weather_data["sunrise"],
            sunset=weather_data["sunset"]
        )
        db.add(weather_record)
        db.commit()

        return weather_data
    else:
        return {"message": "Failed to fetch weather data"}

@app.get("/history")
def get_history(request: Request, db: Session = Depends(get_db)):
    records = db.query(WeatherRecord).order_by(WeatherRecord.id.desc()).all()
    return templates.TemplateResponse("history.html", {"request": request, "records": records})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

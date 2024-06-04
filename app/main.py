from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import sqlite3
import requests
import datetime

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")

API_KEY = "7984a6ee79bc96d84c6a09aaf4cdf934"

def get_db():
    db_path = "weather.db"
    conn = sqlite3.connect(db_path)
    try:
        yield conn.cursor()
    finally:
        conn.close()

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
        conn = sqlite3.connect("weather.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO weather (city, date, temperature, feels_like, temp_min, temp_max, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (weather_data["city"], datetime.datetime.now(), weather_data["temperature"], 
              weather_data["feels_like"], weather_data["temp_min"], weather_data["temp_max"], weather_data["description"]))
        conn.commit()
        conn.close()

        return templates.TemplateResponse("index.html", {"request": request, "weather": weather_data})
    else:
        return {"message": "Failed to fetch weather data"}

@app.get("/weather", response_class=HTMLResponse)
def read_weather_data(request: Request):
    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM weather")
    rows = cursor.fetchall()
    conn.close()

    weather_data = [
        {"id": row[0], "city": row[1], "date": row[2], "temperature": row[3], "feels_like": row[4], 
         "temp_min": row[5], "temp_max": row[6], "description": row[7]} 
        for row in rows
    ]
    
    return templates.TemplateResponse("weather.html", {"request": request, "weather_data": weather_data})

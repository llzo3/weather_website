from fastapi import FastAPI
import requests

app = FastAPI()

LAT = 37.477550020716194
LON = 126.98212524649105
API_KEY = "2c1d56123e5c377524128dbc99536f60"

@app.get("/")
def root():
    URL = f"https://api.openweathermap.org/data/2.5/onecall?lat={LAT}&lon={LON}&exclude=minutely,hourly&units=metric&appid={API_KEY}"
    response = requests.get(URL)
    
    # 응답이 성공적인지 확인 (HTTP 상태 코드 200)
    if response.status_code == 200:
        contents = response.json()
    else:
        contents = response.text  # 에러 메시지를 그대로 반환

    return {"message": contents}

@app.get("/home")
def home():
    return {"message": "Home!"}

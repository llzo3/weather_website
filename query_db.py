import sqlite3

def get_all_weather_data(db_path="weather.db"):
    # SQLite 데이터베이스 연결
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # weather 테이블에서 모든 데이터 조회
    cursor.execute("SELECT * FROM weather")
    rows = cursor.fetchall()

    # 조회된 데이터 출력
    for row in rows:
        print(f"ID: {row[0]}, City: {row[1]}, Date: {row[2]}, Temperature: {row[3]}°C, "
              f"Feels Like: {row[4]}°C, Min Temp: {row[5]}°C, Max Temp: {row[6]}°C, Description: {row[7]}")

    # 연결 종료
    conn.close()

if __name__ == "__main__":
    get_all_weather_data()

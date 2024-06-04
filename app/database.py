from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# 데이터베이스 URL 설정
DATABASE_URL = "sqlite:///./weather.db"

# 데이터베이스 엔진 생성
engine = create_engine(DATABASE_URL)

# 세션 로컬 설정
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 기본 클래스 생성
Base = declarative_base()

# ORM 모델 정의
class Weather(Base):
    __tablename__ = "weather"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, index=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    temperature = Column(Float)
    feels_like = Column(Float)
    temp_min = Column(Float)
    temp_max = Column(Float)
    description = Column(String)

# 데이터베이스에 테이블 생성
Base.metadata.create_all(bind=engine)

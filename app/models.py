# app/models.py

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class WeatherRecord(Base):
    __tablename__ = "weather_records"
    
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, index=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    temperature = Column(String)
    feels_like = Column(String)
    temp_min = Column(String)
    temp_max = Column(String)
    description = Column(String)

from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.orm import relationship
from data_base.dbcore import Base


class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    latitude = Column(Float, nullable=False)
    longtitude = Column(Float, nullable=False)
    timezone = Column(String, nullable=True)

    reminders = relationship('Reminder', back_populates='location')

    def __str__(self):
        return f'location {self.latitude}, {self.longitude}'

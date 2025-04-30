from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from data_base.dbcore import Base


class Reminder(Base):
    __tablename__ = 'reminders'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('user.id'), nullable=False)
    date_time = Column(DateTime, nullable=False)
    text = Column(Text, nullable=False)
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=True)

    user = relationship('User', back_populates='reminders')
    location = relationship('Location', back_populates='reminders')

    def __str__(self):
        return f'reminder {self.text} at {self.date_time}'

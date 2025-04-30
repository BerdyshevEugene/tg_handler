from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from data_base.dbcore import Base


class Group(Base):
    __tablename__ = 'group'

    id = Column(BigInteger, primary_key=True)
    name = Column(String)
    description = Column(String)
    users = relationship('User', back_populates='group')


class User(Base):
    __tablename__ = 'user'

    id = Column(BigInteger, primary_key=True)
    username = Column(String, index=True)
    chat_id = Column(BigInteger, unique=True, nullable=True)

    group_id = Column(BigInteger, ForeignKey('group.id'))
    group = relationship('Group', back_populates='users')

    reminders = relationship('Reminder', back_populates='user')

    def __str__(self):
        return self.name

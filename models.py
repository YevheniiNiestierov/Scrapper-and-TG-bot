from sqlalchemy import Column, Integer, String
from database.database_config import Base


class Vacancies(Base):
    __tablename__ = "vacancies"

    datetime = Column(String, primary_key=True)
    vacancy_count = Column(Integer)
    change = Column(Integer)


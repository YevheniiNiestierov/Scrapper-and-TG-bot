from uuid import UUID

from pydantic import BaseModel


class VacanciesBase(BaseModel):
    datetime: str
    vacancy_count: int
    change: int

    class Config:
        orm_mode = True  #orm_mode to read data even if it's not a dict, but ORM model


from typing import Literal
from pydantic import BaseModel, Field
from datetime import datetime


class Book(BaseModel):
    serial_number: str = Field(pattern=r"^[0-9]{6}$")
    title: str
    author: str


class Client(BaseModel):
    card_number: str = Field(pattern=r"^[0-9]{6}$")
    name: str | None = None


class BookStatus(BaseModel):
    serial_number: str
    status: Literal["available", "taken"]
    loan_id: int | None = None
    borrowed_at: datetime | None = None
    returned_at: datetime | None = None

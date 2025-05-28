from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ReservationResponse(BaseModel):
    id: int
    firstName: Optional[str]
    lastName: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    createdAt: Optional[datetime]
    reservationDate: Optional[datetime]
    service: Optional[str]
    people: Optional[int]
    duration: Optional[int]
    whoCreated: Optional[str]
    cancelled: Optional[bool]

    class Config:
        orm_mode = True


class ReservationCreate(BaseModel):
    firstName: str
    lastName: str
    email: str
    phone: str
    createdAt: datetime
    reservationDate: datetime
    service: str
    people: int
    duration: int
    whoCreated: str
    cancelled: bool

class LoginRequest(BaseModel):
    email_or_username: str
    password: str

class AppConfigResponse(BaseModel):
    id: int
    stations: Optional[int]
    seats: Optional[int]

    class Config:
        from_attributes = True

class AppConfigCreate(BaseModel):
    stations: int
    seats: int
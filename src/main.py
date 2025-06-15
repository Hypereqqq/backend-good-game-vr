from fastapi import Body, FastAPI, Depends, HTTPException, Request
from fastapi import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from typing import List

from db.database import get_db
from lg.auth import login_user

from api.models import AppConfig, Reservation
from api.schemas import AppConfigCreate, AppConfigResponse, ReservationResponse, ReservationCreate, LoginRequest

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import logging


from datetime import datetime, timezone
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/reservations", response_model=List[ReservationResponse])
async def get_reservations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Reservation))
    return result.scalars().all()

@app.post("/reservations", response_model=ReservationResponse)
async def create_reservation(reservation: ReservationCreate, db: AsyncSession = Depends(get_db)):
    new_res = Reservation(**reservation.model_dump())
    db.add(new_res)
    try: 
        await db.commit()
        await db.refresh(new_res)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Nie udało się dodać rezerwacji (prawdopodobnie konflikt ID)")
    return new_res

@app.put("/reservations/{id}", response_model=ReservationResponse)
async def update_reservation(
    id: int = Path(..., description="ID rezerwacji do zaktualizowania"),
    updated_data: ReservationCreate = Body(...),
    db: AsyncSession = Depends(get_db),
):
    query = await db.execute(select(Reservation).where(Reservation.id == id))
    reservation = query.scalars().first()

    if not reservation:
        raise HTTPException(status_code=404, detail="Rezerwacja nie istnieje")

    for field, value in updated_data.dict(by_alias=True).items():
        setattr(reservation, field, value)

    await db.commit()
    await db.refresh(reservation)
    return reservation

@app.delete("/reservations/{id}", status_code=204)
async def delete_reservation(id: int, db: AsyncSession = Depends(get_db)):
    query = await db.execute(select(Reservation).where(Reservation.id == id))
    reservation = query.scalars().first()

    if not reservation:
        raise HTTPException(status_code=404, detail="Rezerwacja nie istnieje")

    await db.delete(reservation)
    await db.commit()
    return

# Logowanie

logging.basicConfig(filename='login_attempts.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

# Konfiguracja rate limiter
limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, data: LoginRequest, db=Depends(get_db)):
    ip = request.client.host
    result, status = await login_user(data.email_or_username, data.password, db)

    if status != 200:
        logging.warning(f"Nieudana próba logowania z IP: {ip}, login: {data.email_or_username}")
        return False

    logging.info(f"Użytkownik {data.email_or_username} zalogował się z IP: {ip}")
    return True


# Ustawienia

@app.get("/config", response_model=List[AppConfigResponse])
async def get_app_config(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AppConfig))
    return result.scalars().all()

@app.put("/config/{id}", response_model=AppConfigResponse)
async def update_config(
    updated_data: AppConfigCreate = Body(...),
    db: AsyncSession = Depends(get_db),
):
    id = 1
    query = await db.execute(select(AppConfig).where(AppConfig.id == id))
    config = query.scalars().first()

    if not config:
        raise HTTPException(status_code=404, detail="Rezerwacja nie istnieje")

    for field, value in updated_data.dict(by_alias=True).items():
        setattr(config, field, value)

    await db.commit()
    await db.refresh(config)
    return config
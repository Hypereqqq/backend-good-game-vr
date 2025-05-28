import bcrypt
from sqlalchemy.future import select
from api.models import User

async def login_user(email_or_username: str, password: str, db):
    query = select(User).where(
        (User.email == email_or_username) | (User.username == email_or_username)
    )
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        return {"error": "Użytkownik nie znaleziony"}, 401

    if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return {"error": "Nieprawidłowe hasło"}, 401

    return {
        "message": "Zalogowano pomyślnie",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }, 200
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, WebSocketException, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from . import config
from .config import settings
from datetime import timedelta, datetime
from ..db.db import get_async_db
from ..models import models, schemas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


# https://chatgpt.com/share/67c3371b-bb78-8010-9d44-81b728ddb08e

"""
Why These Functions Should Remain Synchronous

1. Token Creation (create_access_token)

- Uses standard Python datetime for expiration calculations.
- Calls jwt.encode() to generate a JWT, which is a CPU-bound operation (not I/O-bound).
- Running it asynchronously won’t improve performance, as it's just a local computation.

2. Token Verification (verify_access_token)

- Uses jwt.decode(), which is a CPU-bound operation.
- Extracts and validates the token data, which is also local computation.
- Since no I/O is happening, there's no need for async.

3.Fetching the Current User (get_current_user)

- Calls verify_access_token(), which is already synchronous.
- Uses a synchronous SQLAlchemy database session (Session) to query the user.
- Since FastAPI’s default Session is blocking, making this function async would not work correctly unless you were using an async database session (like SQLModel with asyncpg).

# When Would You Use async Here?

The only reason to make get_current_user() asynchronous is if you are using an async database ORM.
"""

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, [ALGORITHM])

        id: str = payload.get("user_id")
        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=str(id))
    except JWTError:
        raise credentials_exception
    
    return token_data

async def get_current_user(websocket, db: AsyncSession):
    token = websocket.query_params.get("token") # Read the token from the query params
    if not token: 
        auth_header = websocket.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        else:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Missing Authentication Token")
        
    token_data = verify_access_token(token) # Verify the token
    user = await db.get(models.User, token_data["id"])
    if not user:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")

    return user
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.db import get_async_db
from ..core import utils, oauth
from ..models import schemas, models
from sqlalchemy.future import select

router = APIRouter(tags=["Authentication"])

@router.post("/login", response_model=schemas.Token)
async def login(user_creadentials: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(models.User).where(models.User.email==user_creadentials.username))
    user = result.scalar_one_or_none()

    if not user or not utils.verify(user_creadentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    access_token = oauth.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register/", status_code=status.HTTP_200_OK)
async def register(user_info: schemas.UserCreate, db: AsyncSession = Depends(get_async_db)):

    # Missing Email Check for Existing User.
    # Check if user already exist   

    """
    Why This Fix Works?
    select(models.User).where(...)         correctly creates an async-compatible query.
    await db.execute(stmt)                 properly executes it.
    scalar_one_or_none()                   fetches one result or None if no user exists.
    """


    # existing_user = await db.scalar(select(models.User).where(models.User.email == user_info.email))
    result = await db.execute(select(models.User).where(models.User.email == user_info.email))
    existing_user = result.scalar_one_or_none() 

    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")


    # Hash password and create user instance
    hashed_password = utils.get_password_hash(user_info.password)
    user_data = user_info.model_dump()  # Convert Pydantic model to dict
    user_data["password"] = hashed_password  # Replace password with hashed one

    new_user = models.User(**user_data)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"message": "User registered successfully"}
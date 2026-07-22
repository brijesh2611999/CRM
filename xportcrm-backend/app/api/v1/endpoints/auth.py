from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import TenantSignup, Login, Token
from app.services import auth_service

router = APIRouter()


@router.post("/signup", response_model=Token, status_code=201)
async def signup(data: TenantSignup, db: AsyncSession = Depends(get_db)):
    token = await auth_service.signup_tenant(db, data)
    return Token(access_token=token)


@router.post("/login", response_model=Token)
async def login(data: Login, db: AsyncSession = Depends(get_db)):
    token = await auth_service.login(db, data)
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return Token(access_token=token)
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, SQLModel, select

from backend.database import engine
from backend.models import User
from backend.services.auth_service import hash_password,verify_password,create_access_token


router = APIRouter(prefix="/auth",tags=["Authentication"])

class UserCreate(SQLModel):
    username: str
    email: str
    password: str

class UserLogin(SQLModel):
    username:str
    password:str


@router.post("/register")
def register_user(user_data: UserCreate):
    with Session(engine) as session:
        existing_username = session.exec(select(User).where(User.username == user_data.username)).first()
        if existing_username:
            raise HTTPException( status_code=400, detail="Username already exists")
        existing_email = session.exec(select(User).where( User.email == user_data.email)).first()
        if existing_email:
            raise HTTPException(status_code=400,detail="Email already exists")
        user = User(username=user_data.username,email=user_data.email,hashed_password=hash_password( user_data.password))
        session.add(user)
        session.commit()
        session.refresh(user)
        return {
            "message": "User registered successfully",
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
        }

@router.post("/login")
def login_user(user_data:UserLogin):
    with Session(engine)as session:
        user=session.exec(select(User).where(User.username==user_data.username)).first()
        if not user:
            raise HTTPException(status_code=401,detail="Invalid username or password")
        password_valid=verify_password(user_data.password,user.hashed_password)
        if not password_valid:
                    raise HTTPException(status_code=401,detail="Invalid username or password")
        access_token = create_access_token(user.username)

        return {
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
        }
    
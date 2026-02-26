from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_user
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.auth import AuthService
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user

    - **email**: Valid email address
    - **password**: Strong password (min 8 characters)
    - **full_name**: Optional full name
    """
    user = AuthService.register(db, user_data)
    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with email and password

    Returns JWT access token
    """
    user_data = UserLogin(email=form_data.username, password=form_data.password)
    token = AuthService.login(db, user_data)
    return token


@router.post("/login/json", response_model=Token)
def login_json(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login with JSON body (alternative to form data)

    - **email**: User email
    - **password**: User password
    """
    token = AuthService.login(db, user_data)
    return token


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information

    Requires: Bearer token in Authorization header
    """
    return current_user


@router.post("/logout")
def logout():
    """
    Logout (client-side token removal)

    JWT tokens are stateless, so logout is handled on client side by removing the token
    """
    return {"message": "Successfully logged out"}

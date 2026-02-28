from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import timedelta

from app.core.deps import get_db, get_current_active_user
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.auth import AuthService
from app.models.user import User, SubscriptionTier
from app.core.config import settings
from app.core.security import create_access_token

router = APIRouter()


class GoogleTokenRequest(BaseModel):
    credential: str  # Google ID Token


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


@router.post("/google", response_model=Token)
def google_auth(
    body: GoogleTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate with Google ID Token (from Google Identity Services).
    Creates the user if they don't exist yet.
    """
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests

        client_id = settings.GOOGLE_CLIENT_ID
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google OAuth is not configured on this server"
            )

        idinfo = id_token.verify_oauth2_token(
            body.credential,
            google_requests.Request(),
            client_id
        )

        google_id = idinfo["sub"]
        email = idinfo.get("email")
        full_name = idinfo.get("name")

        if not email:
            raise HTTPException(status_code=400, detail="Could not retrieve email from Google account")

        # Find existing user by google_id or email
        user = db.query(User).filter(User.google_id == google_id).first()
        if not user:
            user = db.query(User).filter(User.email == email).first()

        if user:
            # Update google_id if not set
            if not user.google_id:
                user.google_id = google_id
                db.commit()
        else:
            # Create new user (no password needed)
            user = User(
                email=email,
                full_name=full_name,
                google_id=google_id,
                hashed_password=None,
                subscription_tier=SubscriptionTier.FREE,
                query_credits=10,
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid Google token: {e}")


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

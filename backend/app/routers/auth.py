import secrets
from datetime import timedelta
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserLogin, UserCreate, UserResponse, Token
from app.utils.security import verify_password, get_password_hash, create_access_token, require_current_user
from app.config import settings

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

GOOGLE_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

def _require_google_config():
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=503, detail="Google OAuth chưa được cấu hình")

def _google_username(email: str, db: Session) -> str:
    base = email.split("@", 1)[0].lower().replace(".", "_")[:80] or "google_user"
    username = base
    suffix = 1
    while db.query(User).filter(User.username == username).first():
        username = f"{base}_{suffix}"
        suffix += 1
    return username

@router.post("/login", response_model=Token)
def login(form_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not user.is_active or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )

@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter((User.username == user_in.username) | (User.email == user_in.email)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản hoặc email đã tồn tại trong hệ thống"
        )
    
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role="user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserResponse.from_orm(new_user)

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(require_current_user)):
    return UserResponse.from_orm(current_user)

@router.get("/google/login")
def google_login():
    _require_google_config()
    state = create_access_token(
        {"purpose": "google_oauth", "nonce": secrets.token_urlsafe(16)},
        expires_delta=timedelta(minutes=10),
    )
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "online",
        "prompt": "select_account",
    }
    return RedirectResponse(f"{GOOGLE_AUTHORIZE_URL}?{urlencode(params)}")

@router.get("/google/callback")
async def google_callback(code: str, state: str, db: Session = Depends(get_db)):
    _require_google_config()
    try:
        state_payload = jwt.decode(state, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if state_payload.get("purpose") != "google_oauth":
            raise ValueError("Invalid OAuth state")
    except (JWTError, ValueError):
        raise HTTPException(status_code=400, detail="OAuth state không hợp lệ hoặc đã hết hạn")

    async with httpx.AsyncClient(timeout=15.0) as client:
        token_response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Không thể xác thực mã Google OAuth")

    token_data = token_response.json()
    google_token = token_data.get("id_token")
    if not google_token:
        raise HTTPException(status_code=400, detail="Google không trả về ID token")

    try:
        profile = id_token.verify_oauth2_token(
            google_token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except ValueError:
        raise HTTPException(status_code=401, detail="Google ID token không hợp lệ")

    email = (profile.get("email") or "").lower().strip()
    if not email or not profile.get("email_verified"):
        raise HTTPException(status_code=403, detail="Tài khoản Google chưa xác minh email")

    user = db.query(User).filter(User.email == email).first()
    is_admin = email in settings.google_admin_email_list
    if user:
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Tài khoản đã bị vô hiệu hóa")
        if is_admin and user.role != "admin":
            user.role = "admin"
        user.full_name = profile.get("name") or user.full_name
    else:
        user = User(
            username=_google_username(email, db),
            email=email,
            hashed_password=get_password_hash(secrets.token_urlsafe(32)),
            full_name=profile.get("name") or email.split("@", 1)[0],
            role="admin" if is_admin else "user",
        )
        db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    redirect_url = f"{settings.FRONTEND_URL.rstrip('/')}?oauth_token={access_token}"
    return RedirectResponse(redirect_url)

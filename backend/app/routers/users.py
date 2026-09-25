from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserAdminResponse, UserAdminUpdate
from app.utils.security import get_admin_user

router = APIRouter(prefix="/api/v1/users", tags=["User Management"])


@router.get("", response_model=List[UserAdminResponse])
def list_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    return db.query(User).order_by(User.created_at.desc(), User.id.desc()).all()


@router.patch("/{user_id}", response_model=UserAdminResponse)
def update_user(
    user_id: int,
    payload: UserAdminUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    if payload.role is not None and payload.role not in {"admin", "user"}:
        raise HTTPException(status_code=400, detail="Role không hợp lệ")
    if user.id == admin_user.id and payload.is_active is False:
        raise HTTPException(status_code=400, detail="Không thể vô hiệu hóa tài khoản đang sử dụng")
    if user.id == admin_user.id and payload.role == "user":
        raise HTTPException(status_code=400, detail="Không thể hạ quyền tài khoản admin đang sử dụng")
    if user.role == "admin" and payload.role == "user":
        admin_count = db.query(User).filter(User.role == "admin", User.is_active.is_(True)).count()
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="Hệ thống phải còn ít nhất một admin đang hoạt động")

    if payload.role is not None:
        user.role = payload.role
    if payload.is_active is not None:
        user.is_active = payload.is_active
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    if user.id == admin_user.id:
        raise HTTPException(status_code=400, detail="Không thể xóa tài khoản đang sử dụng")
    if user.role == "admin":
        admin_count = db.query(User).filter(User.role == "admin", User.is_active.is_(True)).count()
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="Không thể xóa admin cuối cùng")
    db.delete(user)
    db.commit()

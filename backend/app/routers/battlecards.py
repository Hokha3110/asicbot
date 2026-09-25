from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.battlecard import BattleCard
from app.schemas.battlecard import BattleCardResponse, BattleCardCreate, BattleCardGenerateRequest
from app.services.battlecard_service import BattleCardService
from app.utils.security import get_admin_user, require_current_user

router = APIRouter(prefix="/api/v1/battlecards", tags=["Battle Cards"])

@router.get("", response_model=List[BattleCardResponse])
def get_battlecards(
    solution_name: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(BattleCard)
    if solution_name:
        query = query.filter(BattleCard.solution_name.ilike(f"%{solution_name}%"))
    if category:
        query = query.filter(BattleCard.category.ilike(f"%{category}%"))
    return query.order_by(BattleCard.solution_name.asc()).all()

@router.get("/{card_id}", response_model=BattleCardResponse)
def get_battlecard_by_id(card_id: int, db: Session = Depends(get_db)):
    card = db.query(BattleCard).filter(BattleCard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Không tìm thấy Battle Card")
    return card

@router.post("/generate", response_model=BattleCardResponse)
async def generate_battlecard(
    req: BattleCardGenerateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_current_user)
):
    """
    Generates a complete presales competitive battle card using AI.
    """
    battlecard = await BattleCardService.generate_battlecard(
        solution_name=req.solution_name,
        db=db,
        vendor=req.vendor,
        category=req.category
    )
    return battlecard

@router.post("", response_model=BattleCardResponse)
def create_battlecard(
    card_in: BattleCardCreate,
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    new_card = BattleCard(**card_in.dict())
    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    return new_card

@router.delete("/{card_id}")
def delete_battlecard(
    card_id: int,
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    card = db.query(BattleCard).filter(BattleCard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Không tìm thấy Battle Card")
    db.delete(card)
    db.commit()
    return {"message": "Đã xóa Battle Card thành công"}

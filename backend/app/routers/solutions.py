import re
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.solution import Solution
from app.models.user import User
from app.schemas.solution import SolutionResponse, SolutionCreate, SolutionUpdate, SmartSearchQuery
from app.services.vector_service import vector_service
from app.utils.security import get_admin_user

router = APIRouter(prefix="/api/v1/solutions", tags=["Solution Database"])

@router.get("", response_model=List[SolutionResponse])
def get_solutions(
    category: Optional[str] = None,
    vendor: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Solution)
    if category and category != "all":
        query = query.filter(Solution.category.ilike(f"%{category}%"))
    if vendor and vendor != "all":
        query = query.filter(Solution.vendor.ilike(f"%{vendor}%"))
    return query.order_by(Solution.name.asc()).all()

@router.get("/{solution_id}", response_model=SolutionResponse)
def get_solution_by_id(solution_id: int, db: Session = Depends(get_db)):
    sol = db.query(Solution).filter(Solution.id == solution_id).first()
    if not sol:
        raise HTTPException(status_code=404, detail="Không tìm thấy giải pháp")
    return sol

@router.post("/smart-search", response_model=List[SolutionResponse])
def smart_search(
    query_in: SmartSearchQuery,
    db: Session = Depends(get_db)
):
    """
    Semantic & NLP Intent matching for customer inquiries.
    Example 1: "kiểm tra hacker có vượt qua hệ thống không" -> Matches Picus BAS
    Example 2: "biết dữ liệu nhạy cảm nằm ở đâu" -> Matches Forcepoint / Netwrix DSPM
    """
    user_query = query_in.query.lower()
    all_solutions = db.query(Solution).all()
    
    scored_solutions = []
    
    # Check semantic matches from vector DB chunks
    vector_results = vector_service.query_similar(user_query, top_k=5)
    matched_doc_texts = " ".join([r["text"].lower() for r in vector_results])

    for sol in all_solutions:
        score = 0.0
        sol_text = f"{sol.name} {sol.vendor} {sol.category} {sol.problem} {sol.description} {' '.join(sol.keywords or [])} {' '.join(sol.features or [])} {' '.join(sol.use_case or [])}".lower()
        
        # 1. Direct Keyword / Synonym matching
        query_words = re.findall(r'\w+', user_query)
        for w in query_words:
            if len(w) > 2 and w in sol_text:
                score += 3.0

        # 2. Specific Presales Intent Heuristics
        if any(w in user_query for w in ["hacker", "vượt qua", "tấn công", "mô phỏng", "pentest", "kiểm tra phòng thủ", "mitre"]):
            if "picus" in sol.name.lower() or "bas" in sol.category.lower():
                score += 15.0

        if any(w in user_query for w in ["dữ liệu", "nhạy cảm", "nằm ở đâu", "dspm", "phân loại", "thẻ tín dụng", "lộ lọt", "pii"]):
            if "dspm" in sol.name.lower() or "dspm" in sol.category.lower() or "forcepoint" in sol.name.lower() or "netwrix" in sol.name.lower():
                score += 15.0

        if any(w in user_query for w in ["quyền", "access", "đặc quyền", "tài khoản", "ad", "active directory"]):
            if "access analyzer" in sol.name.lower() or "identity" in sol.category.lower() or "pam" in sol.category.lower():
                score += 12.0

        if any(w in user_query for w in ["soc", "siem", "log", "quản lý log", "giám sát", "alert"]):
            if "graylog" in sol.name.lower() or "siem" in sol.category.lower() or "trend micro" in sol.name.lower():
                score += 12.0

        # 3. Vector relevance boost
        if sol.name.lower() in matched_doc_texts or sol.vendor.lower() in matched_doc_texts:
            score += 5.0

        if score > 0:
            scored_solutions.append((score, sol))

    # Sort by score descending
    scored_solutions.sort(key=lambda x: x[0], reverse=True)
    
    if scored_solutions:
        return [item[1] for item in scored_solutions[:query_in.top_k]]
    
    # If no high confidence matches, return top solutions in the category or default list
    return all_solutions[:query_in.top_k]

@router.post("", response_model=SolutionResponse)
def create_solution(
    sol_in: SolutionCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    existing = db.query(Solution).filter(Solution.name == sol_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Giải pháp với tên này đã tồn tại")
    
    new_sol = Solution(**sol_in.dict())
    db.add(new_sol)
    db.commit()
    db.refresh(new_sol)
    return new_sol

@router.put("/{solution_id}", response_model=SolutionResponse)
def update_solution(
    solution_id: int,
    sol_in: SolutionUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    sol = db.query(Solution).filter(Solution.id == solution_id).first()
    if not sol:
        raise HTTPException(status_code=404, detail="Không tìm thấy giải pháp")
    
    update_data = sol_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(sol, key, value)
        
    db.commit()
    db.refresh(sol)
    return sol

@router.delete("/{solution_id}")
def delete_solution(
    solution_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    sol = db.query(Solution).filter(Solution.id == solution_id).first()
    if not sol:
        raise HTTPException(status_code=404, detail="Không tìm thấy giải pháp")
    db.delete(sol)
    db.commit()
    return {"message": f"Đã xóa giải pháp '{sol.name}' thành công"}

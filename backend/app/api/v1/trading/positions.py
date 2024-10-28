from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.position import Position
from app.schemas.position import PositionCreate, PositionResponse, PositionUpdate
from app.services.trading.position_manager import PositionManager

router = APIRouter()

@router.get("/", response_model=List[PositionResponse])
def get_positions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve positions.
    """
    position_manager = PositionManager(db, current_user)
    return position_manager.get_positions(skip=skip, limit=limit)

@router.get("/{position_id}", response_model=PositionResponse)
def get_position(
    position_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get position by ID.
    """
    position = db.query(Position).filter(
        Position.id == position_id,
        Position.user_id == current_user.id
    ).first()
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position not found"
        )
    return position

@router.post("/{position_id}/close")
def close_position(
    position_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Close position.
    """
    position_manager = PositionManager(db, current_user)
    try:
        position_manager.close_position(position_id)
        return {"msg": "Position successfully closed"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{position_id}/update-sl-tp", response_model=PositionResponse)
def update_sl_tp(
    position_id: int,
    position_data: PositionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update position's stop loss and take profit.
    """
    position_manager = PositionManager(db, current_user)
    try:
        position = position_manager.update_sl_tp(position_id, position_data)
        if not position:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Position not found"
            )
        return position
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/summary", response_model=dict)
def get_positions_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get summary of all positions.
    """
    position_manager = PositionManager(db, current_user)
    return position_manager.get_positions_summary()
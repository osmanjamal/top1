from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.signal import Signal
from app.schemas.signal import SignalCreate, SignalResponse, SignalUpdate
from app.services.trading.signal_processor import SignalProcessor

router = APIRouter()

@router.post("/webhook", response_model=SignalResponse)
async def receive_signal(
    signal_data: SignalCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Any:
    """
    Receive trading signals from external sources (TradingView, custom indicators, etc.)
    """
    try:
        signal_processor = SignalProcessor(db)
        signal = await signal_processor.process_signal(signal_data)
        # Process signal in background
        background_tasks.add_task(signal_processor.execute_signal_strategy, signal.id)
        return signal
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[SignalResponse])
def get_signals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve signals.
    """
    signals = db.query(Signal).filter(
        Signal.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return signals

@router.get("/{signal_id}", response_model=SignalResponse)
def get_signal(
    signal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get signal by ID.
    """
    signal = db.query(Signal).filter(
        Signal.id == signal_id,
        Signal.user_id == current_user.id
    ).first()
    if not signal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signal not found"
        )
    return signal

@router.get("/statistics", response_model=dict)
def get_signal_statistics(
    timeframe: str = "1d",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get signal statistics including success rate, average profit, etc.
    """
    signal_processor = SignalProcessor(db)
    return signal_processor.get_statistics(current_user.id, timeframe)

@router.post("/{signal_id}/backtest")
def backtest_signal(
    signal_id: int,
    timeframe: str = "1m",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Backtest signal strategy.
    """
    signal_processor = SignalProcessor(db)
    try:
        results = signal_processor.backtest_signal(signal_id, timeframe)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{signal_id}/settings", response_model=SignalResponse)
def update_signal_settings(
    signal_id: int,
    settings: SignalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update signal settings.
    """
    signal = db.query(Signal).filter(
        Signal.id == signal_id,
        Signal.user_id == current_user.id
    ).first()
    if not signal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signal not found"
        )
    
    for field, value in settings.dict(exclude_unset=True).items():
        setattr(signal, field, value)
    db.commit()
    db.refresh(signal)
    return signal
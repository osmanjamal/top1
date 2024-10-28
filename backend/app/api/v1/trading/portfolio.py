from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.services.trading.portfolio_manager import PortfolioManager
from app.schemas.portfolio import PortfolioStats, PortfolioHistory, PortfolioAsset

router = APIRouter()

@router.get("/overview", response_model=Dict[str, Any])
def get_portfolio_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get portfolio overview including total balance, PnL, and allocation.
    """
    portfolio_manager = PortfolioManager(db, current_user)
    try:
        return portfolio_manager.get_overview()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/stats", response_model=PortfolioStats)
def get_portfolio_stats(
    timeframe: str = "1d",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get portfolio statistics including win rate, average trade, etc.
    Timeframe options: 1d, 1w, 1m, 3m, 6m, 1y, all
    """
    portfolio_manager = PortfolioManager(db, current_user)
    try:
        return portfolio_manager.get_stats(timeframe)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/history", response_model=PortfolioHistory)
def get_portfolio_history(
    timeframe: str = "1m",
    interval: str = "1d",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get portfolio value history.
    Timeframe options: 1d, 1w, 1m, 3m, 6m, 1y, all
    Interval options: 1h, 4h, 1d, 1w
    """
    portfolio_manager = PortfolioManager(db, current_user)
    try:
        return portfolio_manager.get_history(timeframe, interval)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/assets", response_model=list[PortfolioAsset])
def get_portfolio_assets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get list of all assets in portfolio with their current values and allocations.
    """
    portfolio_manager = PortfolioManager(db, current_user)
    try:
        return portfolio_manager.get_assets()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/performance", response_model=Dict[str, Any])
def get_portfolio_performance(
    timeframe: str = "1m",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get detailed portfolio performance metrics including:
    - Sharpe ratio
    - Drawdown
    - Risk metrics
    - Returns comparison
    """
    portfolio_manager = PortfolioManager(db, current_user)
    try:
        return portfolio_manager.get_performance_metrics(timeframe)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/risk", response_model=Dict[str, Any])
def get_portfolio_risk_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current portfolio risk metrics including:
    - Leverage used
    - Margin levels
    - Position concentration
    - Risk allocation
    """
    portfolio_manager = PortfolioManager(db, current_user)
    try:
        return portfolio_manager.get_risk_metrics()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
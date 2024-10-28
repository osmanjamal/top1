from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
import logging
from datetime import datetime, timedelta

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.position import Position, PositionStatus
from app.models.order import Order, OrderStatus
from app.schemas.portfolio import (
    PortfolioStats, PortfolioHistory, PortfolioAsset,
    PortfolioSummary, PortfolioRisk, TradingPerformance
)
from app.services.trading.portfolio_manager import PortfolioManager
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/overview", response_model=PortfolioSummary)
async def get_portfolio_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get portfolio overview including total balance, PnL, and allocation.
    """
    try:
        portfolio_manager = PortfolioManager(db, current_user)
        return await portfolio_manager.get_overview()
    except Exception as e:
        logger.error(f"Error getting portfolio overview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get portfolio overview"
        )

@router.get("/stats", response_model=PortfolioStats)
async def get_portfolio_stats(
    timeframe: str = Query(
        "1m",
        description="Time period for stats calculation: 1d, 1w, 1m, 3m, 6m, 1y, all"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get portfolio statistics including win rate, average trade, etc.
    """
    try:
        portfolio_manager = PortfolioManager(db, current_user)
        return await portfolio_manager.get_stats(timeframe)
    except Exception as e:
        logger.error(f"Error getting portfolio stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get portfolio statistics"
        )

@router.get("/history", response_model=PortfolioHistory)
async def get_portfolio_history(
    timeframe: str = Query("1m", description="History period"),
    interval: str = Query("1d", description="Data interval"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get portfolio value history.
    """
    try:
        portfolio_manager = PortfolioManager(db, current_user)
        return await portfolio_manager.get_history(timeframe, interval)
    except Exception as e:
        logger.error(f"Error getting portfolio history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get portfolio history"
        )

@router.get("/assets", response_model=List[PortfolioAsset])
async def get_portfolio_assets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of all assets in portfolio with their current values and allocations.
    """
    try:
        portfolio_manager = PortfolioManager(db, current_user)
        return await portfolio_manager.get_assets()
    except Exception as e:
        logger.error(f"Error getting portfolio assets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get portfolio assets"
        )

@router.get("/performance", response_model=TradingPerformance)
async def get_portfolio_performance(
    timeframe: str = Query("1m", description="Performance analysis period"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed portfolio performance metrics.
    """
    try:
        portfolio_manager = PortfolioManager(db, current_user)
        return await portfolio_manager.get_performance_metrics(timeframe)
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get performance metrics"
        )

@router.get("/risk", response_model=PortfolioRisk)
async def get_portfolio_risk_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current portfolio risk metrics.
    """
    try:
        portfolio_manager = PortfolioManager(db, current_user)
        return await portfolio_manager.get_risk_metrics()
    except Exception as e:
        logger.error(f"Error getting risk metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get risk metrics"
        )

@router.get("/positions/active", response_model=List[Dict[str, Any]])
async def get_active_positions(
    symbol: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all active positions with current market data.
    """
    try:
        query = db.query(Position).filter(
            Position.user_id == current_user.id,
            Position.status == PositionStatus.OPEN
        )
        
        if symbol:
            query = query.filter(Position.symbol == symbol)
            
        positions = query.all()
        
        # Enrich positions with current market data
        portfolio_manager = PortfolioManager(db, current_user)
        enriched_positions = []
        
        for position in positions:
            position_data = position.to_dict()
            market_data = await portfolio_manager.get_position_market_data(position.symbol)
            
            if market_data:
                position_data.update({
                    'current_price': market_data.get('price'),
                    'funding_rate': market_data.get('funding_rate'),
                    'mark_price': market_data.get('mark_price'),
                    'index_price': market_data.get('index_price')
                })
            
            enriched_positions.append(position_data)
            
        return enriched_positions
        
    except Exception as e:
        logger.error(f"Error getting active positions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get active positions"
        )

@router.get("/positions/history", response_model=List[Dict[str, Any]])
async def get_position_history(
    symbol: Optional[str] = None,
    status: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get historical positions with filtering options.
    """
    try:
        query = db.query(Position).filter(Position.user_id == current_user.id)
        
        if symbol:
            query = query.filter(Position.symbol == symbol)
        if status:
            query = query.filter(Position.status == status)
        if start_time:
            query = query.filter(Position.opened_at >= start_time)
        if end_time:
            query = query.filter(Position.opened_at <= end_time)
            
        positions = query.order_by(Position.opened_at.desc()).limit(limit).all()
        return [position.to_dict() for position in positions]
        
    except Exception as e:
        logger.error(f"Error getting position history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get position history"
        )

@router.get("/trades/summary", response_model=Dict[str, Any])
async def get_trades_summary(
    timeframe: str = Query("7d", description="Summary period"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get trading summary statistics.
    """
    try:
        portfolio_manager = PortfolioManager(db, current_user)
        return await portfolio_manager.get_trades_summary(timeframe)
    except Exception as e:
        logger.error(f"Error getting trades summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get trades summary"
        )

@router.get("/analysis/drawdown", response_model=Dict[str, Any])
async def get_drawdown_analysis(
    timeframe: str = Query("1m", description="Analysis period"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get drawdown analysis including maximum drawdown and recovery periods.
    """
    try:
        portfolio_manager = PortfolioManager(db, current_user)
        return await portfolio_manager.get_drawdown_analysis(timeframe)
    except Exception as e:
        logger.error(f"Error getting drawdown analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get drawdown analysis"
        )

@router.get("/analysis/risk-adjusted-returns", response_model=Dict[str, Any])
async def get_risk_adjusted_returns(
    timeframe: str = Query("1m", description="Analysis period"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get risk-adjusted return metrics (Sharpe, Sortino, etc.).
    """
    try:
        portfolio_manager = PortfolioManager(db, current_user)
        return await portfolio_manager.get_risk_adjusted_returns(timeframe)
    except Exception as e:
        logger.error(f"Error getting risk-adjusted returns: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get risk-adjusted returns"
        )

@router.get("/analysis/correlation", response_model=Dict[str, Any])
async def get_portfolio_correlation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get correlation analysis between different assets in portfolio.
    """
    try:
        portfolio_manager = PortfolioManager(db, current_user)
        return await portfolio_manager.get_portfolio_correlation()
    except Exception as e:
        logger.error(f"Error getting portfolio correlation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get portfolio correlation"
        )

@router.get("/reports/daily", response_model=Dict[str, Any])
async def get_daily_report(
    date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get daily portfolio report with detailed metrics.
    """
    try:
        portfolio_manager = PortfolioManager(db, current_user)
        return await portfolio_manager.generate_daily_report(date or datetime.utcnow())
    except Exception as e:
        logger.error(f"Error generating daily report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate daily report"
        )

@router.get("/reports/monthly", response_model=Dict[str, Any])
async def get_monthly_report(
    year: int = Query(..., ge=2020),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get monthly portfolio performance report.
    """
    try:
        portfolio_manager = PortfolioManager(db, current_user)
        return await portfolio_manager.generate_monthly_report(year, month)
    except Exception as e:
        logger.error(f"Error generating monthly report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate monthly report"
        )

@router.get("/reports/pnl-distribution", response_model=Dict[str, Any])
async def get_pnl_distribution(
    timeframe: str = Query("1m", description="Analysis period"),
    interval: str = Query("1d", description="Distribution interval"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get PnL distribution analysis.
    """
    try:
        portfolio_manager = PortfolioManager(db, current_user)
        return await portfolio_manager.get_pnl_distribution(timeframe, interval)
    except Exception as e:
        logger.error(f"Error getting PnL distribution: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get PnL distribution"
        )

@router.get("/strategy/analysis", response_model=Dict[str, Any])
async def get_strategy_analysis(
    strategy_name: Optional[str] = None,
    timeframe: str = Query("1m", description="Analysis period"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get trading strategy performance analysis.
    """
    try:
        portfolio_manager = PortfolioManager(db, current_user)
        return await portfolio_manager.get_strategy_analysis(strategy_name, timeframe)
    except Exception as e:
        logger.error(f"Error getting strategy analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get strategy analysis"
        )

@router.get("/strategy/comparison", response_model=Dict[str, Any])
async def get_strategy_comparison(
    timeframe: str = Query("1m", description="Comparison period"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Compare performance across different trading strategies.
    """
    try:
        portfolio_manager = PortfolioManager(db, current_user)
        return await portfolio_manager.get_strategy_comparison(timeframe)
    except Exception as e:
        logger.error(f"Error getting strategy comparison: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get strategy comparison"
        )

@router.get("/optimization/suggestions", response_model=Dict[str, Any])
async def get_portfolio_optimization(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get portfolio optimization suggestions based on historical performance.
    """
    try:
        portfolio_manager = PortfolioManager(db, current_user)
        return await portfolio_manager.get_optimization_suggestions()
    except Exception as e:
        logger.error(f"Error getting optimization suggestions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get optimization suggestions"
        )

@router.get("/limits/status", response_model=Dict[str, Any])
async def get_trading_limits_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current status of trading limits and restrictions.
    """
    try:
        portfolio_manager = PortfolioManager(db, current_user)
        return await portfolio_manager.get_trading_limits_status()
    except Exception as e:
        logger.error(f"Error getting trading limits status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get trading limits status"
        )
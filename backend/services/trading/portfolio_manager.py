from typing import List, Dict, Any, Optional
from decimal import Decimal
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from app.models.position import Position, PositionStatus
from app.models.order import Order
from app.models.trade import Trade
from app.models.user import User
from app.core.config import settings
from app.exchanges.binance.futures import BinanceFuturesClient
from app.core.risk.risk_management import RiskManager
from app.schemas.portfolio import PortfolioStats, PortfolioHistory, PortfolioAsset

logger = logging.getLogger(__name__)

class PortfolioManager:
    """
    Service for managing trading portfolio and analytics.
    """
    
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
        self.risk_manager = RiskManager(user)
        
        # Initialize exchange client
        self.futures_client = BinanceFuturesClient(
            api_key=user.binance_api_key,
            api_secret=user.binance_api_secret,
            testnet=settings.BINANCE_TESTNET
        )

    async def get_overview(self) -> Dict[str, Any]:
        """
        Get portfolio overview including total balance, PnL, and allocation.
        """
        try:
            # Get account information
            account_info = self.futures_client.get_account_info()
            
            # Get open positions
            open_positions = await self._get_open_positions()
            
            # Calculate total balance and PnL
            total_balance = float(account_info['totalWalletBalance'])
            unrealized_pnl = sum(p.unrealized_pnl or 0 for p in open_positions)
            total_margin_used = float(account_info['totalPositionInitialMargin'])
            available_balance = float(account_info['availableBalance'])
            
            # Calculate daily PnL
            daily_pnl = await self._calculate_daily_pnl()
            
            # Calculate asset allocation
            allocation = await self._calculate_asset_allocation(open_positions, total_balance)
            
            return {
                'total_balance': total_balance,
                'unrealized_pnl': unrealized_pnl,
                'realized_pnl_24h': daily_pnl,
                'margin_used': total_margin_used,
                'available_balance': available_balance,
                'margin_level': (total_balance / total_margin_used if total_margin_used > 0 else 0) * 100,
                'open_positions_count': len(open_positions),
                'asset_allocation': allocation,
                'risk_level': self.risk_manager.calculate_risk_score(),
                'account_health': await self._calculate_account_health()
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio overview: {str(e)}")
            raise

    async def get_stats(self, timeframe: str = "1m") -> PortfolioStats:
        """
        Get portfolio statistics including win rate, average trade, etc.
        """
        try:
            # Get time range based on timeframe
            start_time = self._get_start_time(timeframe)
            
            # Get trades within timeframe
            trades = self.db.query(Trade).filter(
                Trade.user_id == self.user.id,
                Trade.created_at >= start_time
            ).all()
            
            if not trades:
                return PortfolioStats(
                    win_rate=0,
                    profit_factor=0,
                    avg_win=0,
                    avg_loss=0,
                    largest_win=0,
                    largest_loss=0,
                    total_trades=0,
                    profitable_trades=0,
                    unprofitable_trades=0
                )
            
            # Calculate statistics
            profitable_trades = [t for t in trades if t.realized_pnl and t.realized_pnl > 0]
            unprofitable_trades = [t for t in trades if t.realized_pnl and t.realized_pnl <= 0]
            
            win_rate = len(profitable_trades) / len(trades) * 100 if trades else 0
            
            total_profit = sum(t.realized_pnl for t in profitable_trades) if profitable_trades else 0
            total_loss = abs(sum(t.realized_pnl for t in unprofitable_trades)) if unprofitable_trades else 0
            
            profit_factor = total_profit / total_loss if total_loss > 0 else total_profit
            
            avg_win = total_profit / len(profitable_trades) if profitable_trades else 0
            avg_loss = total_loss / len(unprofitable_trades) if unprofitable_trades else 0
            
            largest_win = max((t.realized_pnl or 0) for t in trades)
            largest_loss = min((t.realized_pnl or 0) for t in trades)
            
            return PortfolioStats(
                win_rate=win_rate,
                profit_factor=profit_factor,
                avg_win=avg_win,
                avg_loss=avg_loss,
                largest_win=largest_win,
                largest_loss=largest_loss,
                total_trades=len(trades),
                profitable_trades=len(profitable_trades),
                unprofitable_trades=len(unprofitable_trades)
            )
            
        except Exception as e:
            logger.error(f"Error calculating portfolio stats: {str(e)}")
            raise

    async def get_history(self, timeframe: str = "1m", interval: str = "1d") -> PortfolioHistory:
        """
        Get portfolio value history.
        """
        try:
            # Get time range based on timeframe
            start_time = self._get_start_time(timeframe)
            
            # Get daily balance snapshots and PnL
            snapshots = await self._get_balance_history(start_time, interval)
            
            return PortfolioHistory(
                timestamps=[s['timestamp'] for s in snapshots],
                balance=[s['balance'] for s in snapshots],
                pnl=[s['pnl'] for s in snapshots],
                drawdown=[s['drawdown'] for s in snapshots]
            )
            
        except Exception as e:
            logger.error(f"Error getting portfolio history: {str(e)}")
            raise

    async def get_assets(self) -> List[PortfolioAsset]:
        """
        Get list of all assets in portfolio with their current values and allocations.
        """
        try:
            # Get account balances
            account_info = self.futures_client.get_account_info()
            total_balance = float(account_info['totalWalletBalance'])
            
            # Get open positions
            positions = await self._get_open_positions()
            
            assets = []
            for position in positions:
                asset_value = position.size * position.mark_price
                allocation = (asset_value / total_balance * 100) if total_balance > 0 else 0
                
                assets.append(PortfolioAsset(
                    symbol=position.symbol,
                    size=position.size,
                    value=asset_value,
                    allocation=allocation,
                    unrealized_pnl=position.unrealized_pnl,
                    unrealized_pnl_pct=position.unrealized_pnl_pct,
                    leverage=position.leverage,
                    liquidation_price=position.liquidation_price,
                    entry_price=position.entry_price,
                    mark_price=position.mark_price
                ))
                
            return sorted(assets, key=lambda x: x.value, reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting portfolio assets: {str(e)}")
            raise

    async def get_performance_metrics(self, timeframe: str = "1m") -> Dict[str, Any]:
        """
        Get detailed portfolio performance metrics.
        """
        try:
            # Get portfolio history
            history = await self.get_history(timeframe)
            
            if not history.balance:
                return {
                    "sharpe_ratio": 0,
                    "sortino_ratio": 0,
                    "max_drawdown": 0,
                    "max_drawdown_duration": 0,
                    "volatility": 0,
                    "beta": 0,
                    "alpha": 0,
                    "r_squared": 0
                }
            
            # Convert to pandas DataFrame for calculations
            df = pd.DataFrame({
                'balance': history.balance,
                'pnl': history.pnl,
                'drawdown': history.drawdown
            })
            
            # Calculate returns
            df['returns'] = df['balance'].pct_change()
            
            # Calculate metrics
            risk_free_rate = 0.02  # Assumed annual risk-free rate
            daily_rf = (1 + risk_free_rate) ** (1/365) - 1
            
            excess_returns = df['returns'] - daily_rf
            negative_returns = df['returns'][df['returns'] < 0]
            
            metrics = {
                "sharpe_ratio": self._calculate_sharpe_ratio(excess_returns),
                "sortino_ratio": self._calculate_sortino_ratio(excess_returns, negative_returns),
                "max_drawdown": df['drawdown'].min() if 'drawdown' in df else 0,
                "max_drawdown_duration": self._calculate_max_drawdown_duration(df['drawdown']),
                "volatility": df['returns'].std() * np.sqrt(365) if 'returns' in df else 0,
                "value_at_risk": self._calculate_var(df['returns']),
                "expected_shortfall": self._calculate_expected_shortfall(df['returns']),
                "calmar_ratio": self._calculate_calmar_ratio(df['returns'], df['drawdown'])
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {str(e)}")
            raise

    async def get_risk_metrics(self) -> Dict[str, Any]:
        """
        Get current portfolio risk metrics.
        """
        try:
            account_info = self.futures_client.get_account_info()
            positions = await self._get_open_positions()
            
            total_balance = float(account_info['totalWalletBalance'])
            
            # Calculate risk metrics
            metrics = {
                "total_leverage": sum(p.leverage * (p.size * p.mark_price) / total_balance for p in positions),
                "margin_usage": float(account_info['totalPositionInitialMargin']) / total_balance * 100,
                "liquidation_risk": await self._calculate_liquidation_risk(positions),
                "position_concentration": self._calculate_position_concentration(positions, total_balance),
                "correlation_risk": await self._calculate_correlation_risk(positions),
                "exchange_exposure": await self._calculate_exchange_exposure(),
                "risk_distribution": self._calculate_risk_distribution(positions),
                "risk_adjusted_exposure": self.risk_manager.calculate_risk_adjusted_exposure()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {str(e)}")
            raise

    async def _get_open_positions(self) -> List[Position]:
        """Get all open positions with updated market data."""
        positions = self.db.query(Position).filter(
            Position.user_id == self.user.id,
            Position.status == PositionStatus.OPEN
        ).all()
        
        # Update positions with latest market data
        for position in positions:
            await self._update_position_market_data(position)
            
        return positions

    def _get_start_time(self, timeframe: str) -> datetime:
        """Convert timeframe string to datetime."""
        now = datetime.utcnow()
        if timeframe == "1d":
            return now - timedelta(days=1)
        elif timeframe == "1w":
            return now - timedelta(weeks=1)
        elif timeframe == "1m":
            return now - timedelta(days=30)
        elif timeframe == "3m":
            return now - timedelta(days=90)
        elif timeframe == "6m":
            return now - timedelta(days=180)
        elif timeframe == "1y":
            return now - timedelta(days=365)
        else:
            return now - timedelta(days=30)

    @staticmethod
    def _calculate_sharpe_ratio(excess_returns: pd.Series) -> float:
        """Calculate Sharpe ratio."""
        if excess_returns.empty or excess_returns.std() == 0:
            return 0
        return excess_returns.mean() / excess_returns.std() * np.sqrt(365)

    @staticmethod
    def _calculate_sortino_ratio(excess_returns: pd.Series, negative_returns: pd.Series) -> float:
        """Calculate Sortino ratio."""
        if excess_returns.empty or negative_returns.empty or negative_returns.std() == 0:
            return 0
        return excess_returns.mean() / negative_returns.std() * np.sqrt(365)

    @staticmethod
    def _calculate_max_drawdown_duration(drawdown: pd.Series) -> int:
        """Calculate maximum drawdown duration in days."""
        if drawdown.empty:
            return 0
            
        is_drawdown = drawdown < 0
        drawdown_start = is_drawdown.shift(1).fillna(False)
        drawdown_end = is_drawdown.shift(-1).fillna(False)
        
        durations = []
        current_duration = 0
        
        for i in range(len(drawdown)):
            if is_drawdown[i]:
                current_duration += 1
            elif current_duration > 0:
                durations.append(current_duration)
                current_duration = 0
                
        return max(durations) if durations else 0

    @staticmethod
    def _calculate_var(returns: pd.Series, confidence_level: float = 0.95) -> float:
        """Calculate Value at Risk."""
        if returns.empty:
            return 0
        return returns.quantile(1 - confidence_level)

    @staticmethod
    def _calculate_expected_shortfall(returns: pd.Series, confidence_level: float = 0.95) -> float:
        """Calculate Expected Shortfall (CVaR)."""
        if returns.empty:
            return 0
        var = returns.quantile(1 - confidence_level)
        return returns[returns <= var].mean()

    @staticmethod
    def _calculate_calmar_ratio(returns: pd.Series, drawdown: pd.Series) -> float:
        """Calculate Calmar ratio."""
        if returns.empty or drawdown.empty or drawdown.min() == 0:
            return 0
        return returns.mean() * 365 / abs(drawdown.min())
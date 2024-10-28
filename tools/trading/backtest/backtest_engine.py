from typing import Dict, List, Optional, Any, Callable
import pandas as pd
import numpy as np
from datetime import datetime
import logging
from dataclasses import dataclass
from decimal import Decimal

from app.models.order import Order, OrderType, OrderSide
from app.models.position import Position, PositionSide
from app.core.risk.risk_management import RiskManager
from app.core.risk.position_sizing import PositionSizingManager

logger = logging.getLogger(__name__)

@dataclass
class BacktestConfig:
    """Configuration for backtesting."""
    initial_capital: float
    trading_fees: float = 0.001  # 0.1% trading fee
    slippage: float = 0.0005    # 0.05% slippage
    leverage: int = 1
    margin_type: str = "crossed"
    position_size_type: str = "fixed"  # fixed, risk_percentage, kelly
    position_size: float = 0.1  # 10% of capital if using risk_percentage
    use_stop_loss: bool = True
    stop_loss_pct: float = 0.02  # 2% stop loss
    use_take_profit: bool = True
    take_profit_pct: float = 0.06  # 6% take profit
    use_trailing_stop: bool = False
    trailing_stop_pct: float = 0.02  # 2% trailing stop

@dataclass
class BacktestResult:
    """Results from backtesting."""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    total_return: float
    annual_return: float
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    trades: List[Dict]
    equity_curve: pd.Series
    monthly_returns: pd.Series
    drawdown_curve: pd.Series

class BacktestEngine:
    """Engine for backtesting trading strategies."""
    
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.capital = config.initial_capital
        self.positions: Dict[str, Position] = {}
        self.trades: List[Dict] = []
        self.equity_history: List[float] = [config.initial_capital]
        self.risk_manager = RiskManager(None)  # Initialize without user
        self.position_sizing = PositionSizingManager(None)  # Initialize without user
        
        # Performance tracking
        self.total_pnl = 0.0
        self.total_fees = 0.0
        self.peak_equity = config.initial_capital
        self.current_drawdown = 0.0
        self.max_drawdown = 0.0

    def run_backtest(
        self,
        data: pd.DataFrame,
        strategy: Callable,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> BacktestResult:
        """
        Run backtest on historical data.
        
        Args:
            data: Historical price data
            strategy: Strategy function that generates trading signals
            start_date: Start date for backtest
            end_date: End date for backtest
            
        Returns:
            BacktestResult object containing test results
        """
        try:
            # Filter data by date range if specified
            if start_date:
                data = data[data.index >= start_date]
            if end_date:
                data = data[data.index <= end_date]
                
            # Initialize tracking variables
            equity_curve = []
            positions_history = []
            trades_history = []
            
            # Run through each bar
            for timestamp, bar in data.iterrows():
                # Update positions with current price
                self._update_positions(bar)
                
                # Check stop loss and take profit
                self._check_exits(bar)
                
                # Generate trading signals
                signals = strategy(bar, data.loc[:timestamp])
                
                # Execute signals
                if signals:
                    self._execute_signals(signals, bar)
                
                # Record equity and positions
                equity_curve.append(self._calculate_equity())
                positions_history.append(self._get_positions_snapshot())
                
                # Update drawdown
                self._update_drawdown(equity_curve[-1])
            
            # Calculate results
            results = self._calculate_results(
                pd.Series(equity_curve, index=data.index),
                trades_history
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error running backtest: {str(e)}")
            raise

    def _update_positions(self, bar: pd.Series) -> None:
        """Update all open positions with current market data."""
        for symbol, position in self.positions.items():
            # Update position market value
            position.mark_price = bar['close']
            
            # Calculate unrealized PnL
            if position.side == PositionSide.LONG:
                pnl = (bar['close'] - position.entry_price) * position.size
            else:
                pnl = (position.entry_price - bar['close']) * position.size
                
            position.unrealized_pnl = pnl
            
            # Update other metrics
            self._update_position_metrics(position)

    def _check_exits(self, bar: pd.Series) -> None:
        """Check and execute stop loss and take profit orders."""
        for symbol, position in list(self.positions.items()):
            # Check stop loss
            if self.config.use_stop_loss:
                if self._check_stop_loss(position, bar):
                    self._close_position(position, bar, 'stop_loss')
                    continue
                    
            # Check take profit
            if self.config.use_take_profit:
                if self._check_take_profit(position, bar):
                    self._close_position(position, bar, 'take_profit')
                    continue
                    
            # Check trailing stop
            if self.config.use_trailing_stop:
                if self._check_trailing_stop(position, bar):
                    self._close_position(position, bar, 'trailing_stop')

    def _execute_signals(
        self,
        signals: List[Dict],
        bar: pd.Series
    ) -> None:
        """Execute trading signals."""
        for signal in signals:
            if signal['action'] == 'buy':
                self._open_long_position(signal['symbol'], bar)
            elif signal['action'] == 'sell':
                self._open_short_position(signal['symbol'], bar)
            elif signal['action'] == 'close':
                if signal['symbol'] in self.positions:
                    self._close_position(
                        self.positions[signal['symbol']],
                        bar,
                        'signal'
                    )

    def _open_long_position(
        self,
        symbol: str,
        bar: pd.Series
    ) -> None:
        """Open a long position."""
        # Check if we can open new position
        if not self._can_open_position(symbol, bar):
            return
            
        # Calculate position size
        size = self._calculate_position_size(bar)
        if not size:
            return
            
        # Create position
        position = Position(
            symbol=symbol,
            side=PositionSide.LONG,
            entry_price=bar['close'],
            size=size,
            leverage=self.config.leverage
        )
        
        # Add fees
        fee = size * bar['close'] * self.config.trading_fees
        self.total_fees += fee
        self.capital -= fee
        
        # Update tracking
self.positions[symbol] = position
        self._record_trade('long', position, bar)

    def _open_short_position(
        self,
        symbol: str,
        bar: pd.Series
    ) -> None:
        """Open a short position."""
        # Check if we can open new position
        if not self._can_open_position(symbol, bar):
            return
            
        # Calculate position size
        size = self._calculate_position_size(bar)
        if not size:
            return
            
        # Create position
        position = Position(
            symbol=symbol,
            side=PositionSide.SHORT,
            entry_price=bar['close'],
            size=size,
            leverage=self.config.leverage
        )
        
        # Add fees
        fee = size * bar['close'] * self.config.trading_fees
        self.total_fees += fee
        self.capital -= fee
        
        # Update tracking
        self.positions[symbol] = position
        self._record_trade('short', position, bar)

    def _close_position(
        self,
        position: Position,
        bar: pd.Series,
        reason: str
    ) -> None:
        """Close an open position."""
        # Calculate PnL
        if position.side == PositionSide.LONG:
            pnl = (bar['close'] - position.entry_price) * position.size
        else:
            pnl = (position.entry_price - bar['close']) * position.size
            
        # Add fees
        fee = position.size * bar['close'] * self.config.trading_fees
        self.total_fees += fee
        
        # Update capital
        self.capital += pnl - fee
        self.total_pnl += pnl
        
        # Record trade
        self._record_trade('close', position, bar, pnl, reason)
        
        # Remove position
        del self.positions[position.symbol]

    def _calculate_position_size(self, bar: pd.Series) -> Optional[float]:
        """Calculate position size based on configuration."""
        try:
            if self.config.position_size_type == 'fixed':
                return self.config.position_size
            
            elif self.config.position_size_type == 'risk_percentage':
                risk_amount = self.capital * self.config.position_size
                price = bar['close']
                stop_loss = price * (1 - self.config.stop_loss_pct)
                return risk_amount / (price - stop_loss)
            
            elif self.config.position_size_type == 'kelly':
                # Implement Kelly Criterion position sizing
                win_rate = self._calculate_win_rate()
                avg_win = self._calculate_average_win()
                avg_loss = self._calculate_average_loss()
                
                if not all([win_rate, avg_win, avg_loss]):
                    return self.config.position_size
                    
                kelly = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
                return min(kelly, self.config.position_size)
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating position size: {str(e)}")
            return None

    def _can_open_position(self, symbol: str, bar: pd.Series) -> bool:
        """Check if we can open a new position."""
        # Check if symbol already has position
        if symbol in self.positions:
            return False
            
        # Check if we have enough capital
        required_margin = self._calculate_required_margin(bar)
        if required_margin > self.capital:
            return False
            
        # Check drawdown limits
        if self.current_drawdown > self.config.max_drawdown:
            return False
            
        # Check position limits
        if len(self.positions) >= self.risk_manager.max_positions:
            return False
            
        return True

    def _check_stop_loss(self, position: Position, bar: pd.Series) -> bool:
        """Check if position hit stop loss."""
        if position.side == PositionSide.LONG:
            stop_price = position.entry_price * (1 - self.config.stop_loss_pct)
            return bar['low'] <= stop_price
        else:
            stop_price = position.entry_price * (1 + self.config.stop_loss_pct)
            return bar['high'] >= stop_price

    def _check_take_profit(self, position: Position, bar: pd.Series) -> bool:
        """Check if position hit take profit."""
        if position.side == PositionSide.LONG:
            tp_price = position.entry_price * (1 + self.config.take_profit_pct)
            return bar['high'] >= tp_price
        else:
            tp_price = position.entry_price * (1 - self.config.take_profit_pct)
            return bar['low'] <= tp_price

    def _check_trailing_stop(self, position: Position, bar: pd.Series) -> bool:
        """Check if position hit trailing stop."""
        if not hasattr(position, 'highest_price'):
            position.highest_price = position.entry_price
            
        if position.side == PositionSide.LONG:
            # Update highest price
            position.highest_price = max(position.highest_price, bar['high'])
            stop_price = position.highest_price * (1 - self.config.trailing_stop_pct)
            return bar['low'] <= stop_price
        else:
            # Update lowest price
            position.lowest_price = min(position.lowest_price, bar['low'])
            stop_price = position.lowest_price * (1 + self.config.trailing_stop_pct)
            return bar['high'] >= stop_price

    def _update_drawdown(self, current_equity: float) -> None:
        """Update drawdown calculations."""
        self.peak_equity = max(self.peak_equity, current_equity)
        self.current_drawdown = (self.peak_equity - current_equity) / self.peak_equity
        self.max_drawdown = max(self.max_drawdown, self.current_drawdown)

    def _calculate_equity(self) -> float:
        """Calculate current equity including open positions."""
        equity = self.capital
        for position in self.positions.values():
            equity += position.unrealized_pnl
        return equity

    def _calculate_results(
        self,
        equity_curve: pd.Series,
        trades: List[Dict]
    ) -> BacktestResult:
        """Calculate final backtest results."""
        try:
            # Calculate basic metrics
            total_trades = len(trades)
            winning_trades = len([t for t in trades if t['pnl'] > 0])
            losing_trades = total_trades - winning_trades
            
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            # Calculate returns
            total_return = (equity_curve[-1] - equity_curve[0]) / equity_curve[0]
            annual_return = self._calculate_annual_return(equity_curve)
            
            # Calculate risk metrics
            sharpe_ratio = self._calculate_sharpe_ratio(equity_curve)
            sortino_ratio = self._calculate_sortino_ratio(equity_curve)
            
            # Calculate profit factor
            gross_profit = sum([t['pnl'] for t in trades if t['pnl'] > 0])
            gross_loss = abs(sum([t['pnl'] for t in trades if t['pnl'] < 0]))
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
            
            # Calculate monthly returns
            monthly_returns = equity_curve.resample('M').last().pct_change()
            
            # Calculate drawdown curve
            drawdown_curve = (equity_curve.cummax() - equity_curve) / equity_curve.cummax()
            
            return BacktestResult(
                total_trades=total_trades,
                winning_trades=winning_trades,
                losing_trades=losing_trades,
                win_rate=win_rate,
                profit_factor=profit_factor,
                total_return=total_return,
                annual_return=annual_return,
                max_drawdown=self.max_drawdown,
                sharpe_ratio=sharpe_ratio,
                sortino_ratio=sortino_ratio,
                trades=trades,
                equity_curve=equity_curve,
                monthly_returns=monthly_returns,
                drawdown_curve=drawdown_curve
            )
            
        except Exception as e:
            logger.error(f"Error calculating backtest results: {str(e)}")
            raise

    def _record_trade(
        self,
        action: str,
        position: Position,
        bar: pd.Series,
        pnl: float = 0,
        reason: str = 'signal'
    ) -> None:
        """Record trade details."""
        self.trades.append({
            'timestamp': bar.name,
            'symbol': position.symbol,
            'action': action,
            'price': bar['close'],
            'size': position.size,
            'pnl': pnl,
            'reason': reason,
            'equity': self._calculate_equity()
        })

    def _calculate_annual_return(self, equity_curve: pd.Series) -> float:
        """Calculate annualized return."""
        days = (equity_curve.index[-1] - equity_curve.index[0]).days
        if days < 1:
            return 0.0
        return ((1 + (equity_curve[-1] - equity_curve[0]) / equity_curve[0]) ** (365/days)) - 1

    def _calculate_sharpe_ratio(self, equity_curve: pd.Series) -> float:
        """Calculate Sharpe ratio."""
        returns = equity_curve.pct_change().dropna()
        if len(returns) < 2:
            return 0.0
        return np.sqrt(252) * returns.mean() / returns.std()

    def _calculate_sortino_ratio(self, equity_curve: pd.Series) -> float:
        """Calculate Sortino ratio."""
        returns = equity_curve.pct_change().dropna()
        if len(returns) < 2:
            return 0.0
        negative_returns = returns[returns < 0]
        if len(negative_returns) == 0:
            return float('inf')
        return np.sqrt(252) * returns.mean() / negative_returns.std()

    def _calculate_win_rate(self) -> Optional[float]:
        """Calculate historical win rate."""
        if not self.trades:
            return None
        winning_trades = len([t for t in self.trades if t['pnl'] > 0])
        return winning_trades / len(self.trades)

    def _calculate_average_win(self) -> Optional[float]:
        """Calculate average winning trade."""
        winning_trades = [t['pnl'] for t in self.trades if t['pnl'] > 0]
        if not winning_trades:
            return None
        return sum(winning_trades) / len(winning_trades)

    def _calculate_average_loss(self) -> Optional[float]:
        """Calculate average losing trade."""
        losing_trades = [t['pnl'] for t in self.trades if t['pnl'] < 0]
        if not losing_trades:
            return None
        return sum(losing_trades) / len(losing_trades)
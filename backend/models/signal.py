from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Enum, Index, JSON
from sqlalchemy.orm import relationship
import enum
import json

from app.core.database.session import Base

class SignalSource(str, enum.Enum):
    TRADINGVIEW = "TRADINGVIEW"
    CUSTOM_INDICATOR = "CUSTOM_INDICATOR"
    MANUAL = "MANUAL"
    BOT = "BOT"

class SignalType(str, enum.Enum):
    ENTRY = "ENTRY"
    EXIT = "EXIT"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"

class SignalAction(str, enum.Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    CLOSE_LONG = "CLOSE_LONG"
    CLOSE_SHORT = "CLOSE_SHORT"

class SignalStatus(str, enum.Enum):
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"

class Signal(Base):
    """
    Signal model representing trading signals from various sources.
    """
    
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    bot_id = Column(Integer, ForeignKey("bots.id"))
    order_id = Column(Integer, ForeignKey("orders.id"))
    position_id = Column(Integer, ForeignKey("positions.id"))
    
    # Signal identification
    source = Column(Enum(SignalSource), nullable=False)
    type = Column(Enum(SignalType), nullable=False)
    action = Column(Enum(SignalAction), nullable=False)
    status = Column(Enum(SignalStatus), default=SignalStatus.PENDING)
    
    # Market information
    symbol = Column(String, nullable=False, index=True)
    timeframe = Column(String)  # e.g., "1h", "4h", "1d"
    price = Column(Float)
    
    # Signal parameters
    entry_price = Column(Float)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    risk_reward_ratio = Column(Float)
    
    # Position sizing
    quantity = Column(Float)
    leverage = Column(Integer)
    risk_percentage = Column(Float)
    
    # Signal metadata
    description = Column(String)
    strategy_name = Column(String)
    confidence_score = Column(Float)  # 0-100
    time_validity = Column(Integer)  # in minutes
    
    # Technical indicators
    indicators = Column(JSON)  # Store indicator values as JSON
    
    # Execution tracking
    executed_price = Column(Float)
    execution_time = Column(DateTime)
    execution_delay = Column(Float)  # in seconds
    
    # Performance tracking
    pnl = Column(Float)
    pnl_percentage = Column(Float)
    success = Column(Boolean)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expired_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="signals")
    bot = relationship("Bot", back_populates="signals")
    order = relationship("Order", back_populates="signal")
    position = relationship("Position", back_populates="signals")
    
    # Indexes
    __table_args__ = (
        Index('ix_signals_user_symbol', user_id, symbol),
        Index('ix_signals_user_status', user_id, status),
        Index('ix_signals_created_at', created_at),
    )

    @property
    def is_active(self) -> bool:
        """Check if signal is still active."""
        if self.status != SignalStatus.PENDING:
            return False
            
        if self.time_validity and self.created_at:
            time_passed = (datetime.utcnow() - self.created_at).total_seconds() / 60
            return time_passed <= self.time_validity
            
        return True

    @property
    def risk_amount(self) -> Optional[float]:
        """Calculate risk amount in quote currency."""
        if not all([self.entry_price, self.stop_loss, self.quantity]):
            return None
            
        if self.action in [SignalAction.LONG, SignalAction.CLOSE_SHORT]:
            return abs(self.entry_price - self.stop_loss) * self.quantity
        else:
            return abs(self.stop_loss - self.entry_price) * self.quantity

    def set_indicators(self, indicators: dict) -> None:
        """
        Set technical indicators data.
        
        Args:
            indicators: Dictionary of indicator values
        """
        self.indicators = json.dumps(indicators)

    def get_indicators(self) -> Optional[dict]:
        """
        Get technical indicators data.
        
        Returns:
            Dictionary of indicator values
        """
        if not self.indicators:
            return None
            
        return json.loads(self.indicators)

    def calculate_quantity(self, account_balance: float) -> float:
        """
        Calculate position size based on risk parameters.
        
        Args:
            account_balance: Current account balance
            
        Returns:
            Calculated position size
        """
        if not all([self.entry_price, self.stop_loss, self.risk_percentage]):
            return 0.0
            
        risk_amount = account_balance * (self.risk_percentage / 100)
        price_difference = abs(self.entry_price - self.stop_loss)
        
        base_quantity = risk_amount / price_difference
        leveraged_quantity = base_quantity * (self.leverage or 1)
        
        return leveraged_quantity

    def execute_signal(self, executed_price: float) -> None:
        """
        Mark signal as executed with details.
        
        Args:
            executed_price: Price at which signal was executed
        """
        self.status = SignalStatus.EXECUTED
        self.executed_price = executed_price
        self.execution_time = datetime.utcnow()
        
        if self.created_at:
            self.execution_delay = (self.execution_time - self.created_at).total_seconds()
            
        # Calculate PnL if signal is an exit
        if self.type in [SignalType.EXIT, SignalType.STOP_LOSS, SignalType.TAKE_PROFIT]:
            if self.entry_price:
                if self.action == SignalAction.CLOSE_LONG:
                    self.pnl = (executed_price - self.entry_price) * (self.quantity or 0)
                elif self.action == SignalAction.CLOSE_SHORT:
                    self.pnl = (self.entry_price - executed_price) * (self.quantity or 0)
                    
                if self.entry_price > 0:
                    self.pnl_percentage = (abs(executed_price - self.entry_price) / self.entry_price) * 100
                    
                self.success = bool(self.pnl and self.pnl > 0)

    def expire_signal(self) -> None:
        """Mark signal as expired."""
        self.status = SignalStatus.EXPIRED
        self.expired_at = datetime.utcnow()

    def validate_signal(self) -> tuple[bool, str]:
        """
        Validate signal parameters.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.symbol:
            return False, "Symbol is required"
            
        if self.type == SignalType.ENTRY:
            if not self.entry_price or self.entry_price <= 0:
                return False, "Invalid entry price"
                
            if not self.stop_loss or self.stop_loss <= 0:
                return False, "Stop loss is required for entry signals"
                
        if self.risk_percentage and (self.risk_percentage <= 0 or self.risk_percentage > 100):
            return False, "Invalid risk percentage"
            
        if self.leverage and self.leverage <= 0:
            return False, "Invalid leverage"
            
        return True, ""

    def to_dict(self) -> dict:
        """Convert signal to dictionary."""
        return {
            'id': self.id,
            'source': self.source.value,
            'type': self.type.value,
            'action': self.action.value,
            'status': self.status.value,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'price': self.price,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'risk_reward_ratio': self.risk_reward_ratio,
            'quantity': self.quantity,
            'leverage': self.leverage,
            'risk_percentage': self.risk_percentage,
            'description': self.description,
            'strategy_name': self.strategy_name,
            'confidence_score': self.confidence_score,
            'time_validity': self.time_validity,
            'indicators': self.get_indicators(),
            'executed_price': self.executed_price,
            'execution_time': self.execution_time.isoformat() if self.execution_time else None,
            'execution_delay': self.execution_delay,
            'pnl': self.pnl,
            'pnl_percentage': self.pnl_percentage,
            'success': self.success,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'expired_at': self.expired_at.isoformat() if self.expired_at else None,
            'is_active': self.is_active,
            'risk_amount': self.risk_amount
        }

    def __repr__(self) -> str:
        """String representation of signal."""
        return (
            f"Signal(id={self.id}, symbol={self.symbol}, "
            f"type={self.type.value}, action={self.action.value}, "
            f"status={self.status.value})"
        )
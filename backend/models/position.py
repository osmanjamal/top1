from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.schema import CheckConstraint
import enum

from app.core.database.session import Base

class PositionSide(str, enum.Enum):
    LONG = "LONG"
    SHORT = "SHORT"

class PositionStatus(str, enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    LIQUIDATED = "LIQUIDATED"

class MarginType(str, enum.Enum):
    ISOLATED = "ISOLATED"
    CROSSED = "CROSSED"

class Position(Base):
    """
    Position model representing trading positions.
    """
    
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String, nullable=False, index=True)
    side = Column(Enum(PositionSide), nullable=False)
    status = Column(Enum(PositionStatus), nullable=False, default=PositionStatus.OPEN)
    
    # Position details
    entry_price = Column(Float, nullable=False)
    mark_price = Column(Float)
    liquidation_price = Column(Float)
    size = Column(Float, nullable=False)  # Position size in base asset
    leverage = Column(Integer, nullable=False)
    margin_type = Column(Enum(MarginType), default=MarginType.CROSSED)
    isolated_margin = Column(Float)
    
    # Risk management
    stop_loss = Column(Float)
    take_profit = Column(Float)
    trailing_stop = Column(Float)
    
    # PnL tracking
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    total_pnl = Column(Float, default=0.0)
    
    # Position metrics
    roe = Column(Float)  # Return on Equity
    risk_ratio = Column(Float)
    margin_ratio = Column(Float)
    
    # Timestamps
    opened_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="positions")
    orders = relationship("Order", back_populates="position")
    trades = relationship("Trade", back_populates="position")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('size >= 0', name='check_size_positive'),
        CheckConstraint('leverage >= 1', name='check_leverage_minimum'),
        Index('ix_positions_user_symbol', user_id, symbol),
        Index('ix_positions_user_status', user_id, status),
        Index('ix_positions_opened_at', opened_at),
    )

    @property
    def is_open(self) -> bool:
        """Check if position is open."""
        return self.status == PositionStatus.OPEN

    @property
    def is_in_profit(self) -> bool:
        """Check if position is in profit."""
        return bool(self.unrealized_pnl and self.unrealized_pnl > 0)

    @property
    def unrealized_pnl_pct(self) -> float:
        """Calculate unrealized PnL percentage."""
        if not self.entry_price or not self.mark_price:
            return 0.0
        
        if self.side == PositionSide.LONG:
            return ((self.mark_price - self.entry_price) / self.entry_price) * 100
        else:
            return ((self.entry_price - self.mark_price) / self.entry_price) * 100

    def calculate_liquidation_price(self, maintenance_margin_rate: float = 0.01) -> float:
        """
        Calculate liquidation price based on position parameters.
        """
        if self.side == PositionSide.LONG:
            return self.entry_price * (1 - (1 / self.leverage) + maintenance_margin_rate)
        else:
            return self.entry_price * (1 + (1 / self.leverage) - maintenance_margin_rate)

    def update_pnl(self) -> None:
        """Update position's PnL calculations."""
        if not self.mark_price:
            return
            
        # Calculate unrealized PnL
        position_value = self.size * self.mark_price
        entry_value = self.size * self.entry_price
        
        if self.side == PositionSide.LONG:
            self.unrealized_pnl = position_value - entry_value
        else:
            self.unrealized_pnl = entry_value - position_value
            
        # Update total PnL
        self.total_pnl = self.unrealized_pnl + self.realized_pnl
        
        # Calculate ROE
        initial_margin = entry_value / self.leverage
        if initial_margin:
            self.roe = (self.total_pnl / initial_margin) * 100

    def update_from_exchange(self, exchange_position: dict) -> None:
        """
        Update position details from exchange response.
        """
        self.mark_price = float(exchange_position.get('markPrice', self.mark_price))
        self.liquidation_price = float(exchange_position.get('liquidationPrice', self.liquidation_price))
        self.margin_ratio = float(exchange_position.get('marginRatio', self.margin_ratio))
        
        if self.mark_price:
            self.update_pnl()

    def add_margin(self, amount: float) -> None:
        """Add margin to isolated position."""
        if self.margin_type != MarginType.ISOLATED:
            raise ValueError("Can only add margin to isolated positions")
            
        self.isolated_margin = (self.isolated_margin or 0) + amount
        self.liquidation_price = self.calculate_liquidation_price()

    def reduce_margin(self, amount: float) -> None:
        """Reduce margin from isolated position."""
        if self.margin_type != MarginType.ISOLATED:
            raise ValueError("Can only reduce margin from isolated positions")
            
        if not self.isolated_margin or amount > self.isolated_margin:
            raise ValueError("Insufficient margin")
            
        self.isolated_margin -= amount
        self.liquidation_price = self.calculate_liquidation_price()

    def close_position(self, close_price: float, realized_pnl: float = None) -> None:
        """Close the position."""
        self.status = PositionStatus.CLOSED
        self.closed_at = datetime.utcnow()
        
        if realized_pnl is not None:
            self.realized_pnl = realized_pnl
            self.total_pnl = self.realized_pnl
            
        # Clear unrealized values
        self.unrealized_pnl = 0
        self.mark_price = close_price
        self.liquidation_price = None

    def validate_position(self) -> tuple[bool, str]:
        """Validate position parameters."""
        if not self.symbol:
            return False, "Symbol is required"
            
        if not self.size or self.size <= 0:
            return False, "Invalid position size"
            
        if not self.entry_price or self.entry_price <= 0:
            return False, "Invalid entry price"
            
        if self.leverage < 1:
            return False, "Leverage must be at least 1"
            
        if self.margin_type == MarginType.ISOLATED and not self.isolated_margin:
            return False, "Isolated margin is required for isolated positions"
            
        return True, ""

    def to_dict(self) -> dict:
        """Convert position to dictionary."""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'side': self.side.value,
            'status': self.status.value,
            'entry_price': self.entry_price,
            'mark_price': self.mark_price,
            'liquidation_price': self.liquidation_price,
            'size': self.size,
            'leverage': self.leverage,
            'margin_type': self.margin_type.value,
            'isolated_margin': self.isolated_margin,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'trailing_stop': self.trailing_stop,
            'unrealized_pnl': self.unrealized_pnl,
            'realized_pnl': self.realized_pnl,
            'total_pnl': self.total_pnl,
            'roe': self.roe,
            'risk_ratio': self.risk_ratio,
            'margin_ratio': self.margin_ratio,
            'opened_at': self.opened_at.isoformat() if self.opened_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'unrealized_pnl_pct': self.unrealized_pnl_pct,
            'is_open': self.is_open,
            'is_in_profit': self.is_in_profit
        }
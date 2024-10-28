from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Enum, Index
from sqlalchemy.orm import relationship
import enum

from app.core.database.session import Base

class TradeType(str, enum.Enum):
    SPOT = "SPOT"
    MARGIN = "MARGIN"
    FUTURES = "FUTURES"

class TradeSide(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

class TradeStatus(str, enum.Enum):
    NEW = "NEW"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"

class Trade(Base):
    """
    Trade model representing individual trade executions.
    """
    
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"))
    position_id = Column(Integer, ForeignKey("positions.id"))
    exchange_trade_id = Column(String, unique=True, index=True)
    
    # Trade details
    symbol = Column(String, nullable=False, index=True)
    type = Column(Enum(TradeType), nullable=False)
    side = Column(Enum(TradeSide), nullable=False)
    status = Column(Enum(TradeStatus), nullable=False, default=TradeStatus.NEW)
    
    # Price information
    price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    commission = Column(Float)
    commission_asset = Column(String)
    
    # Futures specific
    realized_pnl = Column(Float)
    quote_quantity = Column(Float)  # quantity * price
    
    # Timestamps
    executed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="trades")
    order = relationship("Order", back_populates="trades")
    position = relationship("Position", back_populates="trades")
    
    # Indexes
    __table_args__ = (
        Index('ix_trades_user_symbol', user_id, symbol),
        Index('ix_trades_executed_at', executed_at),
        Index('ix_trades_user_status', user_id, status),
    )

    @property
    def value(self) -> float:
        """Calculate total trade value."""
        return self.price * self.quantity if self.price and self.quantity else 0.0

    @property
    def net_value(self) -> float:
        """Calculate trade value after commission."""
        if not self.commission:
            return self.value
            
        if self.commission_asset == self.symbol.split('USDT')[0]:
            # Commission in base asset
            if self.side == TradeSide.BUY:
                return self.price * (self.quantity - self.commission)
            else:
                return self.price * self.quantity - (self.price * self.commission)
        else:
            # Commission in quote asset (usually USDT)
            return self.value - self.commission

    def calculate_pnl(self, exit_price: float = None) -> float:
        """
        Calculate trade PnL.
        
        Args:
            exit_price: Optional exit price for unrealized PnL calculation
            
        Returns:
            Calculated PnL
        """
        if self.type != TradeType.FUTURES:
            return 0.0
            
        if exit_price and self.status != TradeStatus.FILLED:
            # Calculate unrealized PnL
            if self.side == TradeSide.BUY:
                return (exit_price - self.price) * self.quantity
            else:
                return (self.price - exit_price) * self.quantity
                
        return self.realized_pnl or 0.0

    def calculate_commission(self, commission_rate: Decimal = Decimal('0.001')) -> Decimal:
        """
        Calculate trade commission.
        
        Args:
            commission_rate: Commission rate to apply
            
        Returns:
            Calculated commission
        """
        value = Decimal(str(self.value))
        return value * commission_rate

    def update_from_exchange(self, exchange_trade: dict) -> None:
        """
        Update trade details from exchange response.
        
        Args:
            exchange_trade: Trade information from exchange
        """
        self.exchange_trade_id = exchange_trade.get('id', self.exchange_trade_id)
        self.price = float(exchange_trade.get('price', self.price))
        self.quantity = float(exchange_trade.get('qty', self.quantity))
        
        if 'commission' in exchange_trade:
            self.commission = float(exchange_trade['commission'])
            self.commission_asset = exchange_trade.get('commissionAsset')
            
        if 'realizedPnl' in exchange_trade:
            self.realized_pnl = float(exchange_trade['realizedPnl'])
            
        if 'quoteQty' in exchange_trade:
            self.quote_quantity = float(exchange_trade['quoteQty'])
            
        self.status = TradeStatus(exchange_trade.get('status', self.status))

    def validate_trade(self) -> tuple[bool, str]:
        """
        Validate trade parameters.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.symbol:
            return False, "Symbol is required"
            
        if not self.quantity or self.quantity <= 0:
            return False, "Invalid quantity"
            
        if not self.price or self.price <= 0:
            return False, "Invalid price"
            
        if self.commission and self.commission < 0:
            return False, "Invalid commission"
            
        return True, ""

    def to_dict(self) -> dict:
        """Convert trade to dictionary."""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'position_id': self.position_id,
            'exchange_trade_id': self.exchange_trade_id,
            'symbol': self.symbol,
            'type': self.type.value,
            'side': self.side.value,
            'status': self.status.value,
            'price': self.price,
            'quantity': self.quantity,
            'commission': self.commission,
            'commission_asset': self.commission_asset,
            'realized_pnl': self.realized_pnl,
            'quote_quantity': self.quote_quantity,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'value': self.value,
            'net_value': self.net_value
        }

    def __repr__(self) -> str:
        """String representation of trade."""
        return (
            f"Trade(id={self.id}, symbol={self.symbol}, "
            f"side={self.side.value}, price={self.price}, "
            f"quantity={self.quantity}, status={self.status.value})"
        )
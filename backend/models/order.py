from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Enum, Index
from sqlalchemy.orm import relationship
import enum

from app.core.database.session import Base

class OrderSide(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(str, enum.Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_MARKET = "STOP_MARKET"
    STOP_LIMIT = "STOP_LIMIT"
    TAKE_PROFIT_MARKET = "TAKE_PROFIT_MARKET"
    TAKE_PROFIT_LIMIT = "TAKE_PROFIT_LIMIT"

class OrderStatus(str, enum.Enum):
    NEW = "NEW"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    PENDING_CANCEL = "PENDING_CANCEL"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"

class OrderTimeInForce(str, enum.Enum):
    GTC = "GTC"  # Good Till Cancel
    IOC = "IOC"  # Immediate or Cancel
    FOK = "FOK"  # Fill or Kill
    GTX = "GTX"  # Good Till Crossing

class Order(Base):
    """
    Order model representing trading orders.
    """
    
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exchange_order_id = Column(String, unique=True, index=True)
    symbol = Column(String, nullable=False, index=True)
    side = Column(Enum(OrderSide), nullable=False)
    type = Column(Enum(OrderType), nullable=False)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.NEW)
    
    # Price fields
    price = Column(Float)  # Limit price
    stop_price = Column(Float)  # Stop price for stop orders
    average_price = Column(Float)  # Average fill price
    
    # Quantity fields
    quantity = Column(Float, nullable=False)
    executed_quantity = Column(Float, default=0.0)
    remaining_quantity = Column(Float)
    
    # Order configuration
    time_in_force = Column(Enum(OrderTimeInForce), default=OrderTimeInForce.GTC)
    reduce_only = Column(Boolean, default=False)
    close_position = Column(Boolean, default=False)
    working_type = Column(String)  # MARK_PRICE or CONTRACT_PRICE
    position_side = Column(String)  # LONG, SHORT, or BOTH
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    filled_at = Column(DateTime)
    expired_at = Column(DateTime)
    
    # Position and leverage
    leverage = Column(Integer)
    isolated = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    position = relationship("Position", back_populates="orders")
    trades = relationship("Trade", back_populates="order")
    
    # Indexes for common queries
    __table_args__ = (
        Index('ix_orders_user_symbol', user_id, symbol),
        Index('ix_orders_user_status', user_id, status),
        Index('ix_orders_created_at', created_at),
    )

    @property
    def filled_percentage(self) -> float:
        """Calculate fill percentage of order."""
        if not self.quantity:
            return 0.0
        return (self.executed_quantity / self.quantity) * 100

    @property
    def is_active(self) -> bool:
        """Check if order is still active."""
        return self.status in {
            OrderStatus.NEW,
            OrderStatus.PARTIALLY_FILLED
        }

    @property
    def is_complete(self) -> bool:
        """Check if order is completed."""
        return self.status in {
            OrderStatus.FILLED,
            OrderStatus.CANCELED,
            OrderStatus.REJECTED,
            OrderStatus.EXPIRED
        }

    def calculate_commission(self, commission_rate: Decimal = Decimal('0.001')) -> Decimal:
        """Calculate order commission."""
        if not self.executed_quantity or not self.average_price:
            return Decimal('0')
        
        value = Decimal(str(self.executed_quantity)) * Decimal(str(self.average_price))
        return value * commission_rate

    def update_from_exchange(self, exchange_order: dict) -> None:
        """
        Update order details from exchange response.
        
        Args:
            exchange_order: Order information from exchange
        """
        self.status = OrderStatus(exchange_order.get('status', self.status))
        self.executed_quantity = float(exchange_order.get('executedQty', self.executed_quantity))
        self.remaining_quantity = float(exchange_order.get('remainingQty', self.remaining_quantity))
        
        if exchange_order.get('avgPrice'):
            self.average_price = float(exchange_order['avgPrice'])
            
        if self.status == OrderStatus.FILLED and not self.filled_at:
            self.filled_at = datetime.utcnow()
            
        if self.status == OrderStatus.EXPIRED and not self.expired_at:
            self.expired_at = datetime.utcnow()

    def validate_order(self) -> tuple[bool, str]:
        """
        Validate order parameters.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.symbol:
            return False, "Symbol is required"
            
        if not self.quantity or self.quantity <= 0:
            return False, "Invalid quantity"
            
        if self.type in {OrderType.LIMIT, OrderType.STOP_LIMIT, OrderType.TAKE_PROFIT_LIMIT}:
            if not self.price or self.price <= 0:
                return False, "Price is required for limit orders"
                
        if self.type in {OrderType.STOP_MARKET, OrderType.STOP_LIMIT}:
            if not self.stop_price or self.stop_price <= 0:
                return False, "Stop price is required for stop orders"
                
        return True, ""

    def to_dict(self) -> dict:
        """Convert order to dictionary."""
        return {
            'id': self.id,
            'exchange_order_id': self.exchange_order_id,
            'symbol': self.symbol,
            'side': self.side.value,
            'type': self.type.value,
            'status': self.status.value,
            'price': self.price,
            'stop_price': self.stop_price,
            'average_price': self.average_price,
            'quantity': self.quantity,
            'executed_quantity': self.executed_quantity,
            'remaining_quantity': self.remaining_quantity,
            'time_in_force': self.time_in_force.value,
            'reduce_only': self.reduce_only,
            'close_position': self.close_position,
            'working_type': self.working_type,
            'position_side': self.position_side,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'filled_at': self.filled_at.isoformat() if self.filled_at else None,
            'expired_at': self.expired_at.isoformat() if self.expired_at else None,
            'leverage': self.leverage,
            'isolated': self.isolated,
            'filled_percentage': self.filled_percentage,
            'is_active': self.is_active,
            'is_complete': self.is_complete
        }
from typing import List, Optional, Dict, Any
from decimal import Decimal
import logging
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.order import Order, OrderStatus, OrderType, OrderSide
from app.models.user import User
from app.models.position import Position
from app.schemas.order import OrderCreate, OrderUpdate
from app.core.config import settings
from app.exchanges.binance.futures import BinanceFuturesClient
from app.exchanges.binance.spot import BinanceSpotClient
from app.core.risk.position_sizing import PositionSizingManager

logger = logging.getLogger(__name__)

class OrderManager:
    """
    Service for managing trading orders.
    """
    
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
        self.position_sizing = PositionSizingManager(user)
        
        # Initialize exchange clients
        self.spot_client = BinanceSpotClient(
            api_key=user.binance_api_key,
            api_secret=user.binance_api_secret,
            testnet=settings.BINANCE_TESTNET
        )
        self.futures_client = BinanceFuturesClient(
            api_key=user.binance_api_key,
            api_secret=user.binance_api_secret,
            testnet=settings.BINANCE_TESTNET
        )

    async def create_order(self, order_data: OrderCreate) -> Order:
        """
        Create and execute new order.
        """
        try:
            # Validate order parameters
            await self._validate_order_create(order_data)
            
            # Create order record
            order = Order(
                user_id=self.user.id,
                symbol=order_data.symbol,
                side=order_data.side,
                type=order_data.type,
                quantity=float(order_data.quantity),
                price=float(order_data.price) if order_data.price else None,
                stop_price=float(order_data.stop_price) if order_data.stop_price else None,
                leverage=order_data.leverage,
                reduce_only=order_data.reduce_only,
                close_position=order_data.close_position
            )
            
            # Execute order on exchange
            exchange_order = await self._execute_order_on_exchange(order_data)
            
            # Update order with exchange response
            order.exchange_order_id = exchange_order['orderId']
            order.status = OrderStatus(exchange_order['status'])
            
            if 'executedQty' in exchange_order:
                order.executed_quantity = float(exchange_order['executedQty'])
                
            if 'avgPrice' in exchange_order:
                order.average_price = float(exchange_order['avgPrice'])
            
            # Save order to database
            self.db.add(order)
            self.db.commit()
            self.db.refresh(order)
            
            # Update associated position if needed
            await self._update_position(order)
            
            return order
            
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            self.db.rollback()
            raise

    async def get_order(self, order_id: int) -> Optional[Order]:
        """
        Get order by ID.
        """
        order = self.db.query(Order).filter(
            Order.id == order_id,
            Order.user_id == self.user.id
        ).first()
        
        if order and order.is_active:
            await self._update_order_status(order)
            
        return order

    async def get_orders(
        self,
        symbol: Optional[str] = None,
        status: Optional[OrderStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Order]:
        """
        Get list of orders with filters.
        """
        query = self.db.query(Order).filter(Order.user_id == self.user.id)
        
        if symbol:
            query = query.filter(Order.symbol == symbol)
            
        if status:
            query = query.filter(Order.status == status)
            
        orders = query.order_by(Order.created_at.desc()).offset(offset).limit(limit).all()
        
        # Update status of active orders
        for order in orders:
            if order.is_active:
                await self._update_order_status(order)
                
        return orders

    async def cancel_order(self, order_id: int) -> Order:
        """
        Cancel existing order.
        """
        try:
            order = await self.get_order(order_id)
            if not order:
                raise ValueError(f"Order {order_id} not found")
                
            if not order.is_active:
                raise ValueError(f"Order {order_id} is not active")
                
            # Cancel order on exchange
            if order.leverage:  # Futures order
                response = self.futures_client.cancel_order(
                    symbol=order.symbol,
                    orderId=order.exchange_order_id
                )
            else:  # Spot order
                response = self.spot_client.cancel_order(
                    symbol=order.symbol,
                    orderId=order.exchange_order_id
                )
                
            # Update order status
            order.status = OrderStatus.CANCELED
            self.db.commit()
            
            return order
            
        except Exception as e:
            logger.error(f"Error canceling order: {str(e)}")
            self.db.rollback()
            raise

    async def update_order(self, order_id: int, update_data: OrderUpdate) -> Order:
        """
        Update existing order.
        """
        try:
            order = await self.get_order(order_id)
            if not order:
                raise ValueError(f"Order {order_id} not found")
                
            if not order.is_active:
                raise ValueError(f"Order {order_id} is not active")
                
            # Cancel existing order
            await self.cancel_order(order_id)
            
            # Create new order with updated parameters
            new_order_data = OrderCreate(
                symbol=order.symbol,
                side=order.side,
                type=order.type,
                quantity=update_data.quantity or order.quantity,
                price=update_data.price or order.price,
                stop_price=update_data.stop_price or order.stop_price,
                leverage=order.leverage,
                reduce_only=order.reduce_only,
                close_position=order.close_position
            )
            
            return await self.create_order(new_order_data)
            
        except Exception as e:
            logger.error(f"Error updating order: {str(e)}")
            self.db.rollback()
            raise

    async def _validate_order_create(self, order_data: OrderCreate) -> None:
        """
        Validate order creation parameters.
        """
        # Validate symbol
        if order_data.leverage:  # Futures
            symbol_info = self.futures_client.get_symbol_info(order_data.symbol)
        else:  # Spot
            symbol_info = self.spot_client.get_symbol_info(order_data.symbol)
            
        if not symbol_info:
            raise ValueError(f"Invalid symbol: {order_data.symbol}")
            
        # Validate quantity
        min_qty = float(symbol_info['minQty'])
        max_qty = float(symbol_info['maxQty'])
        step_size = float(symbol_info['stepSize'])
        
        if not (min_qty <= order_data.quantity <= max_qty):
            raise ValueError(f"Quantity must be between {min_qty} and {max_qty}")
            
        # Validate price for limit orders
        if order_data.type in [OrderType.LIMIT, OrderType.STOP_LIMIT]:
            min_price = float(symbol_info['minPrice'])
            max_price = float(symbol_info['maxPrice'])
            tick_size = float(symbol_info['tickSize'])
            
            if not (min_price <= order_data.price <= max_price):
                raise ValueError(f"Price must be between {min_price} and {max_price}")
                
        # Validate leverage for futures
        if order_data.leverage:
            max_leverage = symbol_info.get('maxLeverage', 125)
            if not (1 <= order_data.leverage <= max_leverage):
                raise ValueError(f"Leverage must be between 1 and {max_leverage}")

    async def _execute_order_on_exchange(self, order_data: OrderCreate) -> Dict:
        """
        Execute order on appropriate exchange.
        """
        params = {
            'symbol': order_data.symbol,
            'side': order_data.side.value,
            'type': order_data.type.value,
            'quantity': float(order_data.quantity)
        }
        
        if order_data.price:
            params['price'] = float(order_data.price)
            
        if order_data.stop_price:
            params['stopPrice'] = float(order_data.stop_price)
            
        if order_data.leverage:  # Futures order
            params['leverage'] = order_data.leverage
            return self.futures_client.create_order(**params)
        else:  # Spot order
            return self.spot_client.create_order(**params)

    async def _update_order_status(self, order: Order) -> None:
        """
        Update order status from exchange.
        """
        try:
            if order.leverage:  # Futures order
                exchange_order = self.futures_client.get_order(
                    symbol=order.symbol,
                    orderId=order.exchange_order_id
                )
            else:  # Spot order
                exchange_order = self.spot_client.get_order(
                    symbol=order.symbol,
                    orderId=order.exchange_order_id
                )
                
            order.status = OrderStatus(exchange_order['status'])
            order.executed_quantity = float(exchange_order.get('executedQty', 0))
            
            if 'avgPrice' in exchange_order:
                order.average_price = float(exchange_order['avgPrice'])
                
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error updating order status: {str(e)}")

    async def _update_position(self, order: Order) -> None:
        """
        Update or create position based on order execution.
        """
        if not order.leverage or order.status != OrderStatus.FILLED:
            return
            
        try:
            position = self.db.query(Position).filter(
                Position.user_id == self.user.id,
                Position.symbol == order.symbol,
                Position.status == 'OPEN'
            ).first()
            
            if order.side == OrderSide.BUY:
                if position:
                    position.size += order.executed_quantity
                    position.entry_price = (
                        (position.entry_price * (position.size - order.executed_quantity) +
                         order.average_price * order.executed_quantity) / position.size
                    )
                else:
                    position = Position(
                        user_id=self.user.id,
                        symbol=order.symbol,
                        side='LONG',
                        entry_price=order.average_price,
                        size=order.executed_quantity,
                        leverage=order.leverage
                    )
                    self.db.add(position)
            else:  # SELL
                if position:
                    position.size -= order.executed_quantity
                    if position.size <= 0:
                        position.status = 'CLOSED'
                else:
                    position = Position(
                        user_id=self.user.id,
                        symbol=order.symbol,
                        side='SHORT',
                        entry_price=order.average_price,
                        size=order.executed_quantity,
                        leverage=order.leverage
                    )
                    self.db.add(position)
                    
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error updating position: {str(e)}")
            raise
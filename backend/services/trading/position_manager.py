from typing import List, Optional, Dict, Any
from decimal import Decimal
import logging
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.position import Position, PositionStatus, PositionSide, MarginType
from app.models.user import User
from app.models.order import Order, OrderType, OrderSide
from app.schemas.position import PositionCreate, PositionUpdate
from app.core.config import settings
from app.exchanges.binance.futures import BinanceFuturesClient
from app.core.risk.position_sizing import PositionSizingManager
from app.core.risk.risk_management import RiskManager

logger = logging.getLogger(__name__)

class PositionManager:
    """
    Service for managing trading positions.
    """
    
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
        self.position_sizing = PositionSizingManager(user)
        self.risk_manager = RiskManager(user)
        
        # Initialize futures client
        self.futures_client = BinanceFuturesClient(
            api_key=user.binance_api_key,
            api_secret=user.binance_api_secret,
            testnet=settings.BINANCE_TESTNET
        )

    async def get_positions(
        self,
        symbol: Optional[str] = None,
        status: Optional[PositionStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Position]:
        """
        Get list of positions with filters.
        """
        query = self.db.query(Position).filter(Position.user_id == self.user.id)
        
        if symbol:
            query = query.filter(Position.symbol == symbol)
            
        if status:
            query = query.filter(Position.status == status)
            
        positions = query.order_by(Position.opened_at.desc()).offset(offset).limit(limit).all()
        
        # Update positions with latest market data
        for position in positions:
            if position.status == PositionStatus.OPEN:
                await self._update_position_market_data(position)
                
        return positions

    async def get_position(self, position_id: int) -> Optional[Position]:
        """
        Get position by ID.
        """
        position = self.db.query(Position).filter(
            Position.id == position_id,
            Position.user_id == self.user.id
        ).first()
        
        if position and position.status == PositionStatus.OPEN:
            await self._update_position_market_data(position)
            
        return position

    async def create_position(self, position_data: PositionCreate) -> Position:
        """
        Create new position.
        """
        try:
            # Validate position parameters
            await self._validate_position_create(position_data)
            
            # Check risk limits
            account_info = self.futures_client.get_account_info()
            available_balance = float(account_info['availableBalance'])
            
            is_valid, reason = self.risk_manager.validate_new_position(
                symbol=position_data.symbol,
                size=position_data.size,
                leverage=position_data.leverage,
                account_balance=available_balance
            )
            
            if not is_valid:
                raise ValueError(f"Position validation failed: {reason}")
            
            # Set leverage on exchange
            self.futures_client.change_leverage(
                symbol=position_data.symbol,
                leverage=position_data.leverage
            )
            
            # Set margin type if specified
            if position_data.margin_type:
                self.futures_client.change_margin_type(
                    symbol=position_data.symbol,
                    marginType=position_data.margin_type.value
                )
            
            # Create position record
            position = Position(
                user_id=self.user.id,
                symbol=position_data.symbol,
                side=position_data.side,
                entry_price=float(position_data.entry_price),
                size=float(position_data.size),
                leverage=position_data.leverage,
                margin_type=position_data.margin_type or MarginType.CROSSED,
                stop_loss=position_data.stop_loss,
                take_profit=position_data.take_profit,
                trailing_stop=position_data.trailing_stop
            )
            
            self.db.add(position)
            self.db.commit()
            self.db.refresh(position)
            
            # Place entry order
            order_side = OrderSide.BUY if position.side == PositionSide.LONG else OrderSide.SELL
            entry_order = await self._place_order(
                symbol=position.symbol,
                side=order_side,
                order_type=OrderType.MARKET,
                quantity=position.size,
                leverage=position.leverage
            )
            
            # Place stop loss order if specified
            if position.stop_loss:
                await self._place_stop_loss_order(position)
                
            # Place take profit order if specified
            if position.take_profit:
                await self._place_take_profit_order(position)
                
            return position
            
        except Exception as e:
            logger.error(f"Error creating position: {str(e)}")
            self.db.rollback()
            raise

    async def update_position(self, position_id: int, update_data: PositionUpdate) -> Position:
        """
        Update position parameters.
        """
        try:
            position = await self.get_position(position_id)
            if not position:
                raise ValueError(f"Position {position_id} not found")
                
            if position.status != PositionStatus.OPEN:
                raise ValueError(f"Position {position_id} is not open")
                
            # Update stop loss
            if update_data.stop_loss is not None and update_data.stop_loss != position.stop_loss:
                await self._update_stop_loss(position, update_data.stop_loss)
                
            # Update take profit
            if update_data.take_profit is not None and update_data.take_profit != position.take_profit:
                await self._update_take_profit(position, update_data.take_profit)
                
            # Update trailing stop
            if update_data.trailing_stop is not None and update_data.trailing_stop != position.trailing_stop:
                await self._update_trailing_stop(position, update_data.trailing_stop)
                
            self.db.commit()
            return position
            
        except Exception as e:
            logger.error(f"Error updating position: {str(e)}")
            self.db.rollback()
            raise

    async def close_position(self, position_id: int, market_price: bool = True) -> Position:
        """
        Close existing position.
        """
        try:
            position = await self.get_position(position_id)
            if not position:
                raise ValueError(f"Position {position_id} not found")
                
            if position.status != PositionStatus.OPEN:
                raise ValueError(f"Position {position_id} is not open")
            
            # Cancel all existing orders
            await self._cancel_position_orders(position)
            
            # Place closing order
            order_side = OrderSide.SELL if position.side == PositionSide.LONG else OrderSide.BUY
            close_order = await self._place_order(
                symbol=position.symbol,
                side=order_side,
                order_type=OrderType.MARKET if market_price else OrderType.LIMIT,
                quantity=position.size,
                leverage=position.leverage,
                reduce_only=True
            )
            
            # Update position status
            position.status = PositionStatus.CLOSED
            position.closed_at = datetime.utcnow()
            
            # Calculate final PnL
            await self._update_position_market_data(position)
            position.realized_pnl = position.unrealized_pnl
            position.unrealized_pnl = 0
            
            self.db.commit()
            return position
            
        except Exception as e:
            logger.error(f"Error closing position: {str(e)}")
            self.db.rollback()
            raise

    async def _validate_position_create(self, position_data: PositionCreate) -> None:
        """
        Validate position creation parameters.
        """
        # Validate symbol
        symbol_info = self.futures_client.get_symbol_info(position_data.symbol)
        if not symbol_info:
            raise ValueError(f"Invalid symbol: {position_data.symbol}")
            
        # Validate size
        min_qty = float(symbol_info['minQty'])
        max_qty = float(symbol_info['maxQty'])
        
        if not (min_qty <= position_data.size <= max_qty):
            raise ValueError(f"Position size must be between {min_qty} and {max_qty}")
            
        # Validate leverage
        max_leverage = symbol_info.get('maxLeverage', 125)
        if not (1 <= position_data.leverage <= max_leverage):
            raise ValueError(f"Leverage must be between 1 and {max_leverage}")
            
        # Validate stop loss
        if position_data.stop_loss:
            if position_data.side == PositionSide.LONG and position_data.stop_loss >= position_data.entry_price:
                raise ValueError("Stop loss must be below entry price for long positions")
            elif position_data.side == PositionSide.SHORT and position_data.stop_loss <= position_data.entry_price:
                raise ValueError("Stop loss must be above entry price for short positions")
                
        # Validate take profit
        if position_data.take_profit:
            if position_data.side == PositionSide.LONG and position_data.take_profit <= position_data.entry_price:
                raise ValueError("Take profit must be above entry price for long positions")
            elif position_data.side == PositionSide.SHORT and position_data.take_profit >= position_data.entry_price:
                raise ValueError("Take profit must be below entry price for short positions")

    async def _update_position_market_data(self, position: Position) -> None:
        """
        Update position with latest market data.
        """
        try:
            # Get mark price
            mark_price_info = self.futures_client.get_mark_price(position.symbol)
            position.mark_price = float(mark_price_info['markPrice'])
            
            # Update PnL calculations
            position.update_pnl()
            
            # Get liquidation price
            position_info = self.futures_client.get_position_info(position.symbol)
            position.liquidation_price = float(position_info['liquidationPrice'])
            position.margin_ratio = float(position_info['marginRatio'])
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error updating position market data: {str(e)}")

    async def _place_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: float,
        leverage: int,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        reduce_only: bool = False
    ) -> Dict[str, Any]:
        """
        Place order on exchange.
        """
        params = {
            'symbol': symbol,
            'side': side.value,
            'type': order_type.value,
            'quantity': quantity,
            'leverage': leverage,
            'reduceOnly': reduce_only
        }
        
        if price:
            params['price'] = price
            
        if stop_price:
            params['stopPrice'] = stop_price
            
        return self.futures_client.create_order(**params)

    async def _place_stop_loss_order(self, position: Position) -> None:
        """
        Place stop loss order for position.
        """
        order_side = OrderSide.SELL if position.side == PositionSide.LONG else OrderSide.BUY
        await self._place_order(
            symbol=position.symbol,
            side=order_side,
            order_type=OrderType.STOP_MARKET,
            quantity=position.size,
            leverage=position.leverage,
            stop_price=position.stop_loss,
            reduce_only=True
        )

    async def _place_take_profit_order(self, position: Position) -> None:
        """
        Place take profit order for position.
        """
        order_side = OrderSide.SELL if position.side == PositionSide.LONG else OrderSide.BUY
        await self._place_order(
            symbol=position.symbol,
            side=order_side,
            order_type=OrderType.TAKE_PROFIT_MARKET,
            quantity=position.size,
            leverage=position.leverage,
            stop_price=position.take_profit,
            reduce_only=True
        )

    async def _update_stop_loss(self, position: Position, new_stop_loss: float) -> None:
        """
        Update position's stop loss order.
        """
        # Cancel existing stop loss order
        await self._cancel_position_orders(position, order_type=OrderType.STOP_MARKET)
        
        # Update position stop loss
        position.stop_loss = new_stop_loss
        
        # Place new stop loss order
        if position.status == PositionStatus.OPEN:
            await self._place_stop_loss_order(position)

    async def _update_take_profit(self, position: Position, new_take_profit: float) -> None:
        """
        Update position's take profit order.
        """
        # Cancel existing take profit order
        await self._cancel_position_orders(position, order_type=OrderType.TAKE_PROFIT_MARKET)
        
        # Update position take profit
        position.take_profit = new_take_profit
        
        # Place new take profit order
        if position.status == PositionStatus.OPEN:
            await self._place_take_profit_order(position)

    async def _update_trailing_stop(self, position: Position, new_trailing_stop: float) -> None:
        """
        Update position's trailing stop.
        """
        position.trailing_stop = new_trailing_stop
        
        # Implement trailing stop logic here
        # This might involve monitoring price movements and adjusting stop loss accordingly

    async def _cancel_position_orders(
        self,
        position: Position,
        order_type: Optional[OrderType] = None
    ) -> None:
        """
        Cancel orders associated with position.
        """
        orders = self.db.query(Order).filter(
            Order.position_id == position.id,
            Order.status.in_(['NEW', 'PARTIALLY_FILLED'])
        )
        
        if order_type:
            orders = orders.filter(Order.type == order_type)
            
        for order in orders:
            self.futures_client.cancel_order(
                symbol=position.symbol,
                orderId=order.exchange_order_id
            )
            order.status = 'CANCELED'
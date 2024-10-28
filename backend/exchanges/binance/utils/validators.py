from decimal import Decimal
from typing import Dict, Any, Optional, List
import re
import logging

logger = logging.getLogger(__name__)

class BinanceValidators:
    """
    Validation utilities for Binance API interactions.
    """
    
    # Compiled regex patterns
    SYMBOL_PATTERN = re.compile(r'^[A-Z0-9]{2,20}$')
    ORDER_ID_PATTERN = re.compile(r'^[0-9]{1,20}$')
    TIMESTAMP_PATTERN = re.compile(r'^[0-9]{13}$')

    @classmethod
    def validate_symbol(cls, symbol: str) -> bool:
        """
        Validate trading pair symbol format.
        """
        if not symbol:
            return False
        return bool(cls.SYMBOL_PATTERN.match(symbol))

    @classmethod
    def validate_order_params(cls, params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate order parameters.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = {'symbol', 'side', 'type', 'quantity'}
        
        # Check required fields
        missing_fields = required_fields - set(params.keys())
        if missing_fields:
            return False, f"Missing required fields: {missing_fields}"
            
        # Validate symbol
        if not cls.validate_symbol(params['symbol']):
            return False, "Invalid symbol format"
            
        # Validate side
        if params['side'].upper() not in {'BUY', 'SELL'}:
            return False, "Invalid order side"
            
        # Validate order type
        if params['type'].upper() not in {'LIMIT', 'MARKET', 'STOP', 'STOP_MARKET',
                                        'TAKE_PROFIT', 'TAKE_PROFIT_MARKET'}:
            return False, "Invalid order type"
            
        # Validate quantity
        try:
            quantity = Decimal(str(params['quantity']))
            if quantity <= 0:
                return False, "Quantity must be positive"
        except:
            return False, "Invalid quantity format"
            
        # Validate price for limit orders
        if params['type'].upper() == 'LIMIT' and 'price' not in params:
            return False, "Price required for LIMIT orders"
            
        return True, None

    @classmethod
    def validate_position_params(cls, params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate position parameters.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = {'symbol', 'leverage'}
        
        # Check required fields
        missing_fields = required_fields - set(params.keys())
        if missing_fields:
            return False, f"Missing required fields: {missing_fields}"
            
        # Validate symbol
        if not cls.validate_symbol(params['symbol']):
            return False, "Invalid symbol format"
            
        # Validate leverage
        try:
            leverage = int(params['leverage'])
            if leverage < 1 or leverage > 125:
                return False, "Leverage must be between 1 and 125"
        except:
            return False, "Invalid leverage format"
            
        return True, None

    @staticmethod
    def validate_quantity_precision(
        quantity: Decimal,
        step_size: Decimal
    ) -> tuple[bool, Optional[Decimal]]:
        """
        Validate and adjust quantity precision.
        
        Returns:
            Tuple of (is_valid, adjusted_quantity)
        """
        try:
            # Calculate precision from step size
            precision = abs(Decimal(str(step_size)).as_tuple().exponent)
            
            # Round quantity to valid precision
            adjusted_quantity = round(quantity, precision)
            
            # Check if quantity is multiple of step size
            remainder = adjusted_quantity % step_size
            is_valid = remainder == 0
            
            return is_valid, adjusted_quantity
        except Exception as e:
            logger.error(f"Error validating quantity precision: {str(e)}")
            return False, None

    @staticmethod
    def validate_price_precision(
        price: Decimal,
        tick_size: Decimal
    ) -> tuple[bool, Optional[Decimal]]:
        """
        Validate and adjust price precision.
        
        Returns:
            Tuple of (is_valid, adjusted_price)
        """
        try:
            # Calculate precision from tick size
            precision = abs(Decimal(str(tick_size)).as_tuple().exponent)
            
            # Round price to valid precision
            adjusted_price = round(price, precision)
            
            # Check if price is multiple of tick size
            remainder = adjusted_price % tick_size
            is_valid = remainder == 0
            
            return is_valid, adjusted_price
        except Exception as e:
            logger.error(f"Error validating price precision: {str(e)}")
            return False, None

    @staticmethod
    def validate_stop_price(
        stop_price: Decimal,
        current_price: Decimal,
        direction: str
    ) -> bool:
        """
        Validate stop price relative to current price and direction.
        """
        if direction.upper() == 'BUY':
            return stop_price > current_price
        else:  # SELL
            return stop_price < current_price

    @staticmethod
    def validate_leverage(leverage: int, max_leverage: int) -> bool:
        """
        Validate leverage value.
        """
        return 1 <= leverage <= max_leverage

    @staticmethod
    def validate_margin_type(margin_type: str) -> bool:
        """
        Validate margin type.
        """
        return margin_type.upper() in {'ISOLATED', 'CROSSED'}

    @staticmethod
    def validate_position_side(position_side: str) -> bool:
        """
        Validate position side.
        """
        return position_side.upper() in {'LONG', 'SHORT', 'BOTH'}

    @classmethod
    def validate_order_id(cls, order_id: str) -> bool:
        """
        Validate order ID format.
        """
        if not order_id:
            return False
        return bool(cls.ORDER_ID_PATTERN.match(order_id))

    @classmethod
    def validate_timestamp(cls, timestamp: str) -> bool:
        """
        Validate timestamp format.
        """
        if not timestamp:
            return False
        return bool(cls.TIMESTAMP_PATTERN.match(timestamp))

    @staticmethod
    def validate_time_in_force(time_in_force: str) -> bool:
        """
        Validate time in force parameter.
        """
        return time_in_force.upper() in {'GTC', 'IOC', 'FOK'}

    @staticmethod
    def validate_working_type(working_type: str) -> bool:
        """
        Validate working type parameter.
        """
        return working_type.upper() in {'MARK_PRICE', 'CONTRACT_PRICE'}

    @staticmethod
    def validate_position_risk(
        position_size: Decimal,
        account_balance: Decimal,
        max_position_ratio: Decimal
    ) -> bool:
        """
        Validate position size against account balance.
        """
        max_position_size = account_balance * max_position_ratio
        return position_size <= max_position_size
from typing import Dict, Optional, List
from decimal import Decimal
import logging
from binance.um_futures import UMFutures
from binance.error import ClientError

from app.core.config import settings
from app.core.security import SecurityService
from app.schemas.order import OrderCreate
from app.schemas.position import PositionUpdate

logger = logging.getLogger(__name__)

class BinanceFuturesClient:
    """
    Binance USD-M Futures trading client implementation.
    """
    
    def __init__(
        self,
        api_key: str = settings.BINANCE_API_KEY,
        api_secret: str = settings.BINANCE_API_SECRET,
        testnet: bool = settings.BINANCE_TESTNET
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        
        # Initialize Binance client
        self.client = UMFutures(
            key=api_key,
            secret=api_secret,
            base_url="https://testnet.binancefuture.com" if testnet else None
        )
        
        # Initialize security service
        self.security = SecurityService()

    def get_account_info(self) -> Dict:
        """
        Get futures account information.
        """
        try:
            return self.client.account()
        except ClientError as e:
            logger.error(f"Failed to get account info: {str(e)}")
            raise

    def get_position_risk(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Get position risk information.
        """
        try:
            params = {'symbol': symbol} if symbol else {}
            return self.client.get_position_risk(**params)
        except ClientError as e:
            logger.error(f"Failed to get position risk: {str(e)}")
            raise

    def create_order(self, order: OrderCreate) -> Dict:
        """
        Create new futures order.
        """
        try:
            params = {
                'symbol': order.symbol,
                'side': order.side.upper(),
                'type': order.type.upper(),
                'quantity': float(order.quantity)
            }
            
            if order.price:
                params['price'] = float(order.price)
            
            if order.stop_price:
                params['stopPrice'] = float(order.stop_price)
                
            if order.reduce_only:
                params['reduceOnly'] = order.reduce_only
                
            if order.close_position:
                params['closePosition'] = order.close_position
                
            if order.leverage:
                # Set leverage before placing order
                self.change_leverage(order.symbol, order.leverage)
                
            return self.client.new_order(**params)
        except ClientError as e:
            logger.error(f"Failed to create futures order: {str(e)}")
            raise

    def change_leverage(self, symbol: str, leverage: int) -> Dict:
        """
        Change leverage for symbol.
        """
        try:
            return self.client.change_leverage(
                symbol=symbol,
                leverage=leverage
            )
        except ClientError as e:
            logger.error(f"Failed to change leverage for {symbol}: {str(e)}")
            raise

    def change_margin_type(self, symbol: str, margin_type: str) -> Dict:
        """
        Change margin type (ISOLATED or CROSSED).
        """
        try:
            return self.client.change_margin_type(
                symbol=symbol,
                marginType=margin_type.upper()
            )
        except ClientError as e:
            logger.error(f"Failed to change margin type for {symbol}: {str(e)}")
            raise

    def get_open_positions(self) -> List[Dict]:
        """
        Get all open positions.
        """
        try:
            positions = self.client.get_position_risk()
            return [p for p in positions if float(p['positionAmt']) != 0]
        except ClientError as e:
            logger.error(f"Failed to get open positions: {str(e)}")
            raise

    def get_position(self, symbol: str) -> Optional[Dict]:
        """
        Get position information for symbol.
        """
        try:
            positions = self.client.get_position_risk(symbol=symbol)
            return positions[0] if positions else None
        except ClientError as e:
            logger.error(f"Failed to get position for {symbol}: {str(e)}")
            raise

    def update_position_margin(
        self,
        symbol: str,
        amount: Decimal,
        type: int  # 1: Add, 2: Reduce
    ) -> Dict:
        """
        Update position margin.
        """
        try:
            return self.client.modify_isolated_position_margin(
                symbol=symbol,
                amount=float(amount),
                type=type
            )
        except ClientError as e:
            logger.error(f"Failed to update position margin: {str(e)}")
            raise

    def set_position_mode(self, dual_side_position: bool = False) -> Dict:
        """
        Set position mode (Hedge Mode or One-way Mode).
        """
        try:
            return self.client.change_position_mode(
                dualSidePosition=dual_side_position
            )
        except ClientError as e:
            logger.error(f"Failed to set position mode: {str(e)}")
            raise

    def get_income_history(
        self,
        symbol: Optional[str] = None,
        income_type: Optional[str] = None,
        limit: int = 500
    ) -> List[Dict]:
        """
        Get income history (realized PnL, funding fees, etc.).
        """
        try:
            params = {'limit': limit}
            if symbol:
                params['symbol'] = symbol
            if income_type:
                params['incomeType'] = income_type
            return self.client.get_income_history(**params)
        except ClientError as e:
            logger.error(f"Failed to get income history: {str(e)}")
            raise

    def get_mark_price(self, symbol: str) -> Dict:
        """
        Get mark price and funding rate.
        """
        try:
            return self.client.mark_price(symbol=symbol)
        except ClientError as e:
            logger.error(f"Failed to get mark price for {symbol}: {str(e)}")
            raise

    def get_funding_rate(self, symbol: str) -> Dict:
        """
        Get funding rate history.
        """
        try:
            return self.client.funding_rate(symbol=symbol)
        except ClientError as e:
            logger.error(f"Failed to get funding rate for {symbol}: {str(e)}")
            raise

    def get_ticker(self, symbol: str) -> Dict:
        """
        Get 24hr ticker price change statistics.
        """
        try:
            return self.client.ticker_24hr_price_change(symbol=symbol)
        except ClientError as e:
            logger.error(f"Failed to get ticker for {symbol}: {str(e)}")
            raise

    def cancel_all_open_orders(self, symbol: str) -> Dict:
        """
        Cancel all open orders for a symbol.
        """
        try:
            return self.client.cancel_open_orders(symbol=symbol)
        except ClientError as e:
            logger.error(f"Failed to cancel orders for {symbol}: {str(e)}")
            raise

    def set_hedge_mode(self, symbol: str) -> Dict:
        """
        Enable hedge mode for a symbol.
        """
        try:
            return self.set_position_mode(True)
        except ClientError as e:
            logger.error(f"Failed to set hedge mode: {str(e)}")
            raise

    async def auto_reduce_margin(self, symbol: str, target_margin_ratio: Decimal = Decimal('0.1')):
        """
        Automatically reduce margin to maintain target margin ratio.
        """
        try:
            position = self.get_position(symbol)
            if not position:
                return
                
            current_margin_ratio = Decimal(position['marginRatio'])
            if current_margin_ratio > target_margin_ratio:
                # Calculate required margin reduction
                excess_margin = (current_margin_ratio - target_margin_ratio) * Decimal(position['isolatedWallet'])
                if excess_margin > 0:
                    self.update_position_margin(symbol, excess_margin, 2)  # Reduce margin
                    
        except Exception as e:
            logger.error(f"Failed to auto-reduce margin: {str(e)}")
            raise
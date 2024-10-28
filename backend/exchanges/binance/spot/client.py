from typing import Dict, Optional, List
from decimal import Decimal
import logging
from binance.spot import Spot as BinanceSpot
from binance.error import ClientError

from app.core.config import settings
from app.core.security import SecurityService
from app.schemas.order import OrderCreate

logger = logging.getLogger(__name__)

class BinanceSpotClient:
    """
    Binance Spot trading client implementation.
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
        self.client = BinanceSpot(
            api_key=api_key,
            api_secret=api_secret,
            base_url="https://testnet.binance.vision/api" if testnet else None
        )
        
        # Initialize security service
        self.security = SecurityService()

    def get_account_info(self) -> Dict:
        """
        Get account information.
        """
        try:
            return self.client.account()
        except ClientError as e:
            logger.error(f"Failed to get account info: {str(e)}")
            raise

    def get_asset_balance(self, asset: str) -> Decimal:
        """
        Get specific asset balance.
        """
        try:
            account = self.client.account()
            for balance in account['balances']:
                if balance['asset'] == asset:
                    return Decimal(balance['free'])
            return Decimal('0')
        except ClientError as e:
            logger.error(f"Failed to get {asset} balance: {str(e)}")
            raise

    def create_order(self, order: OrderCreate) -> Dict:
        """
        Create new order.
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
                
            return self.client.new_order(**params)
        except ClientError as e:
            logger.error(f"Failed to create order: {str(e)}")
            raise

    def cancel_order(self, symbol: str, order_id: int) -> Dict:
        """
        Cancel existing order.
        """
        try:
            return self.client.cancel_order(symbol=symbol, orderId=order_id)
        except ClientError as e:
            logger.error(f"Failed to cancel order {order_id}: {str(e)}")
            raise

    def get_order(self, symbol: str, order_id: int) -> Dict:
        """
        Get order status.
        """
        try:
            return self.client.get_order(symbol=symbol, orderId=order_id)
        except ClientError as e:
            logger.error(f"Failed to get order {order_id}: {str(e)}")
            raise

    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Get all open orders.
        """
        try:
            params = {'symbol': symbol} if symbol else {}
            return self.client.get_open_orders(**params)
        except ClientError as e:
            logger.error(f"Failed to get open orders: {str(e)}")
            raise

    def get_all_orders(
        self,
        symbol: str,
        limit: int = 500,
        from_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Get all account orders.
        """
        try:
            params = {
                'symbol': symbol,
                'limit': limit
            }
            if from_id:
                params['orderId'] = from_id
            return self.client.get_all_orders(**params)
        except ClientError as e:
            logger.error(f"Failed to get all orders: {str(e)}")
            raise

    def get_ticker_price(self, symbol: str) -> Decimal:
        """
        Get current price for a symbol.
        """
        try:
            ticker = self.client.ticker_price(symbol=symbol)
            return Decimal(ticker['price'])
        except ClientError as e:
            logger.error(f"Failed to get ticker price for {symbol}: {str(e)}")
            raise

    def get_exchange_info(self, symbol: Optional[str] = None) -> Dict:
        """
        Get exchange trading rules and symbol information.
        """
        try:
            params = {'symbol': symbol} if symbol else {}
            return self.client.exchange_info(**params)
        except ClientError as e:
            logger.error(f"Failed to get exchange info: {str(e)}")
            raise

    def get_24h_ticker(self, symbol: str) -> Dict:
        """
        Get 24 hour price change statistics.
        """
        try:
            return self.client.ticker_24hr(symbol=symbol)
        except ClientError as e:
            logger.error(f"Failed to get 24h ticker for {symbol}: {str(e)}")
            raise

    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate if trading pair exists.
        """
        try:
            info = self.get_exchange_info(symbol)
            return bool(info.get('symbols', []))
        except:
            return False
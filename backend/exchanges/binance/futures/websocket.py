import json
import logging
import asyncio
from typing import Dict, Optional, List, Callable, Any
import websockets
from websockets.exceptions import ConnectionClosed
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)

class BinanceFuturesWebSocket:
    """
    Binance USD-M Futures WebSocket client for real-time market data and user data streaming.
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
        
        # Initialize WebSocket URLs
        self.base_url = (
            "wss://fstream.binancefuture.com/ws"
            if not testnet else
            "wss://stream.binancefuture.com/ws"
        )
        self.user_stream_url = (
            "wss://fstream.binancefuture.com/ws"
            if not testnet else
            "wss://stream.binancefuture.com/ws"
        )
        
        self.websocket = None
        self.user_websocket = None
        self.running = False
        self.callbacks: Dict[str, List[Callable]] = {}
        self.listen_key: Optional[str] = None
        self.last_heartbeat: datetime = datetime.now()
        self.heartbeat_interval = 30  # seconds
        self.reconnect_delay = 5  # seconds

    async def connect(self):
        """
        Establish WebSocket connections for market and user data.
        """
        try:
            # Connect to market data stream
            self.websocket = await websockets.connect(self.base_url)
            
            # Initialize user stream if API credentials are provided
            if self.api_key and self.api_secret:
                await self._init_user_stream()
            
            self.running = True
            logger.info("WebSocket connections established")
            
            # Start message handlers and heartbeat
            await asyncio.gather(
                self._handle_market_messages(),
                self._handle_user_messages(),
                self._heartbeat_loop()
            )
            
        except Exception as e:
            logger.error(f"WebSocket connection failed: {str(e)}")
            await self.reconnect()

    async def _init_user_stream(self):
        """
        Initialize user data stream.
        """
        try:
            # Get listen key for user stream
            self.listen_key = await self._get_listen_key()
            
            # Connect to user stream
            user_stream_endpoint = f"{self.user_stream_url}/{self.listen_key}"
            self.user_websocket = await websockets.connect(user_stream_endpoint)
            
            logger.info("User data stream initialized")
        except Exception as e:
            logger.error(f"Failed to initialize user stream: {str(e)}")
            raise

    async def subscribe_market_stream(self, stream: str, callback: Callable):
        """
        Subscribe to a market data stream.
        """
        if stream not in self.callbacks:
            self.callbacks[stream] = []
        
        self.callbacks[stream].append(callback)
        
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": [stream],
            "id": len(self.callbacks)
        }
        
        await self._send_message(subscribe_message)
        logger.info(f"Subscribed to market stream: {stream}")

    async def subscribe_user_stream(self, callback: Callable):
        """
        Subscribe to user data stream updates.
        """
        if 'user_stream' not in self.callbacks:
            self.callbacks['user_stream'] = []
        
        self.callbacks['user_stream'].append(callback)
        logger.info("Subscribed to user data stream")

    async def _send_message(self, message: Dict):
        """
        Send message to WebSocket server.
        """
        if self.websocket:
            try:
                await self.websocket.send(json.dumps(message))
            except ConnectionClosed:
                logger.error("WebSocket connection closed while sending message")
                await self.reconnect()
            except Exception as e:
                logger.error(f"Failed to send message: {str(e)}")

    async def _handle_market_messages(self):
        """
        Handle incoming market data messages.
        """
        while self.running:
            try:
                if not self.websocket:
                    await asyncio.sleep(1)
                    continue

                message = await self.websocket.recv()
                data = json.loads(message)
                
                # Handle stream data
                stream = data.get('stream')
                if stream and stream in self.callbacks:
                    for callback in self.callbacks[stream]:
                        await callback(data['data'])
                        
            except ConnectionClosed:
                logger.error("Market data WebSocket connection closed")
                await self.reconnect()
            except Exception as e:
                logger.error(f"Error handling market message: {str(e)}")
                await asyncio.sleep(1)

    async def _handle_user_messages(self):
        """
        Handle incoming user data messages.
        """
        while self.running and self.user_websocket:
            try:
                message = await self.user_websocket.recv()
                data = json.loads(message)
                
                # Process user data updates
                if 'user_stream' in self.callbacks:
                    for callback in self.callbacks['user_stream']:
                        await callback(data)
                        
            except ConnectionClosed:
                logger.error("User data WebSocket connection closed")
                await self._init_user_stream()
            except Exception as e:
                logger.error(f"Error handling user message: {str(e)}")
                await asyncio.sleep(1)

    async def _heartbeat_loop(self):
        """
        Maintain WebSocket connection with periodic heartbeats.
        """
        while self.running:
            try:
                if self.listen_key:
                    # Send heartbeat every 30 minutes
                    if (datetime.now() - self.last_heartbeat).seconds > 1800:
                        await self._ping_user_stream()
                        self.last_heartbeat = datetime.now()
                
                await asyncio.sleep(self.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"Heartbeat error: {str(e)}")
                await asyncio.sleep(1)

    async def reconnect(self):
        """
        Reconnect WebSocket connections.
        """
        logger.info(f"Attempting to reconnect in {self.reconnect_delay} seconds...")
        self.running = False
        
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            
        if self.user_websocket:
            await self.user_websocket.close()
            self.user_websocket = None
            
        await asyncio.sleep(self.reconnect_delay)
        await self.connect()

    @staticmethod
    def get_aggTrade_stream(symbol: str) -> str:
        """Get aggregated trade stream name."""
        return f"{symbol.lower()}@aggTrade"

    @staticmethod
    def get_markPrice_stream(symbol: str) -> str:
        """Get mark price stream name."""
        return f"{symbol.lower()}@markPrice"

    @staticmethod
    def get_kline_stream(symbol: str, interval: str) -> str:
        """Get kline/candlestick stream name."""
        return f"{symbol.lower()}@kline_{interval}"

    @staticmethod
    def get_continuous_kline_stream(
        pair: str,
        contract_type: str,
        interval: str
    ) -> str:
        """Get continuous contract kline/candlestick stream name."""
        return f"{pair.lower()}_{contract_type}@continuousKline_{interval}"

    @staticmethod
    def get_miniTicker_stream(symbol: str = None) -> str:
        """Get individual symbol or all market mini-tickers stream name."""
        return f"!miniTicker@arr" if not symbol else f"{symbol.lower()}@miniTicker"

    @staticmethod
    def get_ticker_stream(symbol: str = None) -> str:
        """Get individual symbol or all market tickers stream name."""
        return f"!ticker@arr" if not symbol else f"{symbol.lower()}@ticker"

    @staticmethod
    def get_bookTicker_stream(symbol: str = None) -> str:
        """Get individual symbol or all book tickers stream name."""
        return f"!bookTicker" if not symbol else f"{symbol.lower()}@bookTicker"

    @staticmethod
    def get_liquidation_stream(symbol: str = None) -> str:
        """Get liquidation orders stream name."""
        return f"!forceOrder@arr" if not symbol else f"{symbol.lower()}@forceOrder"

    @staticmethod
    def get_depth_stream(symbol: str, level: str = '20') -> str:
        """Get partial book depth stream name."""
        return f"{symbol.lower()}@depth{level}"

    @staticmethod
    def get_diff_depth_stream(symbol: str) -> str:
        """Get diff. depth stream name."""
        return f"{symbol.lower()}@depth"
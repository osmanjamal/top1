import json
import logging
import asyncio
from typing import Dict, Optional, List, Callable
import websockets
from websockets.exceptions import ConnectionClosed

from app.core.config import settings

logger = logging.getLogger(__name__)

class BinanceSpotWebSocket:
    """
    Binance Spot WebSocket client for real-time market data.
    """
    
    def __init__(self, testnet: bool = settings.BINANCE_TESTNET):
        self.testnet = testnet
        self.base_url = (
            "wss://testnet.binance.vision/ws"
            if testnet else
            "wss://stream.binance.com:9443/ws"
        )
        self.callbacks: Dict[str, List[Callable]] = {}
        self.websocket = None
        self.running = False
        self.reconnect_delay = 5  # seconds

    async def connect(self):
        """
        Establish WebSocket connection.
        """
        try:
            self.websocket = await websockets.connect(self.base_url)
            self.running = True
            logger.info("WebSocket connection established")
            await self._handle_messages()
        except Exception as e:
            logger.error(f"WebSocket connection failed: {str(e)}")
            await self.reconnect()

    async def reconnect(self):
        """
        Reconnect to WebSocket.
        """
        logger.info(f"Attempting to reconnect in {self.reconnect_delay} seconds...")
        await asyncio.sleep(self.reconnect_delay)
        await self.connect()

    async def subscribe(self, stream: str, callback: Callable):
        """
        Subscribe to a stream and register callback.
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
        logger.info(f"Subscribed to stream: {stream}")

    async def unsubscribe(self, stream: str):
        """
        Unsubscribe from a stream.
        """
        if stream in self.callbacks:
            del self.callbacks[stream]
            
        unsubscribe_message = {
            "method": "UNSUBSCRIBE",
            "params": [stream],
            "id": len(self.callbacks)
        }
        
        await self._send_message(unsubscribe_message)
        logger.info(f"Unsubscribed from stream: {stream}")

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

    async def _handle_messages(self):
        """
        Handle incoming WebSocket messages.
        """
        while self.running:
            try:
                if not self.websocket:
                    await self.reconnect()
                    continue

                message = await self.websocket.recv()
                data = json.loads(message)
                
                # Handle subscription confirmation
                if 'result' in data:
                    continue
                    
                # Handle stream data
                stream = data.get('stream')
                if stream and stream in self.callbacks:
                    for callback in self.callbacks[stream]:
                        await callback(data['data'])

            except ConnectionClosed:
                logger.error("WebSocket connection closed")
                await self.reconnect()
            except Exception as e:
                logger.error(f"Error handling message: {str(e)}")
                await asyncio.sleep(1)

    async def close(self):
        """
        Close WebSocket connection.
        """
        self.running = False
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            logger.info("WebSocket connection closed")

    @staticmethod
    def get_trade_stream(symbol: str) -> str:
        """
        Get trade stream name for symbol.
        """
        return f"{symbol.lower()}@trade"

    @staticmethod
    def get_kline_stream(symbol: str, interval: str) -> str:
        """
        Get kline stream name for symbol and interval.
        """
        return f"{symbol.lower()}@kline_{interval}"

    @staticmethod
    def get_ticker_stream(symbol: str) -> str:
        """
        Get 24hr ticker stream name for symbol.
        """
        return f"{symbol.lower()}@ticker"

    @staticmethod
    def get_book_ticker_stream(symbol: str) -> str:
        """
        Get book ticker stream name for symbol.
        """
        return f"{symbol.lower()}@bookTicker"

    @staticmethod
    def get_depth_stream(symbol: str, level: str = '20') -> str:
        """
        Get order book depth stream name for symbol.
        """
        return f"{symbol.lower()}@depth{level}"

    async def subscribe_trades(self, symbol: str, callback: Callable):
        """
        Subscribe to trade updates for a symbol.
        """
        stream = self.get_trade_stream(symbol)
        await self.subscribe(stream, callback)

    async def subscribe_klines(self, symbol: str, interval: str, callback: Callable):
        """
        Subscribe to kline updates for a symbol.
        """
        stream = self.get_kline_stream(symbol, interval)
        await self.subscribe(stream, callback)

    async def subscribe_ticker(self, symbol: str, callback: Callable):
        """
        Subscribe to ticker updates for a symbol.
        """
        stream = self.get_ticker_stream(symbol)
        await self.subscribe(stream, callback)

    async def subscribe_book_ticker(self, symbol: str, callback: Callable):
        """
        Subscribe to book ticker updates for a symbol.
        """
        stream = self.get_book_ticker_stream(symbol)
        await self.subscribe(stream, callback)

    async def subscribe_depth(
        self,
        symbol: str,
        callback: Callable,
        level: str = '20'
    ):
        """
        Subscribe to order book depth updates for a symbol.
        """
        stream = self.get_depth_stream(symbol, level)
        await self.subscribe(stream, callback)
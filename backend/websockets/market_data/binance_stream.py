import asyncio
import logging
import json
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
import websockets
from websockets.exceptions import ConnectionClosed

from app.core.config import settings
from app.models.user import User
from app.exchanges.binance.futures import BinanceFuturesClient

logger = logging.getLogger(__name__)

class BinanceWebSocketManager:
    """
    Manager for handling Binance WebSocket connections and data streams.
    """
    
    def __init__(self, user: Optional[User] = None):
        self.user = user
        self.futures_client = None
        if user:
            self.futures_client = BinanceFuturesClient(
                api_key=user.binance_api_key,
                api_secret=user.binance_api_secret,
                testnet=settings.BINANCE_TESTNET
            )
            
        # WebSocket connection settings
        self.base_url = (
            "wss://fstream.binancefuture.com/ws"
            if not settings.BINANCE_TESTNET else
            "wss://stream.binancefuture.com/ws"
        )
        
        # Connection management
        self.websocket = None
        self.running = False
        self.subscribed_streams: Dict[str, List[Callable]] = {}
        self.last_heartbeat: Optional[datetime] = None
        self.heartbeat_interval = 30  # seconds
        self.reconnect_delay = 5  # seconds
        self.max_reconnect_attempts = 5
        
        # Message handlers
        self.handlers = {
            'trade': self._handle_trade,
            'kline': self._handle_kline,
            'depth': self._handle_depth,
            'ticker': self._handle_ticker,
            'bookTicker': self._handle_book_ticker,
            'markPrice': self._handle_mark_price,
            'forceOrder': self._handle_liquidation,
            'aggTrade': self._handle_agg_trade
        }
        
        # Data storage
        self.orderbook_manager = OrderBookManager()
        self.trades_cache: Dict[str, List[Dict]] = {}
        self.klines_cache: Dict[str, Dict[str, List[Dict]]] = {}
        self.tickers_cache: Dict[str, Dict] = {}
        
        # Stream statistics
        self.message_count = 0
        self.error_count = 0
        self.last_error: Optional[str] = None
        self.latency_stats: List[float] = []
        self.message_count = 0
        self.error_count = 0
        self.last_error: Optional[str] = None
        self.latency_stats: List[float] = []

    async def connect(self):
        """
        Establish WebSocket connection with error handling and reconnection logic.
        """
        try:
            if self.websocket:
                await self.websocket.close()
            
            self.websocket = await websockets.connect(self.base_url)
            self.running = True
            self.last_heartbeat = datetime.utcnow()
            logger.info(f"WebSocket connected to {self.base_url}")
            
            # Start core tasks
            await asyncio.gather(
                self._heartbeat_loop(),
                self._message_handler(),
                self._monitor_connection()
            )
            
        except Exception as e:
            logger.error(f"WebSocket connection error: {str(e)}")
            await self._handle_connection_error()

    async def subscribe(self, stream: str, callback: Callable) -> bool:
        """
        Subscribe to a market data stream.
        
        Args:
            stream: Stream name to subscribe to
            callback: Callback function to handle stream data
            
        Returns:
            Boolean indicating subscription success
        """
        try:
            # Add callback to subscribers
            if stream not in self.subscribed_streams:
                self.subscribed_streams[stream] = []
            self.subscribed_streams[stream].append(callback)
            
            # Send subscription message
            subscribe_message = {
                "method": "SUBSCRIBE",
                "params": [stream],
                "id": len(self.subscribed_streams)
            }
            
            await self._send_message(subscribe_message)
            logger.info(f"Subscribed to stream: {stream}")
            return True
            
        except Exception as e:
            logger.error(f"Error subscribing to stream {stream}: {str(e)}")
            return False

    async def unsubscribe(self, stream: str) -> bool:
        """
        Unsubscribe from a market data stream.
        
        Args:
            stream: Stream to unsubscribe from
            
        Returns:
            Boolean indicating unsubscription success
        """
        try:
            # Remove stream callbacks
            if stream in self.subscribed_streams:
                del self.subscribed_streams[stream]
            
            # Send unsubscribe message
            unsubscribe_message = {
                "method": "UNSUBSCRIBE",
                "params": [stream],
                "id": len(self.subscribed_streams)
            }
            
            await self._send_message(unsubscribe_message)
            logger.info(f"Unsubscribed from stream: {stream}")
            return True
            
        except Exception as e:
            logger.error(f"Error unsubscribing from stream {stream}: {str(e)}")
            return False

    async def _send_message(self, message: Dict) -> bool:
        """
        Send message to WebSocket server with error handling.
        
        Args:
            message: Message to send
            
        Returns:
            Boolean indicating send success
        """
        try:
            if not self.websocket:
                raise ConnectionError("WebSocket not connected")
                
            await self.websocket.send(json.dumps(message))
            return True
            
        except ConnectionClosed:
            logger.error("WebSocket connection closed while sending message")
            await self._handle_connection_error()
            return False
            
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False

    async def _message_handler(self):
        """
        Main loop for handling incoming WebSocket messages.
        """
        while self.running:
            try:
                if not self.websocket:
                    await asyncio.sleep(1)
                    continue
                
                message = await self.websocket.recv()
                message_time = datetime.utcnow()
                
                # Parse message
                data = json.loads(message)
                
                # Update statistics
                self.message_count += 1
                
                # Handle different message types
                if 'stream' in data:
                    stream_name = data['stream']
                    stream_data = data['data']
                    
                    # Calculate message latency
                    if 'E' in stream_data:  # Event time
                        event_time = datetime.fromtimestamp(stream_data['E'] / 1000)
                        latency = (message_time - event_time).total_seconds()
                        self.latency_stats.append(latency)
                        
                        # Keep only last 1000 latency measurements
                        if len(self.latency_stats) > 1000:
                            self.latency_stats.pop(0)
                    
                    # Handle stream data
                    for handler in self.subscribed_streams.get(stream_name, []):
                        try:
                            await handler(stream_data)
                        except Exception as e:
                            logger.error(f"Error in stream handler: {str(e)}")
                            
                elif 'result' in data:
                    # Handle subscription responses
                    logger.debug(f"Subscription response: {data}")
                    
                elif 'error' in data:
                    # Handle error messages
                    self.error_count += 1
                    self.last_error = data['error']['msg']
                    logger.error(f"WebSocket error message: {self.last_error}")
                    
            except ConnectionClosed:
                logger.error("WebSocket connection closed")
                await self._handle_connection_error()
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)}")
                self.error_count += 1
                
            except Exception as e:
                logger.error(f"Error handling message: {str(e)}")
                self.error_count += 1
                await asyncio.sleep(1)

    async def _heartbeat_loop(self):
        """
        Maintain WebSocket connection with periodic heartbeats.
        """
        while self.running:
            try:
                if self.websocket and self.last_heartbeat:
                    time_since_last = (datetime.utcnow() - self.last_heartbeat).total_seconds()
                    
                    if time_since_last > self.heartbeat_interval:
                        ping_message = {"method": "ping"}
                        await self._send_message(ping_message)
                        self.last_heartbeat = datetime.utcnow()
                        
                await asyncio.sleep(self.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {str(e)}")
                await asyncio.sleep(1)

    async def _monitor_connection(self):
        """
        Monitor WebSocket connection health and performance.
        """
        while self.running:
            try:
                # Check connection status
                if not self.websocket:
                    logger.warning("WebSocket disconnected, attempting to reconnect...")
                    await self._handle_connection_error()
                    continue
                
                # Check message flow
                if self.message_count > 0:
                    # Calculate average latency
                    avg_latency = sum(self.latency_stats) / len(self.latency_stats) if self.latency_stats else 0
                    
                    # Log connection statistics
                    logger.info(
                        f"Connection stats - Messages: {self.message_count}, "
                        f"Errors: {self.error_count}, Avg Latency: {avg_latency:.3f}s"
                    )
                    
                    # Check error rate
                    error_rate = self.error_count / self.message_count
                    if error_rate > 0.1:  # 10% error rate threshold
                        logger.warning(f"High error rate detected: {error_rate:.2%}")
                    
                    # Check latency
                    if avg_latency > 1.0:  # 1 second latency threshold
                        logger.warning(f"High latency detected: {avg_latency:.3f}s")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error monitoring connection: {str(e)}")
                await asyncio.sleep(1)

    async def _handle_connection_error(self):
        """
        Handle WebSocket connection errors with reconnection logic.
        """
        attempt = 0
        while attempt < self.max_reconnect_attempts and self.running:
            try:
                logger.info(f"Reconnection attempt {attempt + 1}/{self.max_reconnect_attempts}")
                
                # Close existing connection if any
                if self.websocket:
                    await self.websocket.close()
                    self.websocket = None
                
                # Exponential backoff
                wait_time = self.reconnect_delay * (2 ** attempt)
                await asyncio.sleep(wait_time)
                
                # Attempt reconnection
                await self.connect()
                
                # Resubscribe to streams
                for stream in self.subscribed_streams:
                    subscribe_message = {
                        "method": "SUBSCRIBE",
                        "params": [stream],
                        "id": len(self.subscribed_streams)
                    }
                    await self._send_message(subscribe_message)
                
                logger.info("Successfully reconnected")
                return
                
            except Exception as e:
                logger.error(f"Reconnection attempt {attempt + 1} failed: {str(e)}")
                attempt += 1
        
        if attempt >= self.max_reconnect_attempts:
            logger.error("Max reconnection attempts reached, stopping WebSocket")
            self.running = False

    async def _handle_trade(self, data: Dict[str, Any]):
        """
        Handle individual trade updates.
        """
        try:
            symbol = data['s']  # Symbol
            trade = {
                'symbol': symbol,
                'price': float(data['p']),
                'quantity': float(data['q']),
                'time': datetime.fromtimestamp(data['T'] / 1000),
                'is_buyer_maker': data['m'],
                'trade_id': data['t']
            }
            
            # Update trades cache
            if symbol not in self.trades_cache:
                self.trades_cache[symbol] = []
            self.trades_cache[symbol].append(trade)
            
            # Keep only last 1000 trades per symbol
            if len(self.trades_cache[symbol]) > 1000:
                self.trades_cache[symbol].pop(0)
            
        except Exception as e:
            logger.error(f"Error handling trade: {str(e)}")

    async def _handle_kline(self, data: Dict[str, Any]):
        """
        Handle kline/candlestick updates.
        """
        try:
            symbol = data['s']
            interval = data['k']['i']
            kline = {
                'open_time': datetime.fromtimestamp(data['k']['t'] / 1000),
                'open': float(data['k']['o']),
                'high': float(data['k']['h']),
                'low': float(data['k']['l']),
                'close': float(data['k']['c']),
                'volume': float(data['k']['v']),
                'close_time': datetime.fromtimestamp(data['k']['T'] / 1000),
                'quote_volume': float(data['k']['q']),
                'trades': int(data['k']['n']),
                'is_closed': data['k']['x']
            }
            
            # Update klines cache
            if symbol not in self.klines_cache:
                self.klines_cache[symbol] = {}
            if interval not in self.klines_cache[symbol]:
                self.klines_cache[symbol][interval] = []
                
            # Update or append kline
            for i, existing_kline in enumerate(self.klines_cache[symbol][interval]):
                if existing_kline['open_time'] == kline['open_time']:
                    self.klines_cache[symbol][interval][i] = kline
                    break
            else:
                self.klines_cache[symbol][interval].append(kline)
            
            # Keep only last 1000 klines per symbol/interval
            if len(self.klines_cache[symbol][interval]) > 1000:
                self.klines_cache[symbol][interval].pop(0)
                
        except Exception as e:
            logger.error(f"Error handling kline: {str(e)}")

    async def _handle_depth(self, data: Dict[str, Any]):
        """
        Handle order book updates.
        """
        try:
            symbol = data['s']
            
            # Update order book
            self.orderbook_manager.update_orderbook(
                symbol=symbol,
                bids=[(float(price), float(qty)) for price, qty in data['b']],
                asks=[(float(price), float(qty)) for price, qty in data['a']],
                update_id=data['u'],
                event_time=datetime.fromtimestamp(data['E'] / 1000)
            )
            
        except Exception as e:
            logger.error(f"Error handling depth update: {str(e)}")

    async def _handle_ticker(self, data: Dict[str, Any]):
        """
        Handle 24-hour ticker updates.
        """
        try:
            symbol = data['s']
            ticker = {
                'symbol': symbol,
                'price_change': float(data['p']),
                'price_change_percent': float(data['P']),
                'weighted_avg_price': float(data['w']),
                'last_price': float(data['c']),
                'last_qty': float(data['Q']),
                'open_price': float(data['o']),
                'high_price': float(data['h']),
                'low_price': float(data['l']),
                'volume': float(data['v']),
                'quote_volume': float(data['q']),
                'open_time': datetime.fromtimestamp(data['O'] / 1000),
                'close_time': datetime.fromtimestamp(data['C'] / 1000),
                'first_id': data['F'],
                'last_id': data['L'],
                'count': data['n']
            }
            
            # Update tickers cache
            self.tickers_cache[symbol] = ticker
            
        except Exception as e:
            logger.error(f"Error handling ticker: {str(e)}")

    async def _handle_book_ticker(self, data: Dict[str, Any]):
        """
        Handle book ticker updates.
        """
        try:
            self.orderbook_manager.update_best_positions(
                symbol=data['s'],
                bid_price=float(data['b']),
                bid_qty=float(data['B']),
                ask_price=float(data['a']),
                ask_qty=float(data['A']),
                update_id=data['u']
            )
            
        except Exception as e:
            logger.error(f"Error handling book ticker: {str(e)}")

    async def _handle_mark_price(self, data: Dict[str, Any]):
        """
        Handle mark price updates.
        """
        try:
            symbol = data['s']
            mark_price = float(data['p'])
            index_price = float(data.get('i', 0))
            funding_rate = float(data.get('r', 0))
            next_funding_time = datetime.fromtimestamp(data['T'] / 1000)
            
            # You can implement custom logic here to handle mark price updates
            # For example, trigger position updates or risk calculations
            
        except Exception as e:
            logger.error(f"Error handling mark price: {str(e)}")

    async def _handle_liquidation(self, data: Dict[str, Any]):
        """
        Handle liquidation order updates.
        """
        try:
            liquidation = {
                'symbol': data['s'],
                'side': data['S'],
                'order_type': data['o'],
                'time_in_force': data['f'],
                'original_quantity': float(data['q']),
                'price': float(data['p']),
                'average_price': float(data['ap']),
                'order_status': data['X'],
                'last_filled_qty': float(data['l']),
                'filled_accumulated_qty': float(data['z']),
                'order_time': datetime.fromtimestamp(data['T'] / 1000)
            }
            
            # You can implement custom logic here to handle liquidation events
            # For example, trigger risk alerts or position adjustments
            logger.warning(f"Liquidation detected: {liquidation}")
            
        except Exception as e:
            logger.error(f"Error handling liquidation: {str(e)}")

    async def _handle_agg_trade(self, data: Dict[str, Any]):
        """
        Handle aggregated trade updates.
        """
        try:
            agg_trade = {
                'symbol': data['s'],
                'price': float(data['p']),
                'quantity': float(data['q']),
                'first_trade_id': data['f'],
                'last_trade_id': data['l'],
                'time': datetime.fromtimestamp(data['T'] / 1000),
                'is_buyer_maker': data['m'],
                'is_best_price_match': data['M']
            }
            
            # You can implement custom logic here to handle aggregated trades
            # For example, update trading volume analytics or trigger signals
            
        except Exception as e:
            logger.error(f"Error handling aggregated trade: {str(e)}")

class OrderBookManager:
    """
    Manager for handling order book data and updates.
    """
    
    def __init__(self):
        self.orderbooks: Dict[str, Dict[str, list]] = {}  # symbol -> {bids: [], asks: []}
        self.best_positions: Dict[str, Dict[str, float]] = {}  # symbol -> {bid: price, ask: price, ...}
        self.last_update_ids: Dict[str, int] = {}  # symbol -> last_update_id
        self.depth_cache_size = 1000  # Maximum number of price levels to maintain
        
    def update_orderbook(
        self,
        symbol: str,
        bids: List[tuple[float, float]],
        asks: List[tuple[float, float]],
        update_id: int,
        event_time: datetime
    ):
        """
        Update order book with new data.
        
        Args:
            symbol: Trading pair symbol
            bids: List of (price, quantity) tuples for bids
            asks: List of (price, quantity) tuples for asks
            update_id: Update sequence number
            event_time: Event timestamp
        """
        try:
            # Initialize order book if needed
            if symbol not in self.orderbooks:
                self.orderbooks[symbol] = {
                    'bids': [],
                    'asks': [],
                    'last_update': None
                }
            
            # Verify update sequence
            if symbol in self.last_update_ids:
                if update_id <= self.last_update_ids[symbol]:
                    return  # Skip old updates
            
            orderbook = self.orderbooks[symbol]
            
            # Update bids
            for bid in bids:
                self._update_price_level(orderbook['bids'], bid, True)
            
            # Update asks
            for ask in asks:
                self._update_price_level(orderbook['asks'], ask, False)
            
            # Sort and trim order book
            orderbook['bids'] = sorted(orderbook['bids'], key=lambda x: x[0], reverse=True)[:self.depth_cache_size]
            orderbook['asks'] = sorted(orderbook['asks'], key=lambda x: x[0])[:self.depth_cache_size]
            
            # Update metadata
            self.last_update_ids[symbol] = update_id
            orderbook['last_update'] = event_time
            
        except Exception as e:
            logger.error(f"Error updating order book: {str(e)}")
            
    def update_best_positions(
        self,
        symbol: str,
        bid_price: float,
        bid_qty: float,
        ask_price: float,
        ask_qty: float,
        update_id: int
    ):
        """
        Update best bid/ask positions.
        
        Args:
            symbol: Trading pair symbol
            bid_price: Best bid price
            bid_qty: Best bid quantity
            ask_price: Best ask price
            ask_qty: Best ask quantity
            update_id: Update sequence number
        """
        try:
            self.best_positions[symbol] = {
                'bid_price': bid_price,
                'bid_qty': bid_qty,
                'ask_price': ask_price,
                'ask_qty': ask_qty,
                'spread': ask_price - bid_price,
                'spread_percentage': ((ask_price - bid_price) / ask_price) * 100,
                'mid_price': (ask_price + bid_price) / 2,
                'update_id': update_id,
                'timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error updating best positions: {str(e)}")
            
    def get_orderbook(self, symbol: str) -> Optional[Dict]:
        """
        Get current order book for symbol.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Order book data or None if not available
        """
        return self.orderbooks.get(symbol)
            
    def get_best_positions(self, symbol: str) -> Optional[Dict]:
        """
        Get best bid/ask positions for symbol.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Best positions data or None if not available
        """
        return self.best_positions.get(symbol)
            
    def calculate_order_impact(
        self,
        symbol: str,
        side: str,
        quantity: float
    ) -> Optional[Dict[str, float]]:
        """
        Calculate market impact for a potential order.
        
        Args:
            symbol: Trading pair symbol
            side: Order side ('buy' or 'sell')
            quantity: Order quantity
            
        Returns:
            Dictionary with impact analysis or None if unable to calculate
        """
        try:
            orderbook = self.orderbooks.get(symbol)
            if not orderbook:
                return None
                
            remaining_qty = quantity
            total_value = 0.0
            levels_used = 0
            avg_price = 0.0
            
            # Select price levels based on side
            levels = orderbook['asks'] if side.upper() == 'BUY' else orderbook['bids']
            
            for price, level_qty in levels:
                if remaining_qty <= 0:
                    break
                    
                # Calculate fill at this level
                fill_qty = min(remaining_qty, level_qty)
                total_value += fill_qty * price
                remaining_qty -= fill_qty
                levels_used += 1
                
            if remaining_qty > 0:
                return {
                    'full_fill_possible': False,
                    'fillable_quantity': quantity - remaining_qty,
                    'levels_needed': levels_used,
                    'unfilled_quantity': remaining_qty
                }
                
            avg_price = total_value / quantity
            slippage = (avg_price - levels[0][0]) / levels[0][0] * 100
            
            return {
                'full_fill_possible': True,
                'average_price': avg_price,
                'slippage_percent': slippage,
                'total_value': total_value,
                'levels_used': levels_used
            }
            
        except Exception as e:
            logger.error(f"Error calculating order impact: {str(e)}")
            return None
            
    def _update_price_level(
        self,
        levels: List[tuple[float, float]],
        update: tuple[float, float],
        is_bid: bool
    ):
        """
        Update a single price level in the order book.
        
        Args:
            levels: List of price levels to update
            update: (price, quantity) tuple with update
            is_bid: Boolean indicating if this is a bid level
        """
        price, qty = update
        
        # Remove price level if quantity is 0
        if qty == 0:
            levels[:] = [level for level in levels if level[0] != price]
            return
            
        # Update existing price level or insert new one
        for i, level in enumerate(levels):
            if level[0] == price:
                levels[i] = update
                break
        else:
            levels.append(update)
            
        # Sort levels (descending for bids, ascending for asks)
        levels.sort(key=lambda x: x[0], reverse=is_bid)
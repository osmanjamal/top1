import asyncio
import logging
from typing import Dict, List, Optional, Set, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from collections import deque

from app.core.config import settings
from app.websockets.market_data.binance_stream import BinanceWebSocketManager

logger = logging.getLogger(__name__)

class PriceFeedManager:
    """
    Manager for real-time price feeds and market data aggregation.
    """
    
    def __init__(self):
        # WebSocket connections
        self.binance_ws = BinanceWebSocketManager()
        
        # Price data storage
        self.price_cache: Dict[str, deque] = {}  # symbol -> price history
        self.volume_cache: Dict[str, deque] = {}  # symbol -> volume history
        self.tick_cache: Dict[str, Dict] = {}  # symbol -> latest tick data
        
        # Market analytics
        self.volatility_cache: Dict[str, float] = {}  # symbol -> volatility
        self.momentum_cache: Dict[str, float] = {}  # symbol -> momentum
        self.trend_cache: Dict[str, str] = {}  # symbol -> trend direction
        
        # Configuration
        self.max_cache_size = 1000
        self.update_interval = 1.0  # seconds
        self.volatility_window = 20  # periods for volatility calculation
        self.momentum_window = 14  # periods for momentum calculation
        self.trend_window = 50  # periods for trend determination
        
        # Active symbols tracking
        self.active_symbols: Set[str] = set()
        self.symbol_subscriptions: Dict[str, int] = {}  # symbol -> subscriber count
        
        # Statistics
        self.last_update_time: Dict[str, datetime] = {}
        self.update_count: Dict[str, int] = {}
        self.error_count: Dict[str, int] = {}
        
        # Analytics configuration
        self.analytics_config = {
            'volatility': {
                'high_threshold': 0.02,  # 2% threshold for high volatility
                'low_threshold': 0.005   # 0.5% threshold for low volatility
            },
            'volume': {
                'surge_threshold': 2.0,   # 2x average volume for surge detection
                'dry_threshold': 0.5      # 0.5x average volume for dry detection
            },
            'price': {
                'significant_move': 0.01,  # 1% threshold for significant price moves
                'extreme_move': 0.05      # 5% threshold for extreme price moves
            }
        }

    async def start(self):
        """
        Start the price feed manager and connect to exchanges.
        """
        try:
            # Connect to WebSocket
            await self.binance_ws.connect()
            
            # Start background tasks
            await asyncio.gather(
                self._update_analytics_loop(),
                self._cleanup_loop(),
                self._monitor_feed_loop()
            )
            
        except Exception as e:
            logger.error(f"Error starting price feed: {str(e)}")
            raise

    async def subscribe_symbol(self, symbol: str) -> bool:
        """
        Subscribe to price updates for a symbol.
        
        Args:
            symbol: Trading pair symbol to subscribe to
            
        Returns:
            Boolean indicating subscription success
        """
        try:
            if symbol in self.active_symbols:
                self.symbol_subscriptions[symbol] += 1
                return True
            
            # Initialize caches for new symbol
            self.price_cache[symbol] = deque(maxlen=self.max_cache_size)
            self.volume_cache[symbol] = deque(maxlen=self.max_cache_size)
            self.tick_cache[symbol] = {}
            self.update_count[symbol] = 0
            self.error_count[symbol] = 0
            
            # Subscribe to different data streams
            streams_to_subscribe = [
                f"{symbol.lower()}@trade",        # Trade data
                f"{symbol.lower()}@ticker",       # 24hr ticker
                f"{symbol.lower()}@bookTicker",   # Best bid/ask
                f"{symbol.lower()}@depth20"       # Order book depth
            ]
            
            for stream in streams_to_subscribe:
                success = await self.binance_ws.subscribe(
                    stream=stream,
                    callback=self._handle_price_update
                )
                if not success:
                    logger.error(f"Failed to subscribe to stream: {stream}")
                    return False
            
            self.active_symbols.add(symbol)
            self.symbol_subscriptions[symbol] = 1
            self.last_update_time[symbol] = datetime.utcnow()
            
            logger.info(f"Successfully subscribed to symbol: {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error subscribing to symbol {symbol}: {str(e)}")
            return False

    async def unsubscribe_symbol(self, symbol: str) -> bool:
        """
        Unsubscribe from price updates for a symbol.
        
        Args:
            symbol: Trading pair symbol to unsubscribe from
            
        Returns:
            Boolean indicating unsubscription success
        """
        try:
            if symbol not in self.active_symbols:
                return True
                
            self.symbol_subscriptions[symbol] -= 1
            
            # Only unsubscribe if no more subscribers
            if self.symbol_subscriptions[symbol] <= 0:
                streams_to_unsubscribe = [
                    f"{symbol.lower()}@trade",
                    f"{symbol.lower()}@ticker",
                    f"{symbol.lower()}@bookTicker",
                    f"{symbol.lower()}@depth20"
                ]
                
                for stream in streams_to_unsubscribe:
                    success = await self.binance_ws.unsubscribe(stream)
                    if not success:
                        logger.error(f"Failed to unsubscribe from stream: {stream}")
                        return False
                
                # Cleanup symbol data
                self.active_symbols.remove(symbol)
                del self.symbol_subscriptions[symbol]
                del self.price_cache[symbol]
                del self.volume_cache[symbol]
                del self.tick_cache[symbol]
                del self.volatility_cache[symbol]
                del self.momentum_cache[symbol]
                del self.trend_cache[symbol]
                del self.update_count[symbol]
                del self.error_count[symbol]
                del self.last_update_time[symbol]
                
                logger.info(f"Successfully unsubscribed from symbol: {symbol}")
                
            return True
            
        except Exception as e:
            logger.error(f"Error unsubscribing from symbol {symbol}: {str(e)}")
            return False

    async def get_price(self, symbol: str) -> Optional[float]:
        """
        Get latest price for a symbol.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Latest price or None if not available
        """
        try:
            tick_data = self.tick_cache.get(symbol)
            if tick_data and 'last_price' in tick_data:
                return float(tick_data['last_price'])
            return None
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {str(e)}")
            return None

    async def get_price_history(
        self,
        symbol: str,
        interval: str = '1m',
        limit: int = 100
    ) -> Optional[pd.DataFrame]:
        """
        Get historical price data for a symbol.
        
        Args:
            symbol: Trading pair symbol
            interval: Time interval (e.g., '1m', '5m', '1h')
            limit: Number of records to return
            
        Returns:
            DataFrame with historical prices or None if not available
        """
        try:
            if symbol not in self.price_cache:
                return None
                
            # Convert deque to DataFrame
            df = pd.DataFrame(list(self.price_cache[symbol]))
            
            # Resample data to requested interval
            if interval.endswith('m'):
                freq = f"{interval[:-1]}T"
            elif interval.endswith('h'):
                freq = f"{interval[:-1]}H"
            else:
                freq = interval
                
            resampled = df.resample(freq, on='timestamp').agg({
                'price': 'ohlc',
                'volume': 'sum'
            }).dropna()
            
            return resampled.tail(limit)
            
        except Exception as e:
            logger.error(f"Error getting price history for {symbol}: {str(e)}")
            return None

    async def _handle_price_update(self, data: Dict[str, Any]):
        """
        Handle incoming price update from WebSocket.
        """
        try:
            symbol = data['s']  # Symbol
            timestamp = datetime.fromtimestamp(data['E'] / 1000)
            
            # Update tick cache
            self.tick_cache[symbol] = {
                'last_price': float(data['c']),
                'bid_price': float(data['b']),
                'ask_price': float(data['a']),
                'volume': float(data['v']),
                'timestamp': timestamp
            }
            
            # Update price and volume caches
            self.price_cache[symbol].append({
                'timestamp': timestamp,
                'price': float(data['c']),
                'volume': float(data['v'])
            })
            
            self.last_update_time[symbol] = timestamp
            self.update_count[symbol] += 1
            
        except Exception as e:
            logger.error(f"Error handling price update: {str(e)}")
            if symbol in self.error_count:
                self.error_count[symbol] += 1

    async def _update_analytics_loop(self):
        """
        Background task to update market analytics.
        """
        while True:
            try:
                for symbol in self.active_symbols:
                    if len(self.price_cache[symbol]) >= self.volatility_window:
                        # Update volatility
                        self.volatility_cache[symbol] = await self._calculate_volatility(symbol)
                        
                        # Update momentum
                        self.momentum_cache[symbol] = await self._calculate_momentum(symbol)
                        
                        # Update trend
                        self.trend_cache[symbol] = await self._determine_trend(symbol)
                        
                        # Check for significant market events
                        await self._check_market_events(symbol)
                
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Error in analytics loop: {str(e)}")
                await asyncio.sleep(1)

    async def _calculate_volatility(self, symbol: str) -> float:
        """
        Calculate price volatility for a symbol.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Calculated volatility value
        """
        try:
            prices = [item['price'] for item in self.price_cache[symbol]]
            returns = np.diff(np.log(prices))
            return np.std(returns) * np.sqrt(len(returns))
        except Exception as e:
            logger.error(f"Error calculating volatility for {symbol}: {str(e)}")
            return 0.0

    async def _calculate_momentum(self, symbol: str) -> float:
        """
        Calculate price momentum for a symbol.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Calculated momentum value
        """
        try:
            prices = [item['price'] for item in self.price_cache[symbol]]
            if len(prices) < self.momentum_window:
                return 0.0
            
            current_price = prices[-1]
            past_price = prices[-self.momentum_window]
            return (current_price - past_price) / past_price * 100
            
        except Exception as e:
            logger.error(f"Error calculating momentum for {symbol}: {str(e)}")
            return 0.0

    async def _determine_trend(self, symbol: str) -> str:
        """
        Determine price trend for a symbol.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Trend direction ('up', 'down', or 'sideways')
        """
        try:
            prices = [item['price'] for item in self.price_cache[symbol]]
            if len(prices) < self.trend_window:
                return 'sideways'
            
            # Calculate simple moving averages
            short_ma = np.mean(prices[-20:])
            long_ma = np.mean(prices[-50:])
            
            # Calculate trend strength
            price_change = (prices[-1] - prices[-self.trend_window]) / prices[-self.trend_window] * 100
            
            if short_ma > long_ma and price_change > 1:
                return 'up'
            elif short_ma < long_ma and price_change < -1:
                return 'down'
            else:
                return 'sideways'
                
        except Exception as e:
            logger.error(f"Error determining trend for {symbol}: {str(e)}")
            return 'sideways'

    async def _check_market_events(self, symbol: str):
        """
        Check for significant market events.
        """
        try:
            # Get current market state
            volatility = self.volatility_cache.get(symbol, 0)
            momentum = self.momentum_cache.get(symbol, 0)
            trend = self.trend_cache.get(symbol, 'sideways')
            
            # Check volume surge
            current_volume = self.tick_cache[symbol]['volume']
            avg_volume = np.mean([item['volume'] for item in self.volume_cache[symbol]])
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            # Check price movement
            prices = [item['price'] for item in self.price_cache[symbol]]
            if len(prices) >= 2:
                price_change = (prices[-1] - prices[-2]) / prices[-2] * 100
            else:
                price_change = 0
                
            # Generate alerts based on conditions
            if volatility > self.analytics_config['volatility']['high_threshold']:
                logger.warning(f"High volatility detected for {symbol}: {volatility:.2%}")
            
            if abs(momentum) > 5:  # 5% momentum threshold
                direction = "bullish" if momentum > 0 else "bearish"
                logger.info(f"Strong {direction} momentum for {symbol}: {momentum:.2f}%")
            
            if volume_ratio > self.analytics_config['volume']['surge_threshold']:
                logger.info(f"Volume surge detected for {symbol}: {volume_ratio:.2f}x average")
            
            if abs(price_change) > self.analytics_config['price']['significant_move']:
                direction = "up" if price_change > 0 else "down"
                logger.warning(f"Significant price move {direction} for {symbol}: {price_change:.2f}%")
                
        except Exception as e:
            logger.error(f"Error checking market events for {symbol}: {str(e)}")

    async def _monitor_feed_loop(self):
        """
        Monitor feed health and performance.
        """
        while True:
            try:
                current_time = datetime.utcnow()
                
                for symbol in self.active_symbols:
                    last_update = self.last_update_time.get(symbol)
                    if last_update:
                        time_since_update = (current_time - last_update).total_seconds()
                        
                        # Check for stale data
                        if time_since_update > 60:  # 1 minute threshold
                            logger.warning(f"Stale data detected for {symbol}. Last update: {time_since_update:.1f}s ago")
                        
                        # Check error rate
                        total_updates = self.update_count[symbol]
                        total_errors = self.error_count[symbol]
                        if total_updates > 0:
                            error_rate = total_errors / total_updates
                            if error_rate > 0.1:  # 10% error threshold
                                logger.warning(f"High error rate for {symbol}: {error_rate:.2%}")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {str(e)}")
                await asyncio.sleep(1)

    async def _cleanup_loop(self):
        """
        Periodic cleanup of old data.
        """
        while True:
            try:
                current_time = datetime.utcnow()
                cleanup_threshold = current_time - timedelta(hours=24)
                
                for symbol in list(self.active_symbols):
                    # Clean old data from caches
                    if symbol in self.price_cache:
                        self.price_cache[symbol] = deque(
                            [x for x in self.price_cache[symbol] if x['timestamp'] > cleanup_threshold],
                            maxlen=self.max_cache_size
                        )
                    
                    if symbol in self.volume_cache:
                        self.volume_cache[symbol] = deque(
                            [x for x in self.volume_cache[symbol] if x['timestamp'] > cleanup_threshold],
                            maxlen=self.max_cache_size
                        )
                
                await asyncio.sleep(3600)  # Run cleanup every hour
                
            except Exception as e:
                logger.error(f"Error in cleanup loop: {str(e)}")
                await asyncio.sleep(60)

    async def get_analytics(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive market analytics for a symbol.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Dictionary containing market analytics
        """
        try:
            if symbol not in self.active_symbols:
                return None
                
            prices = [item['price'] for item in self.price_cache[symbol]]
            volumes = [item['volume'] for item in self.volume_cache[symbol]]
            
            if not prices or not volumes:
                return None
                
            # Calculate basic statistics
            current_price = prices[-1]
            price_change = (current_price - prices[0]) / prices[0] * 100
            avg_volume = np.mean(volumes)
            
            # Calculate technical indicators
            sma_20 = np.mean(prices[-20:]) if len(prices) >= 20 else None
            sma_50 = np.mean(prices[-50:]) if len(prices) >= 50 else None
            
            # Calculate price ranges
            daily_high = max(prices[-1440:]) if len(prices) >= 1440 else max(prices)
            daily_low = min(prices[-1440:]) if len(prices) >= 1440 else min(prices)
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'price_change_percent': price_change,
                'volatility': self.volatility_cache.get(symbol, 0),
                'momentum': self.momentum_cache.get(symbol, 0),
                'trend': self.trend_cache.get(symbol, 'sideways'),
                'volume': {
                    'current': volumes[-1],
                    'average': avg_volume,
                    'ratio': volumes[-1] / avg_volume if avg_volume > 0 else 1
                },
                'moving_averages': {
                    'sma_20': sma_20,
                    'sma_50': sma_50,
                    'price_to_sma20': (current_price / sma_20 - 1) * 100 if sma_20 else None,
                    'price_to_sma50': (current_price / sma_50 - 1) * 100 if sma_50 else None
                },
                'price_ranges': {
                    'daily_high': daily_high,
                    'daily_low': daily_low,
                    'daily_range': (daily_high - daily_low) / daily_low * 100
                },
                'feed_stats': {
                    'update_count': self.update_count.get(symbol, 0),
                    'error_count': self.error_count.get(symbol, 0),
                    'last_update': self.last_update_time.get(symbol)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics for {symbol}: {str(e)}")
            return None

    async def get_market_depth(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get market depth analysis for a symbol.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Dictionary containing market depth analysis
        """
        try:
            orderbook = await self.binance_ws.orderbook_manager.get_orderbook(symbol)
            if not orderbook:
                return None
                
            bids = orderbook['bids']
            asks = orderbook['asks']
            
            bid_volume = sum(float(qty) for _, qty in bids)
            ask_volume = sum(float(qty) for _, qty in asks)
            
            return {
                'symbol': symbol,
                'timestamp': datetime.utcnow(),
                'bid_ask_ratio': bid_volume / ask_volume if ask_volume > 0 else 1,
                'total_bid_volume': bid_volume,
                'total_ask_volume': ask_volume,
                'spread': (float(asks[0][0]) - float(bids[0][0])) / float(bids[0][0]) * 100,
                'depth_levels': {
                    'bids': len(bids),
                    'asks': len(asks)
                },
                'price_levels': {
                    'best_bid': float(bids[0][0]),
                    'best_ask': float(asks[0][0]),
                    'mid_price': (float(bids[0][0]) + float(asks[0][0])) / 2
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting market depth for {symbol}: {str(e)}")
            return None

    async def get_trading_signals(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Generate trading signals based on current market conditions.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Dictionary containing trading signals and indicators
        """
        try:
            analytics = await self.get_analytics(symbol)
            if not analytics:
                return None
                
            signals = {
                'symbol': symbol,
                'timestamp': datetime.utcnow(),
                'signals': [],
                'strength': 0  # Signal strength from -100 to 100
            }
            
            # Trend signals
            if analytics['trend'] == 'up':
                if analytics['momentum'] > 0:
                    signals['signals'].append('STRONG_UPTREND')
                    signals['strength'] += 30
                else:
                    signals['signals'].append('WEAK_UPTREND')
                    signals['strength'] += 10
            elif analytics['trend'] == 'down':
                if analytics['momentum'] < 0:
                    signals['signals'].append('STRONG_DOWNTREND')
                    signals['strength'] -= 30
                else:
                    signals['signals'].append('WEAK_DOWNTREND')
                    signals['strength'] -= 10
                    
            # Momentum signals
            if abs(analytics['momentum']) > 5:
                direction = 'BULLISH' if analytics['momentum'] > 0 else 'BEARISH'
                signals['signals'].append(f'STRONG_MOMENTUM_{direction}')
                signals['strength'] += 20 if direction == 'BULLISH' else -20
                
            # Volume signals
            if analytics['volume']['ratio'] > 2:
                signals['signals'].append('VOLUME_SURGE')
                signals['strength'] += 10 if analytics['price_change_percent'] > 0 else -10
                
            # Moving average signals
            if analytics['moving_averages']['sma_20'] and analytics['moving_averages']['sma_50']:
                if analytics['moving_averages']['sma_20'] > analytics['moving_averages']['sma_50']:
                    signals['signals'].append('MA_GOLDEN_CROSS')
                    signals['strength'] += 15
                elif analytics['moving_averages']['sma_20'] < analytics['moving_averages']['sma_50']:
                    signals['signals'].append('MA_DEATH_CROSS')
                    signals['strength'] -= 15
                    
            # Volatility signals
            if analytics['volatility'] > self.analytics_config['volatility']['high_threshold']:
                signals['signals'].append('HIGH_VOLATILITY')
                signals['strength'] = signals['strength'] * 0.8  # Reduce signal strength in high volatility
                
            # Ensure strength stays within bounds
            signals['strength'] = max(min(signals['strength'], 100), -100)
            
            # Add indicator values
            signals['indicators'] = {
                'trend': analytics['trend'],
                'momentum': analytics['momentum'],
                'volatility': analytics['volatility'],
                'volume_ratio': analytics['volume']['ratio'],
                'price_to_sma20': analytics['moving_averages']['price_to_sma20'],
                'price_to_sma50': analytics['moving_averages']['price_to_sma50']
            }
            
            return signals
            
        except Exception as e:
            logger.error(f"Error generating trading signals for {symbol}: {str(e)}")
            return None
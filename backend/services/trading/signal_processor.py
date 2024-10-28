from typing import Optional, Dict, Any, List
import logging
from decimal import Decimal
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
from binance.client import Client

from app.models.signal import Signal, SignalStatus, SignalSource, SignalType, SignalAction
from app.models.order import Order, OrderStatus, OrderType, OrderSide
from app.models.position import Position, PositionSide, PositionStatus
from app.schemas.signal import SignalCreate
from app.core.config import settings
from app.exchanges.binance.futures import BinanceFuturesClient
from app.core.risk.risk_management import RiskManager

logger = logging.getLogger(__name__)

class SignalProcessor:
    """
    Service for processing and executing trading signals.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.risk_manager = RiskManager(None)  # Will be set per user
        
    async def process_signal(self, signal_data: SignalCreate) -> Signal:
        """
        Process incoming trading signal.
        
        Args:
            signal_data: Signal creation data
            
        Returns:
            Created signal instance
        """
        try:
            # Validate signal data
            is_valid, message = await self._validate_signal(signal_data)
            if not is_valid:
                raise ValueError(f"Invalid signal: {message}")
            
            # Create signal record
            signal = Signal(
                user_id=signal_data.user_id,
                source=signal_data.source,
                type=signal_data.type,
                action=signal_data.action,
                symbol=signal_data.symbol,
                timeframe=signal_data.timeframe,
                price=signal_data.price,
                entry_price=signal_data.entry_price,
                stop_loss=signal_data.stop_loss,
                take_profit=signal_data.take_profit,
                quantity=signal_data.quantity,
                leverage=signal_data.leverage,
                risk_percentage=signal_data.risk_percentage,
                strategy_name=signal_data.strategy_name,
                description=signal_data.description
            )
            
            # Add technical indicators if provided
            if signal_data.indicators:
                signal.set_indicators(signal_data.indicators)
            
            # Calculate confidence score
            signal.confidence_score = await self._calculate_confidence_score(signal_data)
            
            # Set time validity if not provided
            if not signal_data.time_validity:
                signal.time_validity = self._get_default_time_validity(signal_data.timeframe)
            
            self.db.add(signal)
            self.db.commit()
            self.db.refresh(signal)
            
            return signal
            
        except Exception as e:
            logger.error(f"Error processing signal: {str(e)}")
            self.db.rollback()
            raise

    async def execute_signal_strategy(self, signal_id: int) -> None:
        """
        Execute trading strategy based on signal.
        
        Args:
            signal_id: ID of signal to execute
        """
        try:
            signal = self.db.query(Signal).filter(Signal.id == signal_id).first()
            if not signal:
                raise ValueError(f"Signal {signal_id} not found")
            
            # Initialize exchange client for user
            user = signal.user
            self.futures_client = BinanceFuturesClient(
                api_key=user.binance_api_key,
                api_secret=user.binance_api_secret,
                testnet=settings.BINANCE_TESTNET
            )
            
            # Update risk manager with user
            self.risk_manager.user = user
            
            # Check if signal is still valid
            if not signal.is_active:
                signal.status = SignalStatus.EXPIRED
                self.db.commit()
                return
            
            # Get current market data
            market_data = await self._get_market_data(signal.symbol)
            
            # Validate signal against current market conditions
            if not await self._validate_market_conditions(signal, market_data):
                signal.status = SignalStatus.CANCELLED
                self.db.commit()
                return
            
            # Check risk management rules
            if not await self._check_risk_management(signal):
                signal.status = SignalStatus.CANCELLED
                self.db.commit()
                return
            
            # Execute signal strategy
            if signal.type == SignalType.ENTRY:
                await self._execute_entry_signal(signal, market_data)
            elif signal.type == SignalType.EXIT:
                await self._execute_exit_signal(signal, market_data)
            elif signal.type in [SignalType.STOP_LOSS, SignalType.TAKE_PROFIT]:
                await self._execute_tp_sl_signal(signal, market_data)
            
            # Update signal status
            signal.status = SignalStatus.EXECUTED
            signal.execution_time = datetime.utcnow()
            
            if signal.created_at:
                signal.execution_delay = (signal.execution_time - signal.created_at).total_seconds()
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error executing signal strategy: {str(e)}")
            signal.status = SignalStatus.FAILED
            self.db.commit()
            raise

    async def _validate_signal(self, signal_data: SignalCreate) -> tuple[bool, str]:
        """
        Validate signal parameters.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Validate symbol
            symbol_info = self.futures_client.get_symbol_info(signal_data.symbol)
            if not symbol_info:
                return False, f"Invalid symbol: {signal_data.symbol}"
            
            # Validate action and type combination
            if signal_data.type == SignalType.ENTRY:
                if signal_data.action not in [SignalAction.LONG, SignalAction.SHORT]:
                    return False, "Invalid action for entry signal"
                    
                if not signal_data.entry_price or signal_data.entry_price <= 0:
                    return False, "Entry price required for entry signals"
                    
                if not signal_data.stop_loss or signal_data.stop_loss <= 0:
                    return False, "Stop loss required for entry signals"
                
            elif signal_data.type == SignalType.EXIT:
                if signal_data.action not in [SignalAction.CLOSE_LONG, SignalAction.CLOSE_SHORT]:
                    return False, "Invalid action for exit signal"
            
            # Validate price levels
            current_price = float(self.futures_client.get_symbol_price(signal_data.symbol))
            
            if signal_data.type == SignalType.ENTRY:
                if signal_data.action == SignalAction.LONG:
                    if signal_data.stop_loss >= signal_data.entry_price:
                        return False, "Stop loss must be below entry price for long positions"
                    if signal_data.take_profit and signal_data.take_profit <= signal_data.entry_price:
                        return False, "Take profit must be above entry price for long positions"
                else:  # SHORT
                    if signal_data.stop_loss <= signal_data.entry_price:
                        return False, "Stop loss must be above entry price for short positions"
                    if signal_data.take_profit and signal_data.take_profit >= signal_data.entry_price:
                        return False, "Take profit must be below entry price for short positions"
            
            # Validate risk parameters
            if signal_data.risk_percentage:
                if signal_data.risk_percentage <= 0 or signal_data.risk_percentage > 100:
                    return False, "Invalid risk percentage"
            
            if signal_data.leverage:
                max_leverage = symbol_info.get('maxLeverage', 125)
                if signal_data.leverage <= 0 or signal_data.leverage > max_leverage:
                    return False, f"Leverage must be between 1 and {max_leverage}"
            
            return True, ""
            
        except Exception as e:
            logger.error(f"Error validating signal: {str(e)}")
            return False, str(e)
        except Exception as e:
            logger.error(f"Error validating signal: {str(e)}")
            return False, str(e)

    async def _execute_entry_signal(self, signal: Signal, market_data: Dict[str, Any]) -> None:
        """
        Execute entry signal by placing appropriate orders.
        """
        try:
            # Calculate position size
            account_info = self.futures_client.get_account_info()
            available_balance = float(account_info['availableBalance'])
            
            if signal.risk_percentage:
                # Calculate size based on risk percentage
                risk_amount = available_balance * (signal.risk_percentage / 100)
                price_difference = abs(float(signal.entry_price) - float(signal.stop_loss))
                base_size = risk_amount / price_difference
                position_size = base_size * (signal.leverage or 1)
            else:
                position_size = signal.quantity
            
            # Set leverage
            if signal.leverage:
                self.futures_client.change_leverage(
                    symbol=signal.symbol,
                    leverage=signal.leverage
                )
            
            # Place entry order
            order_side = OrderSide.BUY if signal.action == SignalAction.LONG else OrderSide.SELL
            
            entry_order = await self._place_order(
                symbol=signal.symbol,
                side=order_side,
                order_type=OrderType.LIMIT if signal.entry_price else OrderType.MARKET,
                quantity=position_size,
                price=signal.entry_price,
                reduce_only=False
            )
            
            # Place stop loss order
            sl_side = OrderSide.SELL if signal.action == SignalAction.LONG else OrderSide.BUY
            
            sl_order = await self._place_order(
                symbol=signal.symbol,
                side=sl_side,
                order_type=OrderType.STOP_MARKET,
                quantity=position_size,
                stop_price=signal.stop_loss,
                reduce_only=True
            )
            
            # Place take profit order if specified
            if signal.take_profit:
                tp_order = await self._place_order(
                    symbol=signal.symbol,
                    side=sl_side,
                    order_type=OrderType.TAKE_PROFIT_MARKET,
                    quantity=position_size,
                    stop_price=signal.take_profit,
                    reduce_only=True
                )
            
            # Update signal with order information
            signal.order_id = entry_order['orderId']
            signal.executed_price = float(entry_order.get('avgPrice', signal.entry_price))
            
        except Exception as e:
            logger.error(f"Error executing entry signal: {str(e)}")
            raise

    async def _execute_exit_signal(self, signal: Signal, market_data: Dict[str, Any]) -> None:
        """
        Execute exit signal by closing position.
        """
        try:
            # Find open position
            position = self.db.query(Position).filter(
                Position.user_id == signal.user_id,
                Position.symbol == signal.symbol,
                Position.status == PositionStatus.OPEN
            ).first()
            
            if not position:
                raise ValueError(f"No open position found for {signal.symbol}")
            
            # Validate exit direction
            if (signal.action == SignalAction.CLOSE_LONG and position.side != PositionSide.LONG) or \
               (signal.action == SignalAction.CLOSE_SHORT and position.side != PositionSide.SHORT):
                raise ValueError("Exit signal direction does not match position side")
            
            # Cancel existing orders
            await self._cancel_position_orders(position)
            
            # Place closing order
            order_side = OrderSide.SELL if position.side == PositionSide.LONG else OrderSide.BUY
            
            close_order = await self._place_order(
                symbol=signal.symbol,
                side=order_side,
                order_type=OrderType.MARKET,
                quantity=position.size,
                reduce_only=True
            )
            
            # Update signal and position
            signal.order_id = close_order['orderId']
            signal.executed_price = float(close_order.get('avgPrice', market_data['price']))
            
            position.status = PositionStatus.CLOSED
            position.closed_at = datetime.utcnow()
            
            # Calculate PnL
            entry_value = position.size * position.entry_price
            exit_value = position.size * signal.executed_price
            
            if position.side == PositionSide.LONG:
                position.realized_pnl = exit_value - entry_value
            else:
                position.realized_pnl = entry_value - exit_value
            
            signal.pnl = position.realized_pnl
            if entry_value != 0:
                signal.pnl_percentage = (position.realized_pnl / entry_value) * 100
            
            signal.success = bool(position.realized_pnl > 0)
            
        except Exception as e:
            logger.error(f"Error executing exit signal: {str(e)}")
            raise

    async def _execute_tp_sl_signal(self, signal: Signal, market_data: Dict[str, Any]) -> None:
        """
        Execute take profit or stop loss signal.
        """
        try:
            # Find relevant position
            position = self.db.query(Position).filter(
                Position.user_id == signal.user_id,
                Position.symbol == signal.symbol,
                Position.status == PositionStatus.OPEN
            ).first()
            
            if not position:
                raise ValueError(f"No open position found for {signal.symbol}")
            
            # Update stop loss or take profit
            if signal.type == SignalType.STOP_LOSS:
                await self._update_stop_loss(position, signal.price)
            else:  # TAKE_PROFIT
                await self._update_take_profit(position, signal.price)
            
            signal.executed_price = signal.price
            
        except Exception as e:
            logger.error(f"Error executing TP/SL signal: {str(e)}")
            raise

    async def _calculate_confidence_score(self, signal_data: SignalCreate) -> float:
        """
        Calculate signal confidence score based on multiple factors.
        """
        try:
            score = 50.0  # Base score
            
            # Get technical indicators
            indicators = await self._get_technical_indicators(
                signal_data.symbol,
                signal_data.timeframe
            )
            
            # Analyze trend alignment
            trend_score = await self._analyze_trend_alignment(
                signal_data,
                indicators
            )
            score += trend_score * 0.3  # 30% weight
            
            # Analyze volume profile
            volume_score = await self._analyze_volume_profile(
                signal_data.symbol,
                indicators
            )
            score += volume_score * 0.2  # 20% weight
            
            # Analyze price action
            price_score = await self._analyze_price_action(
                signal_data,
                indicators
            )
            score += price_score * 0.3  # 30% weight
            
            # Analyze market conditions
            market_score = await self._analyze_market_conditions(
                signal_data.symbol
            )
            score += market_score * 0.2  # 20% weight
            
            return min(max(score, 0), 100)  # Ensure score is between 0 and 100
            
        except Exception as e:
            logger.error(f"Error calculating confidence score: {str(e)}")
            return 50.0  # Return base score on error

    async def _get_technical_indicators(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """
        Calculate technical indicators for analysis.
        """
        try:
            # Get historical klines data
            klines = self.futures_client.get_klines(
                symbol=symbol,
                interval=timeframe,
                limit=100
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            df[['open', 'high', 'low', 'close', 'volume']] = df[
                ['open', 'high', 'low', 'close', 'volume']
            ].astype(float)
            
            # Calculate indicators
            indicators = {
                'sma_20': df['close'].rolling(20).mean().iloc[-1],
                'sma_50': df['close'].rolling(50).mean().iloc[-1],
                'rsi_14': self._calculate_rsi(df['close'], 14).iloc[-1],
                'macd': self._calculate_macd(df['close']),
                'bollinger_bands': self._calculate_bollinger_bands(df['close']),
                'atr': self._calculate_atr(df['high'], df['low'], df['close']).iloc[-1],
                'volume_sma': df['volume'].rolling(20).mean().iloc[-1],
                'current_volume': df['volume'].iloc[-1]
            }
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {str(e)}")
            raise

    @staticmethod
    def _calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def _calculate_macd(prices: pd.Series) -> Dict[str, float]:
        """Calculate MACD indicator."""
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        return {
            'macd': macd.iloc[-1],
            'signal': signal.iloc[-1],
            'histogram': histogram.iloc[-1]
        }

    @staticmethod
    def _calculate_bollinger_bands(prices: pd.Series, period: int = 20) -> Dict[str, float]:
        """Calculate Bollinger Bands."""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)
        return {
            'upper': upper_band.iloc[-1],
            'middle': sma.iloc[-1],
            'lower': lower_band.iloc[-1]
        }

    @staticmethod
    def _calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Average True Range."""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()

    def _get_default_time_validity(self, timeframe: str) -> int:
        """
        Get default time validity in minutes based on timeframe.
        """
        timeframe_minutes = {
            '1m': 5,
            '3m': 15,
            '5m': 25,
            '15m': 75,
            '30m': 150,
            '1h': 300,
            '2h': 600,
            '4h': 1200,
            '6h': 1800,
            '8h': 2400,
            '12h': 3600,
            '1d': 7200
        }
        return timeframe_minutes.get(timeframe, 60)  # Default 60 minutes

    async def _get_market_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get current market data including price and market depth.
        """
        try:
            market_data = {
                'price': float(self.futures_client.get_mark_price(symbol)['markPrice']),
                'book': self.futures_client.get_order_book(symbol),
                'ticker': self.futures_client.get_24h_ticker(symbol),
                'funding_rate': float(self.futures_client.get_funding_rate(symbol)['fundingRate']),
                'open_interest': float(self.futures_client.get_open_interest(symbol)['openInterest'])
            }
            
            # Add market depth analysis
            depth = market_data['book']
            total_bid_volume = sum(float(level[1]) for level in depth['bids'][:10])
            total_ask_volume = sum(float(level[1]) for level in depth['asks'][:10])
            
            market_data['buy_sell_ratio'] = total_bid_volume / total_ask_volume if total_ask_volume > 0 else 1
            market_data['market_depth'] = {
                'bid_volume': total_bid_volume,
                'ask_volume': total_ask_volume,
                'spread': (float(depth['asks'][0][0]) - float(depth['bids'][0][0])) / float(depth['bids'][0][0]) * 100
            }
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error getting market data: {str(e)}")
            raise

    async def _validate_market_conditions(self, signal: Signal, market_data: Dict[str, Any]) -> bool:
        """
        Validate if current market conditions are suitable for signal execution.
        """
        try:
            # Check if price is within valid range
            current_price = market_data['price']
            if signal.type == SignalType.ENTRY:
                price_diff = abs(current_price - signal.entry_price) / signal.entry_price
                if price_diff > 0.01:  # 1% price deviation threshold
                    logger.warning(f"Price deviation too large: {price_diff*100}%")
                    return False
            
            # Check market volatility
            ticker = market_data['ticker']
            price_change = abs(float(ticker['priceChangePercent']))
            if price_change > 5:  # 5% price change threshold
                logger.warning(f"Market too volatile: {price_change}% change")
                return False
            
            # Check trading volume
            if float(ticker['volume']) < market_data['market_depth']['bid_volume'] * 100:
                logger.warning("Insufficient market liquidity")
                return False
            
            # Check spread
            if market_data['market_depth']['spread'] > 0.1:  # 0.1% spread threshold
                logger.warning(f"Spread too high: {market_data['market_depth']['spread']}%")
                return False
            
            # Check funding rate for futures
            if abs(market_data['funding_rate']) > 0.001:  # 0.1% funding rate threshold
                logger.warning(f"High funding rate: {market_data['funding_rate']}%")
                return False
            
            # Check buy/sell ratio
            if signal.action == SignalAction.LONG and market_data['buy_sell_ratio'] < 0.8:
                logger.warning("Weak buying pressure for long position")
                return False
            elif signal.action == SignalAction.SHORT and market_data['buy_sell_ratio'] > 1.2:
                logger.warning("Weak selling pressure for short position")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating market conditions: {str(e)}")
            return False

    async def _check_risk_management(self, signal: Signal) -> bool:
        """
        Check if signal complies with risk management rules.
        """
        try:
            # Get account information
            account_info = self.futures_client.get_account_info()
            available_balance = float(account_info['availableBalance'])
            total_margin = float(account_info['totalMarginBalance'])
            
            # Check account health
            margin_ratio = float(account_info['totalMaintMargin']) / total_margin if total_margin > 0 else 0
            if margin_ratio > 0.8:  # 80% margin usage threshold
                logger.warning(f"High margin usage: {margin_ratio*100}%")
                return False
            
            # Check position sizing
            if signal.quantity:
                position_value = signal.quantity * signal.entry_price
                account_risk = position_value / available_balance
                if account_risk > 0.1:  # 10% account risk threshold
                    logger.warning(f"Position size too large: {account_risk*100}% of account")
                    return False
            
            # Check existing positions
            open_positions = self.db.query(Position).filter(
                Position.user_id == signal.user_id,
                Position.status == PositionStatus.OPEN
            ).all()
            
            total_exposure = sum(p.size * p.mark_price for p in open_positions)
            if total_exposure > available_balance * 2:  # 200% account exposure threshold
                logger.warning("Total exposure too high")
                return False
            
            # Check correlation risk
            if not await self._check_correlation_risk(signal, open_positions):
                return False
            
            # Check maximum positions
            if len(open_positions) >= 10:  # Maximum 10 concurrent positions
                logger.warning("Maximum number of positions reached")
                return False
            
            # Check drawdown
            daily_pnl = await self._calculate_daily_pnl(signal.user_id)
            if daily_pnl < -0.1 * available_balance:  # 10% daily drawdown threshold
                logger.warning(f"Daily drawdown threshold reached: {daily_pnl}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking risk management: {str(e)}")
            return False

    async def _place_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        reduce_only: bool = False
    ) -> Dict[str, Any]:
        """
        Place order on exchange with retry logic.
        """
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                params = {
                    'symbol': symbol,
                    'side': side.value,
                    'type': order_type.value,
                    'quantity': quantity,
                    'reduceOnly': reduce_only
                }
                
                if price:
                    params['price'] = price
                if stop_price:
                    params['stopPrice'] = stop_price
                    
                response = self.futures_client.create_order(**params)
                logger.info(f"Order placed successfully: {response['orderId']}")
                return response
                
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Order attempt {attempt + 1} failed: {str(e)}")
                await asyncio.sleep(retry_delay)

    async def _cancel_position_orders(self, position: Position) -> None:
        """Cancel all orders associated with position."""
        try:
            self.futures_client.cancel_all_orders(symbol=position.symbol)
        except Exception as e:
            logger.error(f"Error canceling position orders: {str(e)}")
            raise

    async def _check_correlation_risk(
        self,
        signal: Signal,
        open_positions: List[Position]
    ) -> bool:
        """
        Check correlation risk with existing positions.
        """
        if not open_positions:
            return True
            
        try:
            # Get price correlation matrix
            symbols = [p.symbol for p in open_positions] + [signal.symbol]
            correlation = await self._calculate_correlation_matrix(symbols)
            
            # Check correlation threshold
            for pos in open_positions:
                if pos.symbol in correlation and signal.symbol in correlation:
                    corr = abs(correlation[pos.symbol][signal.symbol])
                    if corr > 0.8:  # 80% correlation threshold
                        logger.warning(f"High correlation ({corr}) between {signal.symbol} and {pos.symbol}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking correlation risk: {str(e)}")
            return True  # Allow trade on correlation check error

    async def _calculate_correlation_matrix(self, symbols: List[str], timeframe: str = '1d') -> Dict[str, Dict[str, float]]:
        """Calculate price correlation matrix for symbols."""
        try:
            price_data = {}
            for symbol in symbols:
                klines = self.futures_client.get_klines(symbol=symbol, interval=timeframe, limit=30)
                prices = [float(k[4]) for k in klines]  # Close prices
                price_data[symbol] = prices
                
            df = pd.DataFrame(price_data)
            correlation = df.corr().to_dict()
            return correlation
            
        except Exception as e:
            logger.error(f"Error calculating correlation matrix: {str(e)}")
            return {}

    async def _calculate_daily_pnl(self, user_id: int) -> float:
        """Calculate total daily PnL."""
        try:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Get realized PnL from closed positions
            closed_positions = self.db.query(Position).filter(
                Position.user_id == user_id,
                Position.closed_at >= today_start,
                Position.status == PositionStatus.CLOSED
            ).all()
            
            realized_pnl = sum(p.realized_pnl or 0 for p in closed_positions)
            
            # Get unrealized PnL from open positions
            open_positions = self.db.query(Position).filter(
                Position.user_id == user_id,
                Position.status == PositionStatus.OPEN
            ).all()
            
            unrealized_pnl = sum(p.unrealized_pnl or 0 for p in open_positions)
            
            return realized_pnl + unrealized_pnl
            
        except Exception as e:
            logger.error(f"Error calculating daily PnL: {str(e)}")
            return 0.0
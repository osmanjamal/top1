from decimal import Decimal
from typing import Optional

from app.core.config import settings
from app.models.position import Position
from app.models.user import User

class PositionSizingManager:
    """
    Manager for calculating and validating position sizes.
    """
    
    def __init__(self, user: User):
        self.user = user
        self.max_position_size = Decimal(str(settings.MAX_POSITION_SIZE))
        self.max_leverage = settings.MAX_LEVERAGE

    def calculate_position_size(
        self,
        account_balance: Decimal,
        risk_per_trade: Decimal,
        stop_loss_pct: Decimal,
        leverage: Optional[int] = 1
    ) -> Decimal:
        """
        Calculate position size based on account balance and risk parameters.
        
        Args:
            account_balance: Total account balance
            risk_per_trade: Percentage of account to risk per trade (decimal)
            stop_loss_pct: Stop loss percentage (decimal)
            leverage: Position leverage (default: 1)
            
        Returns:
            Calculated position size in quote currency
        """
        if leverage > self.max_leverage:
            raise ValueError(f"Leverage exceeds maximum allowed: {self.max_leverage}")
        
        # Calculate maximum loss amount
        max_risk_amount = account_balance * risk_per_trade
        
        # Calculate position size based on stop loss
        position_size = (max_risk_amount / stop_loss_pct) * leverage
        
        # Check against maximum position size
        max_allowed_size = account_balance * self.max_position_size * leverage
        if position_size > max_allowed_size:
            position_size = max_allowed_size
            
        return position_size

    def validate_position_size(
        self,
        position_size: Decimal,
        account_balance: Decimal,
        leverage: Optional[int] = 1
    ) -> bool:
        """
        Validate if position size is within allowed limits.
        """
        max_allowed_size = account_balance * self.max_position_size * leverage
        return position_size <= max_allowed_size

    def adjust_for_correlation(
        self,
        position_size: Decimal,
        symbol: str,
        account_balance: Decimal
    ) -> Decimal:
        """
        Adjust position size based on correlation with existing positions.
        """
        # Get correlated positions
        correlated_exposure = self._get_correlated_exposure(symbol)
        
        # Adjust position size if total exposure exceeds limits
        max_allowed_exposure = account_balance * self.max_position_size
        if (position_size + correlated_exposure) > max_allowed_exposure:
            position_size = max_allowed_exposure - correlated_exposure
            
        return max(position_size, Decimal('0'))

    def calculate_pyramid_size(
        self,
        current_position: Position,
        account_balance: Decimal,
        profit_threshold: Decimal = Decimal('0.02')  # 2%
    ) -> Optional[Decimal]:
        """
        Calculate pyramid (position increase) size based on current profit.
        """
        if current_position.unrealized_pnl_pct < profit_threshold:
            return None
            
        # Calculate additional size based on profit
        additional_size = current_position.size * (
            current_position.unrealized_pnl_pct / profit_threshold
        ) * Decimal('0.5')  # 50% of theoretical increase
        
        # Validate against maximum position size
        total_size = current_position.size + additional_size
        if not self.validate_position_size(total_size, account_balance):
            return None
            
        return additional_size

    def calculate_dp_size(
        self,
        price: Decimal,
        account_balance: Decimal,
        interval_pct: Decimal = Decimal('0.02'),  # 2%
        num_orders: int = 5
    ) -> list[tuple[Decimal, Decimal]]:
        """
        Calculate dollar-cost averaging position sizes and prices.
        """
        base_position_size = self.calculate_position_size(
            account_balance=account_balance,
            risk_per_trade=self.max_position_size / num_orders,
            stop_loss_pct=interval_pct
        )
        
        positions = []
        for i in range(num_orders):
            entry_price = price * (Decimal('1') - (interval_pct * i))
            positions.append((entry_price, base_position_size))
            
        return positions

    def _get_correlated_exposure(self, symbol: str) -> Decimal:
        """
        Calculate total exposure from correlated positions.
        """
        # Implement correlation calculation logic
        return Decimal('0')

    def _validate_risk_parameters(
        self,
        risk_per_trade: Decimal,
        stop_loss_pct: Decimal,
        leverage: int
    ) -> bool:
        """
        Validate risk parameters are within acceptable ranges.
        """
        if risk_per_trade > self.max_position_size:
            return False
        if leverage > self.max_leverage:
            return False
        if stop_loss_pct > Decimal('0.1'):  # 10% maximum stop loss
            return False
        return True
export const POSITION_SIDES = {
    LONG: 'LONG',
    SHORT: 'SHORT',
    BOTH: 'BOTH'  // For hedge mode
  } as const;
  
  export const POSITION_STATUS = {
    OPEN: 'OPEN',
    CLOSED: 'CLOSED',
    LIQUIDATED: 'LIQUIDATED',
    PENDING_CLOSE: 'PENDING_CLOSE'
  } as const;
  
  export const MARGIN_TYPES = {
    ISOLATED: 'ISOLATED',
    CROSSED: 'CROSSED'
  } as const;
  
  export const POSITION_MODE = {
    ONE_WAY: 'ONE_WAY',
    HEDGE: 'HEDGE'
  } as const;
  
  export const LEVERAGE_BRACKETS = {
    TIER_1: { bracket: 1, leverage: 125, minNotional: 0, maxNotional: 10000 },
    TIER_2: { bracket: 2, leverage: 100, minNotional: 10000, maxNotional: 50000 },
    TIER_3: { bracket: 3, leverage: 75, minNotional: 50000, maxNotional: 250000 },
    TIER_4: { bracket: 4, leverage: 50, minNotional: 250000, maxNotional: 1000000 },
    TIER_5: { bracket: 5, leverage: 25, minNotional: 1000000, maxNotional: 5000000 },
    TIER_6: { bracket: 6, leverage: 10, minNotional: 5000000, maxNotional: Infinity }
  } as const;
  
  export const RISK_LIMITS = {
    LEVERAGE: {
      MIN: 1,
      MAX: 125,
      DEFAULT: 20
    },
    MARGIN_RATIO: {
      WARNING: 0.8,    // 80% margin usage
      DANGER: 0.9,     // 90% margin usage
      LIQUIDATION: 0.975  // 97.5% margin usage
    },
    POSITION_SIZE: {
      MAX_SINGLE_POSITION: 0.2,  // 20% of account balance
      MAX_TOTAL_POSITIONS: 0.5   // 50% of account balance
    },
    DRAWDOWN: {
      MAX_POSITION_DRAWDOWN: 0.2,  // 20% position drawdown
      MAX_ACCOUNT_DRAWDOWN: 0.5    // 50% account drawdown
    }
  } as const;
  
  export const STOP_TYPES = {
    STOP_LOSS: 'STOP_LOSS',
    TAKE_PROFIT: 'TAKE_PROFIT',
    TRAILING_STOP: 'TRAILING_STOP'
  } as const;
  
  export const POSITION_EVENTS = {
    OPEN: 'POSITION_OPEN',
    UPDATE: 'POSITION_UPDATE',
    CLOSE: 'POSITION_CLOSE',
    LIQUIDATION: 'POSITION_LIQUIDATION',
    MARGIN_CALL: 'MARGIN_CALL',
    ADL_WARNING: 'ADL_WARNING'  // Auto-Deleveraging Warning
  } as const;
  
  export const MARGIN_CALL_LEVELS = {
    WARNING: 'WARNING',      // First warning level
    CRITICAL: 'CRITICAL',    // Critical level, close to liquidation
    LIQUIDATION: 'LIQUIDATION'  // Liquidation imminent
  } as const;
  
  export const PNL_TYPES = {
    REALIZED: 'REALIZED',
    UNREALIZED: 'UNREALIZED'
  } as const;
  
  export const POSITION_METRICS = {
    LEVERAGE_TIERS: [1, 2, 3, 5, 10, 20, 50, 75, 100, 125],
    ROE_THRESHOLDS: {
      EXCELLENT: 50,  // >50% ROE
      GOOD: 20,      // >20% ROE
      AVERAGE: 5,    // >5% ROE
      POOR: 0        // ≤0% ROE
    },
    RISK_SCORES: {
      LOW: 'LOW',           // Conservative position
      MEDIUM: 'MEDIUM',     // Balanced position
      HIGH: 'HIGH',         // Aggressive position
      EXTREME: 'EXTREME'    // Very risky position
    }
  } as const;
  
  export const POSITION_ERRORS = {
    INSUFFICIENT_MARGIN: 'Insufficient margin for position',
    MAX_LEVERAGE_EXCEEDED: 'Maximum leverage exceeded',
    MAX_POSITION_SIZE_EXCEEDED: 'Maximum position size exceeded',
    INVALID_LEVERAGE: 'Invalid leverage value',
    INVALID_MARGIN_TYPE: 'Invalid margin type',
    POSITION_NOT_FOUND: 'Position not found',
    ALREADY_EXISTS: 'Position already exists',
    LIQUIDATION_IN_PROGRESS: 'Position is being liquidated',
    ADL_IN_PROGRESS: 'Position is being auto-deleveraged'
  } as const;
  
  export const FUNDING_RATE_THRESHOLDS = {
    HIGH_POSITIVE: 0.001,   // 0.1% positive funding rate
    HIGH_NEGATIVE: -0.001,  // 0.1% negative funding rate
    EXTREME_POSITIVE: 0.003, // 0.3% positive funding rate
    EXTREME_NEGATIVE: -0.003 // 0.3% negative funding rate
  } as const;
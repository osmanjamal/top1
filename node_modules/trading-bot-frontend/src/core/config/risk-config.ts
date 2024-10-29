export const RISK_CONFIG = {
    // Position Size Management
    positionSizing: {
      maxRiskPerTrade: 0.02, // Maximum 2% risk per trade
      maxTotalRisk: 0.10,    // Maximum 10% total portfolio risk
      maxDrawdown: 0.20,     // Maximum 20% drawdown before stopping
      positionSizeMultipliers: {
        lowRisk: 0.5,        // 50% of standard position size
        standardRisk: 1.0,   // Standard position size
        highRisk: 1.5        // 150% of standard position size
      }
    },
  
    // Leverage Management
    leverage: {
      maxLeverageByVolatility: {
        lowVol: 100,         // Maximum leverage for low volatility assets
        mediumVol: 50,       // Maximum leverage for medium volatility assets
        highVol: 20          // Maximum leverage for high volatility assets
      },
      marginRequirements: {
        isolated: {
          minimum: 0.10,     // 10% minimum margin for isolated
          recommended: 0.15  // 15% recommended margin for isolated
        },
        cross: {
          minimum: 0.05,     // 5% minimum margin for cross
          recommended: 0.10  // 10% recommended margin for cross
        }
      }
    },
  
    // Stop Loss Configuration
    stopLoss: {
      default: {
        percentage: 0.05,    // 5% default stop loss
        atrMultiplier: 2     // 2x ATR for dynamic stop loss
      },
      trailing: {
        activation: 0.01,    // 1% profit to activate trailing stop
        callback: 0.005     // 0.5% callback rate
      },
      dynamicAdjustment: {
        volatilityBased: true,
        minDistance: 0.01,   // 1% minimum distance
        maxDistance: 0.10    // 10% maximum distance
      }
    },
  
    // Take Profit Configuration
    takeProfit: {
      default: {
        percentage: 0.15,    // 15% default take profit
        riskRewardRatio: 3   // 3:1 risk-reward ratio
      },
      scaling: {
        levels: [0.33, 0.66, 1], // Scale out at 33%, 66%, and 100% of target
        portions: [0.3, 0.3, 0.4] // Portion of position to close at each level
      }
    },
  
    // Risk Scoring
    riskScoring: {
      factors: {
        volatility: 0.3,     // 30% weight for volatility
        volume: 0.2,         // 20% weight for volume
        momentum: 0.2,       // 20% weight for momentum
        correlation: 0.15,   // 15% weight for correlation
        liquidity: 0.15      // 15% weight for liquidity
      },
      thresholds: {
        low: 0.3,           // Score below 0.3 is low risk
        medium: 0.6,        // Score below 0.6 is medium risk
        high: 0.8           // Score below 0.8 is high risk
                           // Score above 0.8 is extreme risk
      }
    },
  
    // Portfolio Management
    portfolio: {
      maxExposurePerAsset: 0.20,     // Maximum 20% exposure per asset
      maxExposurePerSector: 0.40,     // Maximum 40% exposure per sector
      correlationLimits: {
        maxPositiveCorrelation: 0.7,  // Maximum allowed positive correlation
        minNegativeCorrelation: -0.3  // Minimum required negative correlation
      },
      rebalancing: {
        threshold: 0.05,              // 5% deviation triggers rebalancing
        frequency: 'weekly'           // Rebalancing frequency
      }
    },
  
    // Risk Alerts
    alerts: {
      marginLevel: {
        warning: 0.8,       // 80% margin usage warning
        critical: 0.9       // 90% margin usage critical alert
      },
      drawdown: {
        warning: 0.15,      // 15% drawdown warning
        critical: 0.20      // 20% drawdown critical alert
      },
      volatility: {
        warning: 1.5,       // 1.5x normal volatility warning
        critical: 2.0       // 2.0x normal volatility critical alert
      }
    },
  
    // Trading Hours Risk Adjustment
    tradingHours: {
      highRiskHours: ['00:00-02:00', '12:00-14:00', '20:00-22:00'],
      positionSizeAdjustment: 0.7,    // Reduce position size to 70% during high risk hours
      leverageAdjustment: 0.5         // Reduce leverage to 50% during high risk hours
    }
  } as const;
  
  // Utility functions
  export const calculatePositionSize = (
    accountBalance: number,
    riskLevel: keyof typeof RISK_CONFIG.positionSizing.positionSizeMultipliers
  ): number => {
    const baseRisk = RISK_CONFIG.positionSizing.maxRiskPerTrade;
    const multiplier = RISK_CONFIG.positionSizing.positionSizeMultipliers[riskLevel];
    return accountBalance * baseRisk * multiplier;
  };
  
  export const calculateMaxLeverage = (
    volatility: 'lowVol' | 'mediumVol' | 'highVol'
  ): number => {
    return RISK_CONFIG.leverage.maxLeverageByVolatility[volatility];
  };
  
  export const getRiskScore = (factors: {
    volatility: number;
    volume: number;
    momentum: number;
    correlation: number;
    liquidity: number;
  }): number => {
    const weights = RISK_CONFIG.riskScoring.factors;
    return Object.entries(factors).reduce((score, [factor, value]) => {
      const weight = weights[factor as keyof typeof weights];
      return score + (value * weight);
    }, 0);
  };
  
  export default RISK_CONFIG;
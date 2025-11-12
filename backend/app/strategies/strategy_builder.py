"""Strategy builder for dynamic strategy creation."""

import json
from typing import Dict, Any, Optional, List
from app.strategies.base_strategy import BaseStrategy
from app.strategies.templates import (
    MACrossoverStrategy, RSIDivergenceStrategy, BollingerBreakoutStrategy,
    MACDSignalStrategy, StochasticStrategy, IchimokuStrategy, ScalpingStrategy,
    SupportResistanceStrategy, FibonacciStrategy, RangeTradingStrategy,
    BreakoutStrategy, MeanReversionStrategy, MomentumStrategy, GridTradingStrategy,
    MartingaleStrategy, PivotPointStrategy, TripleScreenStrategy, TurtleStrategy,
    SessionBreakoutStrategy
)
from app.utils.logger import logger


# Strategy registry
STRATEGY_REGISTRY = {
    "ma_crossover": MACrossoverStrategy,
    "rsi_divergence": RSIDivergenceStrategy,
    "bollinger_breakout": BollingerBreakoutStrategy,
    "macd_signal": MACDSignalStrategy,
    "stochastic": StochasticStrategy,
    "ichimoku": IchimokuStrategy,
    "scalping": ScalpingStrategy,
    "support_resistance": SupportResistanceStrategy,
    "fibonacci": FibonacciStrategy,
    "range_trading": RangeTradingStrategy,
    "breakout": BreakoutStrategy,
    "mean_reversion": MeanReversionStrategy,
    "momentum": MomentumStrategy,
    "grid_trading": GridTradingStrategy,
    "martingale": MartingaleStrategy,
    "pivot_points": PivotPointStrategy,
    "triple_screen": TripleScreenStrategy,
    "turtle": TurtleStrategy,
    "session_breakout": SessionBreakoutStrategy,
}


class StrategyBuilder:
    """Builds strategies from configuration."""
    
    @staticmethod
    def create_strategy(strategy_type: str, params: Optional[Dict[str, Any]] = None) -> BaseStrategy:
        """
        Create a strategy instance.
        
        Args:
            strategy_type: Strategy type name
            params: Strategy parameters
        
        Returns:
            Strategy instance
        """
        if strategy_type not in STRATEGY_REGISTRY:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
        
        strategy_class = STRATEGY_REGISTRY[strategy_type]
        return strategy_class(params or {})
    
    @staticmethod
    def create_from_json(config: Dict[str, Any]) -> BaseStrategy:
        """
        Create strategy from JSON configuration.
        
        Args:
            config: Strategy configuration dictionary
        
        Returns:
            Strategy instance
        """
        strategy_type = config.get("type")
        params = config.get("params", {})
        return StrategyBuilder.create_strategy(strategy_type, params)
    
    @staticmethod
    def create_from_file(filepath: str) -> BaseStrategy:
        """
        Create strategy from JSON file.
        
        Args:
            filepath: Path to JSON file
        
        Returns:
            Strategy instance
        """
        with open(filepath, 'r') as f:
            config = json.load(f)
        return StrategyBuilder.create_from_json(config)
    
    @staticmethod
    def save_strategy(strategy: BaseStrategy, filepath: str) -> None:
        """
        Save strategy configuration to JSON file.
        
        Args:
            strategy: Strategy instance
            filepath: Path to save file
        """
        config = {
            "type": strategy.name.lower().replace("strategy", ""),
            "params": strategy.params,
            "description": strategy.__doc__ or ""
        }
        
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Strategy saved to {filepath}")
    
    @staticmethod
    def list_available_strategies() -> List[Dict[str, Any]]:
        """
        List all available strategies.
        
        Returns:
            List of strategy information dictionaries
        """
        strategies = []
        for name, strategy_class in STRATEGY_REGISTRY.items():
            # Create instance to get default params
            instance = strategy_class()
            strategies.append({
                "name": name,
                "class_name": strategy_class.__name__,
                "description": strategy_class.__doc__ or "No description",
                "default_params": instance.get_default_params()
            })
        return strategies
    
    @staticmethod
    def validate_strategy_config(config: Dict[str, Any]) -> bool:
        """
        Validate strategy configuration.
        
        Args:
            config: Strategy configuration
        
        Returns:
            True if valid, raises exception if invalid
        """
        if "type" not in config:
            raise ValueError("Strategy config must include 'type'")
        
        if config["type"] not in STRATEGY_REGISTRY:
            raise ValueError(f"Unknown strategy type: {config['type']}")
        
        # Try to create strategy to validate params
        try:
            StrategyBuilder.create_from_json(config)
        except Exception as e:
            raise ValueError(f"Invalid strategy configuration: {e}")
        
        return True


def create_custom_strategy(code: str) -> BaseStrategy:
    """
    Create custom strategy from Python code.
    
    Args:
        code: Python code string defining strategy class
    
    Returns:
        Strategy instance
    
    WARNING: This executes user code. Use with caution in production.
    """
    # In production, use a sandboxed environment
    namespace = {
        "BaseStrategy": BaseStrategy,
        "__builtins__": __builtins__
    }
    
    exec(code, namespace)
    
    # Find strategy class
    for key, value in namespace.items():
        if isinstance(value, type) and issubclass(value, BaseStrategy) and value != BaseStrategy:
            return value()
    
    raise ValueError("No valid strategy class found in code")


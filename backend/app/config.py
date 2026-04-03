"""Application configuration using Pydantic Settings."""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, model_validator
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://trading_user:trading_pass@localhost:5432/trading_db",
        description="PostgreSQL database URL"
    )
    REDIS_URL: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL"
    )
    
    # Data Providers
    OANDA_API_KEY: str = Field(
        default="",
        description="OANDA API key for live data"
    )
    OANDA_ACCOUNT_ID: str = Field(
        default="",
        description="OANDA account ID"
    )
    ALPHA_VANTAGE_API_KEY: str = Field(
        default="",
        description="Alpha Vantage API key (backup data provider)"
    )
    
    # Application
    APP_ENV: str = Field(
        default="development",
        description="Application environment"
    )
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level"
    )
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Comma-separated list of allowed CORS origins"
    )
    
    # Security
    JWT_SECRET: str = Field(
        default="your_jwt_secret_here_change_in_production",
        description="JWT secret key"
    )
    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="JWT algorithm"
    )
    JWT_EXPIRATION: int = Field(
        default=3600,
        description="JWT expiration time in seconds"
    )
    
    # Trading Settings
    DEFAULT_INITIAL_CAPITAL: float = Field(
        default=10000.0,
        description="Default initial capital for backtesting"
    )
    DEFAULT_COMMISSION: float = Field(
        default=0.0001,
        description="Default commission rate"
    )
    DEFAULT_SLIPPAGE: float = Field(
        default=0.0001,
        description="Default slippage rate"
    )
    MAX_POSITIONS: int = Field(
        default=5,
        description="Maximum concurrent positions"
    )
    MAX_DAILY_LOSS: float = Field(
        default=500.0,
        description="Maximum daily loss limit"
    )
    
    # AI Advisor — provider selection
    AI_PROVIDER: str = Field(
        default="openrouter",
        description="AI provider: 'openrouter', 'anthropic', or 'openai'"
    )
    AI_MODEL: str = Field(
        default="",
        description="Model override (leave blank to use provider default)"
    )

    # OpenRouter
    OPENROUTER_API_KEY: str = Field(default="", description="OpenRouter API key")
    OPENROUTER_MODEL: str = Field(
        default="meta-llama/llama-3.1-8b-instruct:free",
        description="OpenRouter model (legacy, used if AI_MODEL is blank)"
    )

    # Anthropic direct
    ANTHROPIC_API_KEY: str = Field(default="", description="Anthropic API key (sk-ant-...)")

    # OpenAI direct
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key (sk-...)")

    # Telegram Notifications
    TELEGRAM_BOT_TOKEN: str = Field(
        default="",
        description="Telegram bot token from @BotFather"
    )
    TELEGRAM_CHAT_ID: str = Field(
        default="",
        description="Your Telegram chat ID (use @userinfobot to find it)"
    )
    TELEGRAM_MIN_PRIORITY: str = Field(
        default="opportunity",
        description="Minimum priority for Telegram: 'info', 'opportunity', 'warning'"
    )

    # Signal Engine
    SIGNAL_SCAN_INTERVAL: int = Field(
        default=30,
        description="How often (seconds) to scan for new signals"
    )
    ACTIVE_PAIRS: str = Field(
        default="GBP_USD,EUR_USD,USD_JPY,USD_CHF,AUD_USD,USD_CAD",
        description="Comma-separated list of pairs to scan for signals"
    )
    ACTIVE_STRATEGIES: str = Field(
        default="asian_range_breakout,session_breakout,triple_screen",
        description="Fallback strategies if a pair has no specific config"
    )
    DEFAULT_RISK_PER_TRADE_PCT: float = Field(
        default=1.0,
        description="Default % of balance to risk per trade"
    )

    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()

    @field_validator("OANDA_API_KEY", "OANDA_ACCOUNT_ID")
    @classmethod
    def validate_oanda_credentials(cls, v: str) -> str:
        if os.getenv("APP_ENV") == "production" and not v:
            raise ValueError("OANDA credentials are required in production")
        return v
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


# Global settings instance
settings = Settings()


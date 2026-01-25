"""
Incidex Configuration Module

Loads configuration from environment variables with support for .env files.
All secrets should be stored in environment variables, never hardcoded.

Required environment variables:
- OPENAI_API_KEY: OpenAI API key for GPT-4 incident extraction

Optional environment variables:
- REPORT_SIGNING_KEY: Secret key for signing approval tokens
- SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM: Email settings
- DISCORD_WEBHOOK_URL: Discord webhook for alerts
- REVIEWER_EMAILS: Comma-separated list of reviewer email addresses
- INCIDEX_BASE_URL: Base URL for the Incidex site (default: https://incidex.au)
"""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def _load_env_file():
    """
    Load environment variables from .env file if it exists.
    Does not override existing environment variables.
    """
    env_file = Path(__file__).parent / '.env'

    if not env_file.exists():
        return

    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue

                # Parse KEY=value
                if '=' not in line:
                    logger.warning(f".env line {line_num}: Invalid format (no '=' found)")
                    continue

                key, _, value = line.partition('=')
                key = key.strip()
                value = value.strip()

                # Remove surrounding quotes if present
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]

                # Only set if not already in environment
                if key not in os.environ:
                    os.environ[key] = value

    except Exception as e:
        logger.warning(f"Error loading .env file: {e}")


def _get_required_env(key: str) -> str:
    """Get a required environment variable, raising if not found."""
    value = os.environ.get(key)
    if not value:
        raise EnvironmentError(
            f"Required environment variable '{key}' is not set. "
            f"Please set it in your environment or create a .env file. "
            f"See .env.example for reference."
        )
    return value


def _get_optional_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get an optional environment variable with a default value."""
    return os.environ.get(key, default)


def _get_int_env(key: str, default: int) -> int:
    """Get an integer environment variable with a default value."""
    value = os.environ.get(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        logger.warning(f"Invalid integer value for {key}: {value}, using default: {default}")
        return default


def _get_bool_env(key: str, default: bool = False) -> bool:
    """Get a boolean environment variable with a default value."""
    value = os.environ.get(key, '').lower()
    if value in ('true', '1', 'yes', 'on'):
        return True
    if value in ('false', '0', 'no', 'off'):
        return False
    return default


# Load .env file on module import
_load_env_file()


# =============================================================================
# API Keys (Required)
# =============================================================================

# OpenAI API key for GPT-4 incident extraction
# Get from: https://platform.openai.com/api-keys
try:
    OPENAI_API_KEY: str = _get_required_env('OPENAI_API_KEY')
except EnvironmentError as e:
    # Allow import to succeed for scripts that don't need the API key
    OPENAI_API_KEY = None
    logger.warning(str(e))


# =============================================================================
# Processing Settings
# =============================================================================

# Number of articles to process in each batch
BATCH_SIZE: int = _get_int_env('BATCH_SIZE', 50)

# Delay between API requests (seconds) for rate limiting
RATE_LIMIT_DELAY: int = _get_int_env('RATE_LIMIT_DELAY', 1)

# Maximum concurrent requests for async operations
MAX_CONCURRENT_REQUESTS: int = _get_int_env('MAX_CONCURRENT_REQUESTS', 8)

# Hours of articles to fetch (default: 24)
DEFAULT_HOURS_BACK: int = _get_int_env('DEFAULT_HOURS_BACK', 24)


# =============================================================================
# Community Reports Settings
# =============================================================================

# Secret key for signing approval tokens (HMAC)
REPORT_SIGNING_KEY: Optional[str] = _get_optional_env('REPORT_SIGNING_KEY')

# Base URL for the Incidex site (used in email links)
INCIDEX_BASE_URL: str = _get_optional_env('INCIDEX_BASE_URL', 'https://incidex.au')

# Comma-separated list of reviewer email addresses
REVIEWER_EMAILS: Optional[str] = _get_optional_env('REVIEWER_EMAILS')


# =============================================================================
# Email Settings (SMTP)
# =============================================================================

SMTP_HOST: Optional[str] = _get_optional_env('SMTP_HOST')
SMTP_PORT: int = _get_int_env('SMTP_PORT', 587)
SMTP_USER: Optional[str] = _get_optional_env('SMTP_USER')
SMTP_PASSWORD: Optional[str] = _get_optional_env('SMTP_PASSWORD')
SMTP_FROM: Optional[str] = _get_optional_env('SMTP_FROM')
SMTP_USE_TLS: bool = _get_bool_env('SMTP_USE_TLS', True)


# =============================================================================
# Discord Alerts
# =============================================================================

DISCORD_WEBHOOK_URL: Optional[str] = _get_optional_env('DISCORD_WEBHOOK_URL')


# =============================================================================
# Google APIs (Optional)
# =============================================================================

# Google API Key for Gemini (alternative to OpenAI)
GOOGLE_API_KEY: Optional[str] = _get_optional_env('GOOGLE_API_KEY')

# Google Maps API Key for geocoding fallback
GOOGLE_MAPS_API_KEY: Optional[str] = _get_optional_env('GOOGLE_MAPS_API_KEY')


# =============================================================================
# Feature Flags
# =============================================================================

# Enable debug mode (more verbose logging)
DEBUG_MODE: bool = _get_bool_env('DEBUG_MODE', False)

# Enable dry-run mode by default (don't save changes)
DRY_RUN_DEFAULT: bool = _get_bool_env('DRY_RUN_DEFAULT', False)


# =============================================================================
# Validation
# =============================================================================

def validate_config(require_openai: bool = True) -> bool:
    """
    Validate that all required configuration is present.

    Args:
        require_openai: Whether to require OPENAI_API_KEY

    Returns:
        True if valid, raises EnvironmentError if not
    """
    errors = []

    if require_openai and not OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY is required but not set")

    if OPENAI_API_KEY and not OPENAI_API_KEY.startswith('sk-'):
        errors.append("OPENAI_API_KEY appears to be invalid (should start with 'sk-')")

    if errors:
        raise EnvironmentError("Configuration validation failed:\n- " + "\n- ".join(errors))

    return True


def get_config_summary() -> dict:
    """
    Get a summary of the current configuration (with secrets masked).
    Useful for debugging and logging.
    """
    def mask_secret(value: Optional[str]) -> str:
        if not value:
            return "(not set)"
        if len(value) <= 8:
            return "***"
        return f"{value[:4]}...{value[-4:]}"

    return {
        "OPENAI_API_KEY": mask_secret(OPENAI_API_KEY),
        "GOOGLE_API_KEY": mask_secret(GOOGLE_API_KEY),
        "GOOGLE_MAPS_API_KEY": mask_secret(GOOGLE_MAPS_API_KEY),
        "BATCH_SIZE": BATCH_SIZE,
        "RATE_LIMIT_DELAY": RATE_LIMIT_DELAY,
        "MAX_CONCURRENT_REQUESTS": MAX_CONCURRENT_REQUESTS,
        "REPORT_SIGNING_KEY": "(set)" if REPORT_SIGNING_KEY else "(not set)",
        "SMTP_HOST": SMTP_HOST or "(not set)",
        "DISCORD_WEBHOOK_URL": "(set)" if DISCORD_WEBHOOK_URL else "(not set)",
        "DEBUG_MODE": DEBUG_MODE,
    }

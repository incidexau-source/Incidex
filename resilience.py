"""
Resilience Module for Incidex Pipeline

Provides fault tolerance patterns for the RSS monitoring pipeline:
- Circuit Breaker: Prevents cascade failures by tracking errors
- Pipeline Checkpoint: Enables resumption from failures
- Retry with Backoff: Automatic retry with exponential backoff

Usage:
    from resilience import CircuitBreaker, PipelineCheckpoint, retry_with_backoff

    # Circuit breaker for API calls
    openai_breaker = CircuitBreaker(name="openai", failure_threshold=5)
    result = openai_breaker.call(api_function, *args)

    # Checkpoint for pipeline state
    checkpoint = PipelineCheckpoint()
    checkpoint.mark_url_processed(url)
    checkpoint.save()

    # Retry decorator
    @retry_with_backoff(max_retries=3)
    def flaky_function():
        ...
"""

import json
import logging
import time
import functools
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Optional, Any, List, Dict, TypeVar, ParamSpec
from enum import Enum

logger = logging.getLogger(__name__)


# Type variables for generic retry decorator
P = ParamSpec('P')
T = TypeVar('T')


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation, requests allowed
    OPEN = "open"          # Failures exceeded threshold, requests blocked
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitOpenError(Exception):
    """Raised when circuit breaker is open and request is blocked."""

    def __init__(self, name: str, reset_time: float):
        self.name = name
        self.reset_time = reset_time
        super().__init__(
            f"Circuit '{name}' is open. "
            f"Will reset in {reset_time:.1f} seconds."
        )


@dataclass
class CircuitBreaker:
    """
    Circuit breaker pattern implementation.

    Prevents cascade failures by tracking error rates and temporarily
    blocking requests when a service becomes unavailable.

    States:
    - CLOSED: Normal operation, all requests pass through
    - OPEN: Too many failures, requests are blocked
    - HALF_OPEN: Testing recovery, one request allowed

    Args:
        name: Identifier for this circuit (for logging)
        failure_threshold: Number of failures before opening circuit
        success_threshold: Successes needed in half-open to close
        reset_timeout: Seconds before attempting to close circuit
        exclude_exceptions: Exception types that don't count as failures
    """
    name: str = "default"
    failure_threshold: int = 5
    success_threshold: int = 2
    reset_timeout: float = 60.0
    exclude_exceptions: tuple = field(default_factory=lambda: (KeyboardInterrupt, SystemExit))

    # Internal state
    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _failure_count: int = field(default=0, init=False)
    _success_count: int = field(default=0, init=False)
    _last_failure_time: float = field(default=0.0, init=False)
    _last_state_change: float = field(default_factory=time.time, init=False)

    @property
    def state(self) -> CircuitState:
        """Get current circuit state, checking for timeout transitions."""
        if self._state == CircuitState.OPEN:
            if time.time() - self._last_failure_time >= self.reset_timeout:
                self._transition_to(CircuitState.HALF_OPEN)
        return self._state

    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)."""
        return self.state == CircuitState.CLOSED

    @property
    def is_open(self) -> bool:
        """Check if circuit is open (blocking requests)."""
        return self.state == CircuitState.OPEN

    def _transition_to(self, new_state: CircuitState):
        """Transition to a new state."""
        old_state = self._state
        self._state = new_state
        self._last_state_change = time.time()

        if new_state == CircuitState.CLOSED:
            self._failure_count = 0
            self._success_count = 0
        elif new_state == CircuitState.HALF_OPEN:
            self._success_count = 0

        logger.info(f"Circuit '{self.name}': {old_state.value} -> {new_state.value}")

    def _record_success(self):
        """Record a successful call."""
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.success_threshold:
                self._transition_to(CircuitState.CLOSED)
                logger.info(f"Circuit '{self.name}' recovered after {self.success_threshold} successes")

    def _record_failure(self, exception: Exception):
        """Record a failed call."""
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._state == CircuitState.HALF_OPEN:
            # Single failure in half-open reopens circuit
            self._transition_to(CircuitState.OPEN)
            logger.warning(f"Circuit '{self.name}' reopened after failure in half-open state")
        elif self._failure_count >= self.failure_threshold:
            self._transition_to(CircuitState.OPEN)
            logger.warning(
                f"Circuit '{self.name}' opened after {self._failure_count} failures. "
                f"Will retry in {self.reset_timeout}s"
            )

    def call(self, func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        """
        Execute a function through the circuit breaker.

        Args:
            func: The function to execute
            *args, **kwargs: Arguments to pass to the function

        Returns:
            The function's return value

        Raises:
            CircuitOpenError: If circuit is open
            Exception: Any exception from the function (after recording failure)
        """
        state = self.state

        if state == CircuitState.OPEN:
            reset_time = self.reset_timeout - (time.time() - self._last_failure_time)
            raise CircuitOpenError(self.name, max(0, reset_time))

        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result
        except self.exclude_exceptions:
            # Don't count these as failures
            raise
        except Exception as e:
            self._record_failure(e)
            raise

    async def call_async(self, func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        """
        Execute an async function through the circuit breaker.

        Args:
            func: The async function to execute
            *args, **kwargs: Arguments to pass to the function

        Returns:
            The function's return value

        Raises:
            CircuitOpenError: If circuit is open
            Exception: Any exception from the function (after recording failure)
        """
        state = self.state

        if state == CircuitState.OPEN:
            reset_time = self.reset_timeout - (time.time() - self._last_failure_time)
            raise CircuitOpenError(self.name, max(0, reset_time))

        try:
            result = await func(*args, **kwargs)
            self._record_success()
            return result
        except self.exclude_exceptions:
            raise
        except Exception as e:
            self._record_failure(e)
            raise

    def reset(self):
        """Manually reset the circuit to closed state."""
        self._transition_to(CircuitState.CLOSED)
        logger.info(f"Circuit '{self.name}' manually reset")

    def get_stats(self) -> dict:
        """Get circuit breaker statistics."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "last_failure": datetime.fromtimestamp(self._last_failure_time).isoformat()
                if self._last_failure_time else None,
            "time_in_state": time.time() - self._last_state_change,
        }


@dataclass
class PipelineCheckpoint:
    """
    Checkpoint system for pipeline resumption.

    Tracks processed URLs and pipeline state to enable resumption
    after failures without reprocessing completed work.

    Args:
        checkpoint_file: Path to the checkpoint file
        auto_save: Whether to save after each update
        max_age_days: Maximum age of entries before cleanup
    """
    checkpoint_file: Path = field(default_factory=lambda: Path("data/pipeline_checkpoint.json"))
    auto_save: bool = True
    max_age_days: int = 7

    # State
    _state: Dict[str, Any] = field(default_factory=dict, init=False)
    _dirty: bool = field(default=False, init=False)

    def __post_init__(self):
        """Load existing checkpoint if available."""
        self._load()

    def _load(self):
        """Load checkpoint from file."""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    self._state = json.load(f)
                logger.debug(f"Loaded checkpoint with {len(self._state.get('processed_urls', []))} URLs")
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load checkpoint: {e}. Starting fresh.")
                self._state = self._default_state()
        else:
            self._state = self._default_state()

    def _default_state(self) -> dict:
        """Return default checkpoint state."""
        return {
            "processed_urls": [],
            "last_stage": None,
            "last_run": None,
            "pending_incidents": [],
            "stats": {
                "total_processed": 0,
                "total_incidents": 0,
                "total_errors": 0,
            }
        }

    def save(self):
        """Save checkpoint to file."""
        if not self._dirty:
            return

        # Ensure directory exists
        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)

        # Clean old entries before saving
        self._cleanup_old_entries()

        self._state["last_saved"] = datetime.now().isoformat()

        try:
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(self._state, f, indent=2, default=str)
            self._dirty = False
            logger.debug(f"Saved checkpoint to {self.checkpoint_file}")
        except IOError as e:
            logger.error(f"Failed to save checkpoint: {e}")

    def _cleanup_old_entries(self):
        """Remove entries older than max_age_days."""
        cutoff = datetime.now() - timedelta(days=self.max_age_days)
        cutoff_str = cutoff.isoformat()

        # Filter processed_urls to keep only recent ones
        if "processed_urls" in self._state:
            original_count = len(self._state["processed_urls"])
            self._state["processed_urls"] = [
                entry for entry in self._state["processed_urls"]
                if entry.get("timestamp", "") >= cutoff_str
            ]
            removed = original_count - len(self._state["processed_urls"])
            if removed > 0:
                logger.debug(f"Cleaned up {removed} old URL entries")

    def is_url_processed(self, url: str) -> bool:
        """Check if a URL has been processed recently."""
        for entry in self._state.get("processed_urls", []):
            if entry.get("url") == url:
                return True
        return False

    def mark_url_processed(self, url: str, success: bool = True):
        """Mark a URL as processed."""
        if "processed_urls" not in self._state:
            self._state["processed_urls"] = []

        self._state["processed_urls"].append({
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "success": success,
        })

        self._state["stats"]["total_processed"] = \
            self._state["stats"].get("total_processed", 0) + 1

        self._dirty = True
        if self.auto_save:
            self.save()

    def set_stage(self, stage: str):
        """Set the current pipeline stage."""
        self._state["last_stage"] = stage
        self._state["last_stage_time"] = datetime.now().isoformat()
        self._dirty = True
        if self.auto_save:
            self.save()

    def get_stage(self) -> Optional[str]:
        """Get the last pipeline stage."""
        return self._state.get("last_stage")

    def add_pending_incident(self, incident: dict):
        """Add an incident to the pending list (for batch processing)."""
        if "pending_incidents" not in self._state:
            self._state["pending_incidents"] = []

        self._state["pending_incidents"].append({
            **incident,
            "added_at": datetime.now().isoformat(),
        })
        self._dirty = True

    def get_pending_incidents(self) -> List[dict]:
        """Get all pending incidents."""
        return self._state.get("pending_incidents", [])

    def clear_pending_incidents(self):
        """Clear the pending incidents list."""
        self._state["pending_incidents"] = []
        self._dirty = True
        if self.auto_save:
            self.save()

    def record_error(self, error: str, context: Optional[dict] = None):
        """Record an error for debugging."""
        if "errors" not in self._state:
            self._state["errors"] = []

        self._state["errors"].append({
            "error": error,
            "context": context,
            "timestamp": datetime.now().isoformat(),
        })

        # Keep only last 100 errors
        self._state["errors"] = self._state["errors"][-100:]

        self._state["stats"]["total_errors"] = \
            self._state["stats"].get("total_errors", 0) + 1

        self._dirty = True

    def start_run(self):
        """Mark the start of a new pipeline run."""
        self._state["last_run"] = datetime.now().isoformat()
        self._state["run_in_progress"] = True
        self._dirty = True
        if self.auto_save:
            self.save()

    def end_run(self, success: bool = True):
        """Mark the end of a pipeline run."""
        self._state["run_in_progress"] = False
        self._state["last_run_success"] = success
        self._state["last_run_end"] = datetime.now().isoformat()
        self._dirty = True
        self.save()

    def get_stats(self) -> dict:
        """Get checkpoint statistics."""
        return {
            "processed_urls": len(self._state.get("processed_urls", [])),
            "pending_incidents": len(self._state.get("pending_incidents", [])),
            "last_stage": self._state.get("last_stage"),
            "last_run": self._state.get("last_run"),
            "run_in_progress": self._state.get("run_in_progress", False),
            **self._state.get("stats", {}),
        }

    def clear(self):
        """Clear all checkpoint data."""
        self._state = self._default_state()
        self._dirty = True
        self.save()
        logger.info("Checkpoint cleared")


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    retryable_exceptions: tuple = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None,
):
    """
    Decorator for retrying functions with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        exponential_base: Base for exponential backoff calculation
        retryable_exceptions: Exception types that trigger retry
        on_retry: Optional callback(exception, attempt) called before each retry

    Example:
        @retry_with_backoff(max_retries=3, base_delay=1.0)
        def call_api():
            return requests.get(url)
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries + 1} attempts: {e}"
                        )
                        raise

                    delay = min(base_delay * (exponential_base ** attempt), max_delay)

                    if on_retry:
                        on_retry(e, attempt + 1)

                    logger.warning(
                        f"Function {func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    time.sleep(delay)

            # Should not reach here, but just in case
            raise last_exception

        @functools.wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            import asyncio
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(
                            f"Async function {func.__name__} failed after {max_retries + 1} attempts: {e}"
                        )
                        raise

                    delay = min(base_delay * (exponential_base ** attempt), max_delay)

                    if on_retry:
                        on_retry(e, attempt + 1)

                    logger.warning(
                        f"Async function {func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    await asyncio.sleep(delay)

            raise last_exception

        # Return appropriate wrapper based on function type
        if asyncio_iscoroutinefunction(func):
            return async_wrapper
        return wrapper

    return decorator


def asyncio_iscoroutinefunction(func) -> bool:
    """Check if a function is an async coroutine function."""
    import inspect
    return inspect.iscoroutinefunction(func)


# =============================================================================
# Global Circuit Breakers for Common Services
# =============================================================================

# OpenAI API circuit breaker
openai_circuit = CircuitBreaker(
    name="openai",
    failure_threshold=5,
    reset_timeout=60.0,
)

# Nominatim geocoding circuit breaker
nominatim_circuit = CircuitBreaker(
    name="nominatim",
    failure_threshold=10,
    reset_timeout=120.0,  # Longer timeout for rate-limited service
)

# RSS feed fetching circuit breaker
rss_circuit = CircuitBreaker(
    name="rss",
    failure_threshold=15,
    reset_timeout=30.0,
)


def get_all_circuit_stats() -> Dict[str, dict]:
    """Get statistics for all global circuit breakers."""
    return {
        "openai": openai_circuit.get_stats(),
        "nominatim": nominatim_circuit.get_stats(),
        "rss": rss_circuit.get_stats(),
    }

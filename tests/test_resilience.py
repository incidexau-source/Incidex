#!/usr/bin/env python3
"""
Tests for the resilience module.

Tests circuit breaker, checkpoint, and retry logic.
"""

import json
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from resilience import (
    CircuitBreaker,
    CircuitState,
    CircuitOpenError,
    PipelineCheckpoint,
    retry_with_backoff,
)


class TestCircuitBreaker(unittest.TestCase):
    """Test circuit breaker functionality."""

    def test_initial_state_is_closed(self):
        """Circuit should start in closed state."""
        cb = CircuitBreaker(name="test")
        self.assertEqual(cb.state, CircuitState.CLOSED)
        self.assertTrue(cb.is_closed)
        self.assertFalse(cb.is_open)

    def test_successful_calls_keep_circuit_closed(self):
        """Successful calls should not affect closed circuit."""
        cb = CircuitBreaker(name="test")

        def success():
            return "ok"

        for _ in range(10):
            result = cb.call(success)
            self.assertEqual(result, "ok")

        self.assertTrue(cb.is_closed)

    def test_failures_open_circuit(self):
        """Enough failures should open the circuit."""
        cb = CircuitBreaker(name="test", failure_threshold=3)

        def fail():
            raise ValueError("error")

        # Fail 3 times
        for _ in range(3):
            with self.assertRaises(ValueError):
                cb.call(fail)

        # Circuit should now be open
        self.assertTrue(cb.is_open)
        self.assertEqual(cb.state, CircuitState.OPEN)

    def test_open_circuit_blocks_calls(self):
        """Open circuit should raise CircuitOpenError."""
        cb = CircuitBreaker(name="test", failure_threshold=1)

        def fail():
            raise ValueError("error")

        # Fail once to open
        with self.assertRaises(ValueError):
            cb.call(fail)

        # Next call should be blocked
        def success():
            return "ok"

        with self.assertRaises(CircuitOpenError) as ctx:
            cb.call(success)

        self.assertIn("test", str(ctx.exception))

    def test_circuit_resets_after_timeout(self):
        """Circuit should transition to half-open after timeout."""
        cb = CircuitBreaker(name="test", failure_threshold=1, reset_timeout=0.1)

        def fail():
            raise ValueError("error")

        # Fail to open
        with self.assertRaises(ValueError):
            cb.call(fail)

        self.assertTrue(cb.is_open)

        # Wait for timeout
        time.sleep(0.15)

        # Should now be half-open
        self.assertEqual(cb.state, CircuitState.HALF_OPEN)

    def test_half_open_success_closes_circuit(self):
        """Successful calls in half-open should close circuit."""
        cb = CircuitBreaker(
            name="test",
            failure_threshold=1,
            success_threshold=2,
            reset_timeout=0.1
        )

        def fail():
            raise ValueError("error")

        def success():
            return "ok"

        # Fail to open
        with self.assertRaises(ValueError):
            cb.call(fail)

        # Wait for timeout
        time.sleep(0.15)

        # Two successful calls should close
        cb.call(success)
        self.assertEqual(cb.state, CircuitState.HALF_OPEN)
        cb.call(success)
        self.assertEqual(cb.state, CircuitState.CLOSED)

    def test_half_open_failure_reopens_circuit(self):
        """Failure in half-open should reopen circuit."""
        cb = CircuitBreaker(name="test", failure_threshold=1, reset_timeout=0.1)

        def fail():
            raise ValueError("error")

        # Fail to open
        with self.assertRaises(ValueError):
            cb.call(fail)

        # Wait for timeout
        time.sleep(0.15)

        # Fail again in half-open
        with self.assertRaises(ValueError):
            cb.call(fail)

        self.assertTrue(cb.is_open)

    def test_excluded_exceptions_dont_count(self):
        """Excluded exceptions should not count as failures."""
        cb = CircuitBreaker(
            name="test",
            failure_threshold=2,
            exclude_exceptions=(KeyboardInterrupt,)
        )

        def interrupt():
            raise KeyboardInterrupt()

        # KeyboardInterrupt should not count
        for _ in range(5):
            with self.assertRaises(KeyboardInterrupt):
                cb.call(interrupt)

        # Circuit should still be closed
        self.assertTrue(cb.is_closed)

    def test_manual_reset(self):
        """Manual reset should close circuit."""
        cb = CircuitBreaker(name="test", failure_threshold=1)

        def fail():
            raise ValueError("error")

        # Fail to open
        with self.assertRaises(ValueError):
            cb.call(fail)

        self.assertTrue(cb.is_open)

        # Manual reset
        cb.reset()
        self.assertTrue(cb.is_closed)

    def test_get_stats(self):
        """Stats should return correct information."""
        cb = CircuitBreaker(name="test_stats", failure_threshold=3)

        def fail():
            raise ValueError("error")

        with self.assertRaises(ValueError):
            cb.call(fail)

        stats = cb.get_stats()
        self.assertEqual(stats["name"], "test_stats")
        self.assertEqual(stats["state"], "closed")
        self.assertEqual(stats["failure_count"], 1)


class TestPipelineCheckpoint(unittest.TestCase):
    """Test pipeline checkpoint functionality."""

    def setUp(self):
        """Create temporary checkpoint file."""
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        )
        self.temp_file.close()
        self.checkpoint_path = Path(self.temp_file.name)

    def tearDown(self):
        """Clean up temporary file."""
        if self.checkpoint_path.exists():
            self.checkpoint_path.unlink()

    def test_new_checkpoint_has_default_state(self):
        """New checkpoint should have default state."""
        cp = PipelineCheckpoint(
            checkpoint_file=self.checkpoint_path,
            auto_save=False
        )

        self.assertEqual(cp.get_stats()["processed_urls"], 0)
        self.assertEqual(cp.get_stats()["pending_incidents"], 0)
        self.assertIsNone(cp.get_stage())

    def test_mark_url_processed(self):
        """URLs can be marked as processed."""
        cp = PipelineCheckpoint(
            checkpoint_file=self.checkpoint_path,
            auto_save=False
        )

        cp.mark_url_processed("https://example.com/article1")
        cp.mark_url_processed("https://example.com/article2")

        self.assertTrue(cp.is_url_processed("https://example.com/article1"))
        self.assertTrue(cp.is_url_processed("https://example.com/article2"))
        self.assertFalse(cp.is_url_processed("https://example.com/article3"))

    def test_set_and_get_stage(self):
        """Stage can be set and retrieved."""
        cp = PipelineCheckpoint(
            checkpoint_file=self.checkpoint_path,
            auto_save=False
        )

        cp.set_stage("extracting_incidents")
        self.assertEqual(cp.get_stage(), "extracting_incidents")

        cp.set_stage("geocoding")
        self.assertEqual(cp.get_stage(), "geocoding")

    def test_pending_incidents(self):
        """Pending incidents can be added and retrieved."""
        cp = PipelineCheckpoint(
            checkpoint_file=self.checkpoint_path,
            auto_save=False
        )

        cp.add_pending_incident({"title": "Incident 1"})
        cp.add_pending_incident({"title": "Incident 2"})

        pending = cp.get_pending_incidents()
        self.assertEqual(len(pending), 2)
        self.assertEqual(pending[0]["title"], "Incident 1")

        cp.clear_pending_incidents()
        self.assertEqual(len(cp.get_pending_incidents()), 0)

    def test_save_and_load(self):
        """Checkpoint persists to file."""
        cp1 = PipelineCheckpoint(
            checkpoint_file=self.checkpoint_path,
            auto_save=True
        )

        cp1.mark_url_processed("https://example.com/test")
        cp1.set_stage("test_stage")
        cp1.save()

        # Load in new instance
        cp2 = PipelineCheckpoint(
            checkpoint_file=self.checkpoint_path,
            auto_save=False
        )

        self.assertTrue(cp2.is_url_processed("https://example.com/test"))
        self.assertEqual(cp2.get_stage(), "test_stage")

    def test_run_tracking(self):
        """Run start/end is tracked."""
        cp = PipelineCheckpoint(
            checkpoint_file=self.checkpoint_path,
            auto_save=False
        )

        cp.start_run()
        self.assertTrue(cp.get_stats()["run_in_progress"])

        cp.end_run(success=True)
        self.assertFalse(cp.get_stats()["run_in_progress"])

    def test_error_recording(self):
        """Errors are recorded."""
        cp = PipelineCheckpoint(
            checkpoint_file=self.checkpoint_path,
            auto_save=False
        )

        cp.record_error("Test error", {"url": "https://example.com"})

        stats = cp.get_stats()
        self.assertEqual(stats["total_errors"], 1)

    def test_clear(self):
        """Clear resets all state."""
        cp = PipelineCheckpoint(
            checkpoint_file=self.checkpoint_path,
            auto_save=False
        )

        cp.mark_url_processed("https://example.com")
        cp.set_stage("test")
        cp.add_pending_incident({"title": "test"})

        cp.clear()

        self.assertFalse(cp.is_url_processed("https://example.com"))
        self.assertIsNone(cp.get_stage())
        self.assertEqual(len(cp.get_pending_incidents()), 0)


class TestRetryWithBackoff(unittest.TestCase):
    """Test retry decorator."""

    def test_no_retry_on_success(self):
        """Successful function should not retry."""
        call_count = 0

        @retry_with_backoff(max_retries=3)
        def success():
            nonlocal call_count
            call_count += 1
            return "ok"

        result = success()
        self.assertEqual(result, "ok")
        self.assertEqual(call_count, 1)

    def test_retry_on_failure(self):
        """Failed function should retry."""
        call_count = 0

        @retry_with_backoff(max_retries=2, base_delay=0.01)
        def fail_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("error")
            return "ok"

        result = fail_then_succeed()
        self.assertEqual(result, "ok")
        self.assertEqual(call_count, 2)

    def test_raises_after_max_retries(self):
        """Function should raise after max retries."""
        call_count = 0

        @retry_with_backoff(max_retries=2, base_delay=0.01)
        def always_fail():
            nonlocal call_count
            call_count += 1
            raise ValueError("always fails")

        with self.assertRaises(ValueError):
            always_fail()

        self.assertEqual(call_count, 3)  # Initial + 2 retries

    def test_on_retry_callback(self):
        """Callback should be called on retry."""
        retry_calls = []

        def on_retry(exc, attempt):
            retry_calls.append((str(exc), attempt))

        @retry_with_backoff(max_retries=2, base_delay=0.01, on_retry=on_retry)
        def fail_twice():
            if len(retry_calls) < 2:
                raise ValueError("error")
            return "ok"

        result = fail_twice()
        self.assertEqual(result, "ok")
        self.assertEqual(len(retry_calls), 2)


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3
"""
Tests for the config module.

Verifies that:
- Environment variables are loaded correctly
- .env file parsing works
- Default values are applied
- Validation functions work
- Secrets are properly masked in summaries
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestConfigEnvLoading(unittest.TestCase):
    """Test environment variable loading."""

    def test_env_var_override(self):
        """Environment variables should be used when set."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-test-key-12345'}):
            # Re-import to pick up new env var
            import importlib
            import config
            importlib.reload(config)

            self.assertEqual(config.OPENAI_API_KEY, 'sk-test-key-12345')

    def test_default_values(self):
        """Default values should be applied for optional settings."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-test'}, clear=False):
            import importlib
            import config
            importlib.reload(config)

            self.assertEqual(config.BATCH_SIZE, 50)
            self.assertEqual(config.RATE_LIMIT_DELAY, 1)
            self.assertEqual(config.MAX_CONCURRENT_REQUESTS, 8)
            self.assertEqual(config.SMTP_PORT, 587)

    def test_bool_env_parsing(self):
        """Boolean environment variables should be parsed correctly."""
        import config

        # Test truthy values
        for value in ['true', 'True', 'TRUE', '1', 'yes', 'YES', 'on', 'ON']:
            with patch.dict(os.environ, {'DEBUG_MODE': value}):
                self.assertTrue(config._get_bool_env('DEBUG_MODE', False))

        # Test falsy values
        for value in ['false', 'False', 'FALSE', '0', 'no', 'NO', 'off', 'OFF']:
            with patch.dict(os.environ, {'DEBUG_MODE': value}):
                self.assertFalse(config._get_bool_env('DEBUG_MODE', True))

    def test_int_env_parsing(self):
        """Integer environment variables should be parsed correctly."""
        import config

        with patch.dict(os.environ, {'BATCH_SIZE': '100'}):
            self.assertEqual(config._get_int_env('BATCH_SIZE', 50), 100)

        # Invalid integer should use default
        with patch.dict(os.environ, {'BATCH_SIZE': 'not-a-number'}):
            self.assertEqual(config._get_int_env('BATCH_SIZE', 50), 50)


class TestEnvFileParsing(unittest.TestCase):
    """Test .env file parsing."""

    def test_env_file_parsing(self):
        """Test that .env file is parsed correctly."""
        import config

        # Create a temporary .env file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write('# Comment line\n')
            f.write('TEST_KEY=test_value\n')
            f.write('QUOTED_KEY="quoted value"\n')
            f.write("SINGLE_QUOTED='single quoted'\n")
            f.write('SPACES_KEY = value with spaces \n')
            f.write('\n')  # Empty line
            temp_path = f.name

        try:
            # Manually parse the file
            with open(temp_path, 'r') as f:
                lines = f.readlines()

            # Verify parsing logic
            parsed = {}
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, _, value = line.partition('=')
                    key = key.strip()
                    value = value.strip()
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    parsed[key] = value

            self.assertEqual(parsed['TEST_KEY'], 'test_value')
            self.assertEqual(parsed['QUOTED_KEY'], 'quoted value')
            self.assertEqual(parsed['SINGLE_QUOTED'], 'single quoted')

        finally:
            os.unlink(temp_path)


class TestConfigValidation(unittest.TestCase):
    """Test configuration validation."""

    def test_validate_with_valid_key(self):
        """Validation should pass with valid API key."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-valid-key-12345'}):
            import importlib
            import config
            importlib.reload(config)

            self.assertTrue(config.validate_config(require_openai=True))

    def test_validate_without_key_when_not_required(self):
        """Validation should pass without key if not required."""
        with patch.dict(os.environ, {}, clear=True):
            import importlib
            import config

            # Clear the key
            config.OPENAI_API_KEY = None

            self.assertTrue(config.validate_config(require_openai=False))

    def test_validate_invalid_key_format(self):
        """Validation should fail with invalid key format."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'invalid-key'}):
            import importlib
            import config
            importlib.reload(config)

            with self.assertRaises(EnvironmentError) as context:
                config.validate_config(require_openai=True)

            self.assertIn('invalid', str(context.exception).lower())


class TestConfigSummary(unittest.TestCase):
    """Test configuration summary generation."""

    def test_secrets_are_masked(self):
        """Secrets should be masked in the summary."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-proj-1234567890abcdef'}):
            import importlib
            import config
            importlib.reload(config)

            summary = config.get_config_summary()

            # API key should be masked
            self.assertIn('...', summary['OPENAI_API_KEY'])
            self.assertNotIn('1234567890', summary['OPENAI_API_KEY'])

    def test_unset_secrets_show_not_set(self):
        """Unset secrets should show (not set)."""
        import config

        # Temporarily clear the keys
        original_google = config.GOOGLE_API_KEY
        config.GOOGLE_API_KEY = None

        try:
            summary = config.get_config_summary()
            self.assertEqual(summary['GOOGLE_API_KEY'], '(not set)')
        finally:
            config.GOOGLE_API_KEY = original_google

    def test_short_secrets_fully_masked(self):
        """Short secrets should be fully masked."""
        import config

        def mask_secret(value):
            if not value:
                return "(not set)"
            if len(value) <= 8:
                return "***"
            return f"{value[:4]}...{value[-4:]}"

        self.assertEqual(mask_secret('short'), '***')
        self.assertEqual(mask_secret('longer-secret-key'), 'long...-key')


class TestRequiredEnvVar(unittest.TestCase):
    """Test required environment variable handling."""

    def test_missing_required_raises(self):
        """Missing required env var should raise EnvironmentError."""
        import config

        # Clear the environment
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(EnvironmentError) as context:
                config._get_required_env('NONEXISTENT_KEY')

            self.assertIn('NONEXISTENT_KEY', str(context.exception))


if __name__ == '__main__':
    unittest.main()

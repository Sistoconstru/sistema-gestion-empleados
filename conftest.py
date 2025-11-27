"""
conftest.py - Configuration for pytest and Django tests
Mock python-magic to avoid Windows compatibility issues
"""
import sys
from unittest.mock import MagicMock

# Mock the magic module before any Django imports
mock_magic = MagicMock()
mock_magic.from_buffer = MagicMock(return_value='application/pdf')
sys.modules['magic'] = mock_magic

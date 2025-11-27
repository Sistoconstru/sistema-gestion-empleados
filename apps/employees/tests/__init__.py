"""
Test module for employees app
Mock python-magic to avoid Windows compatibility issues
"""
import sys
from unittest.mock import MagicMock

# Mock the magic module before Django imports the documents app
if 'magic' not in sys.modules:
    mock_magic = MagicMock()
    mock_magic.from_buffer = MagicMock(return_value='application/pdf')
    sys.modules['magic'] = mock_magic

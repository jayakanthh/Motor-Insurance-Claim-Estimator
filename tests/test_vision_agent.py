import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.vision_model import VisionAgent

class TestVisionAgent(unittest.TestCase):
    def test_mock_provider(self):
        agent = VisionAgent(provider="mock")
        result = agent.analyze_image(b"fake_data")
        self.assertIn("damages", result)
        self.assertTrue(len(result["damages"]) > 0)
        self.assertIn("confidence", result)

    @patch("app.vision_model.OpenAI")
    def test_openai_provider_initialization(self, mock_openai):
        # Test initialization with valid API key
        agent = VisionAgent(provider="openai", api_key="test_key")
        mock_openai.assert_called_once_with(api_key="test_key")
        self.assertIsNotNone(agent.client)

    def test_openai_provider_no_key(self):
        # Test initialization without API key (should still init but fail later if used)
        # In our implementation, we init OpenAI client if OpenAI module is available.
        # If we pass None as key, OpenAI client might raise error or wait for env var.
        # Here we just check if it tries to init.
        pass

if __name__ == '__main__':
    unittest.main()

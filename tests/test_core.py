import unittest
import sys
import os
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core import ClaimEstimator

class TestClaimEstimator(unittest.TestCase):
    def setUp(self):
        self.estimator = ClaimEstimator()

    def test_mock_analysis_flow(self):
        # Create a dummy image byte stream
        dummy_image = b"fake_image_data"
        
        result = self.estimator.analyze_claim(dummy_image)
        
        # Check structure
        self.assertIn("damage_assessment", result)
        self.assertIn("cost_estimate", result)
        self.assertIn("status", result)
        
        # Check logic
        estimate = result['cost_estimate']
        self.assertIn("line_items", estimate)
        self.assertIn("summary", estimate)
        
        # Check if totals match
        summary = estimate['summary']
        self.assertAlmostEqual(
            summary['total_cost'], 
            summary['subtotal'] + summary['tax']
        )
        
        print(json.dumps(result, indent=2))

if __name__ == '__main__':
    unittest.main()

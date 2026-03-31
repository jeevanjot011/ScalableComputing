import unittest
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'loan_service'))

from app import calculate_loan_emi, lambda_handler

class TestLoanCalculator(unittest.TestCase):
    
    def test_calculate_emi_standard(self):
        """Test standard EMI calculation"""
        result = calculate_loan_emi(500000, 7.5, 20)
        self.assertAlmostEqual(float(result['emi']), 4027.97, places=2)
        self.assertEqual(result['months'], 240)
    
    def test_calculate_emi_zero_interest(self):
        """Test zero interest edge case"""
        result = calculate_loan_emi(120000, 0, 10)
        self.assertEqual(float(result['emi']), 1000.00)
    
    def test_lambda_handler_health(self):
        """Test health check endpoint"""
        event = {'httpMethod': 'GET'}
        context = type('Context', (), {'aws_request_id': 'test-123'})()
        response = lambda_handler(event, context)
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['status'], 'healthy')
    
    def test_lambda_handler_calculation(self):
        """Test loan calculation via handler"""
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'principal': 1000000,
                'annual_rate': 10,
                'years': 5
            })
        }
        context = type('Context', (), {'aws_request_id': 'test-456'})()
        response = lambda_handler(event, context)
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertIn('emi', body)

if __name__ == '__main__':
    unittest.main()

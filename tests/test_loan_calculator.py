import unittest
import json
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal

# Mock boto3 before importing app
sys.modules['boto3'] = Mock()
sys.modules['botocore'] = Mock()
sys.modules['botocore.config'] = Mock()
sys.modules['botocore.config'].Config = Mock

# Set environment variables before import
os.environ['TABLE_NAME'] = 'test-table'
os.environ['SNS_TOPIC_ARN'] = 'arn:aws:sns:us-east-1:123456789012:test-topic'
os.environ['SQS_QUEUE_URL'] = 'https://sqs.us-east-1.amazonaws.com/123456789012/test-queue'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

# Now import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../loan_service'))

class TestLoanCalculator(unittest.TestCase):
    
    @patch.dict('os.environ', {
        'TABLE_NAME': 'test-table',
        'SNS_TOPIC_ARN': 'arn:aws:sns:us-east-1:123456789012:test-topic',
        'SQS_QUEUE_URL': 'https://sqs.us-east-1.amazonaws.com/123456789012/test-queue',
        'AWS_DEFAULT_REGION': 'us-east-1'
    })
    @patch('boto3.resource')
    @patch('boto3.client')
    def test_calculate_emi_standard(self, mock_client, mock_resource):
        """Test standard EMI calculation"""
        from app import calculate_loan_emi
        
        result = calculate_loan_emi(500000, 7.5, 20)
        self.assertAlmostEqual(float(result['emi']), 4027.97, places=2)
        self.assertEqual(result['months'], 240)
    
    def test_calculate_emi_zero_interest(self):
        """Test zero interest edge case"""
        # Import fresh to avoid boto3 initialization
        import importlib
        import app as app_module
        importlib.reload(app_module)
        
        result = app_module.calculate_loan_emi(120000, 0, 10)
        self.assertEqual(float(result['emi']), 1000.00)
        self.assertEqual(result['months'], 120)
    
    @patch.dict('os.environ', {'AWS_DEFAULT_REGION': 'us-east-1'})
    @patch('boto3.resource')
    def test_lambda_handler_health(self, mock_resource):
        """Test health check endpoint"""
        from app import lambda_handler
        
        event = {'httpMethod': 'GET'}
        context = type('Context', (), {'aws_request_id': 'test-123'})()
        response = lambda_handler(event, context)
        
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['status'], 'healthy')
    
    @patch.dict('os.environ', {'AWS_DEFAULT_REGION': 'us-east-1'})
    @patch('boto3.resource')
    @patch('boto3.client')
    def test_lambda_handler_calculation(self, mock_client, mock_resource):
        """Test loan calculation via handler"""
        from app import lambda_handler
        
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
        self.assertGreater(body['emi'], 0)

if __name__ == '__main__':
    unittest.main()

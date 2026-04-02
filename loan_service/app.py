import json
import math
import boto3
import os
import logging
import time
from datetime import datetime
from decimal import Decimal
from botocore.config import Config

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configure boto3 with timeouts (SonarQube fix)
boto_config = Config(
    connect_timeout=5,  # seconds
    read_timeout=10,    # seconds
    retries={'max_attempts': 3}
)

# Initialize AWS clients with timeout config
dynamodb = boto3.resource('dynamodb', config=boto_config)
sns = boto3.client('sns', config=boto_config)
sqs = boto3.client('sqs', config=boto_config)

# Get environment variables
TABLE_NAME = os.environ.get('TABLE_NAME', 'ScalableG1')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', '')
SQS_QUEUE_URL = os.environ.get('SQS_QUEUE_URL', '')

def calculate_loan_emi(principal, annual_rate, years):
    monthly_rate = annual_rate / (12 * 100)
    months = years * 12
    if monthly_rate == 0:
        emi = principal / months
    else:
        emi = principal * monthly_rate * (1 + monthly_rate)**months / ((1 + monthly_rate)**months - 1)
    total_payment = emi * months
    total_interest = total_payment - principal
    
    return {
        "emi": Decimal(str(round(emi, 2))),
        "total_payment": Decimal(str(round(total_payment, 2))),
        "total_interest": Decimal(str(round(total_interest, 2))),
        "months": months
    }

def generate_numeric_id():
    """Generate numeric ID for DynamoDB (since order_id is Number type)"""
    # Use timestamp in milliseconds + random suffix
    import random
    timestamp = int(time.time() * 1000)
    random_suffix = random.randint(1000, 9999)
    return timestamp + random_suffix

def save_to_dynamodb(calculation_id, data):
    """Save calculation result to DynamoDB"""
    try:
        logger.info(f"Saving to DynamoDB with ID: {calculation_id}")
        
        table = dynamodb.Table(TABLE_NAME)
        
        # Generate numeric ID for DynamoDB (order_id is Number type)
        numeric_id = generate_numeric_id()
        
        item = {
            'order_id': numeric_id,  # Now it's a Number, not String
            'calculation_uuid': calculation_id,  # Keep original UUID as string attribute
            'timestamp': datetime.now().isoformat(),
            'type': 'loan_calculation',
            'principal': Decimal(str(data['input']['principal'])),
            'annual_rate': Decimal(str(data['input']['annual_rate'])),
            'years': data['input']['years'],
            'emi': data['emi'],
            'total_payment': data['total_payment'],
            'total_interest': data['total_interest'],
            'ttl': int((datetime.now().timestamp() + 90 * 24 * 60 * 60))
        }
        
        response = table.put_item(Item=item)
        logger.info(f"DynamoDB save successful, order_id: {numeric_id}")
        return True
        
    except Exception as e:
        logger.error(f"DynamoDB error: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def send_sns_notification(calculation_id, data):
    """Send SNS notification for large loans"""
    try:
        if SNS_TOPIC_ARN and float(data['input']['principal']) > 1000000:
            message = f"Large loan calculation: ₹{data['input']['principal']}\n"
            message += f"EMI: €{float(data['emi']):.2f}/month for {data['input']['years']} years\n"
            message += f"Calculation ID: {calculation_id}"
            
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject=f"High Value Loan Alert - {calculation_id}",
                Message=message
            )
        return True
    except Exception as e:
        logger.error(f"SNS error: {str(e)}")
        return False

def send_to_sqs(calculation_id, data):
    """Send to SQS for async processing"""
    try:
        if SQS_QUEUE_URL:
            message_data = {
                'calculation_id': calculation_id,
                'type': 'loan_calculation',
                'timestamp': datetime.now().isoformat(),
                'data': {
                    'emi': float(data['emi']),
                    'total_payment': float(data['total_payment']),
                    'total_interest': float(data['total_interest']),
                    'input': {
                        'principal': float(data['input']['principal']),
                        'annual_rate': float(data['input']['annual_rate']),
                        'years': data['input']['years']
                    }
                }
            }
            
            sqs.send_message(
                QueueUrl=SQS_QUEUE_URL,
                MessageBody=json.dumps(message_data)
            )
        return True
    except Exception as e:
        logger.error(f"SQS error: {str(e)}")
        return False

def lambda_handler(event, context):
    request_id = context.aws_request_id if context else 'unknown'
    
    try:
        http_method = event.get('httpMethod', 'POST')
        
        # Health check
        if http_method == 'GET':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'status': 'healthy',
                    'service': 'loan-calculator',
                    'version': '2.2.0',
                    'request_id': request_id
                })
            }
        
        # Parse input
        body_str = event.get('body') if event.get('body') else '{}'
        if isinstance(body_str, str):
            body = json.loads(body_str)
        else:
            body = body_str
        
        principal = float(body.get('principal', 0))
        annual_rate = float(body.get('annual_rate', 0))
        years = int(body.get('years', 0))
        
        # Validation
        if principal <= 0 or annual_rate < 0 or years <= 0:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Invalid input. All values must be positive.',
                    'request_id': request_id
                })
            }
        
        # Calculate
        result = calculate_loan_emi(principal, annual_rate, years)
        result['input'] = {
            'principal': principal,
            'annual_rate': annual_rate,
            'years': years
        }
        result['request_id'] = request_id
        
        # Async operations
        result['persisted'] = save_to_dynamodb(request_id, result)
        result['notification_sent'] = send_sns_notification(request_id, result)
        result['queued'] = send_to_sqs(request_id, result)
        
        # Convert Decimals to floats for JSON response
        response_result = {
            'emi': float(result['emi']),
            'total_payment': float(result['total_payment']),
            'total_interest': float(result['total_interest']),
            'months': result['months'],
            'input': result['input'],
            'request_id': request_id,
            'persisted': result['persisted'],
            'notification_sent': result['notification_sent'],
            'queued': result['queued']
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_result, indent=2)
        }
        
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Invalid JSON', 'request_id': request_id})
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e), 'request_id': request_id})
        }

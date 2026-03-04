"""
Email Validator API - Enhanced Security Version
"""
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import io
from datetime import datetime, timedelta
import os
import hashlib
import hmac
from functools import wraps
from config import config
from validators.email_validator import EmailValidator

# Create Flask app
app = Flask(__name__)
CORS(app)

# Load configuration
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialize validator
validator = EmailValidator()

# API key storage (in production, use a database or secure key management)
API_KEYS = {
    'demo_key_123': {
        'name': 'Demo Account',
        'rate_limit': 10,  # requests per minute
        'monthly_limit': 1000,
        'usage': 0,
        'last_reset': datetime.utcnow()
    },
    'premium_key_456': {
        'name': 'Premium Account',
        'rate_limit': 1000,  # requests per minute
        'monthly_limit': 50000,
        'usage': 0,
        'last_reset': datetime.utcnow()
    }
}

# Pricing constants
PRICING_PER_EMAIL = 0.001
PRICING_MONTHLY_50K = 29.0

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get API key from Authorization header or query parameter
        auth_header = request.headers.get('Authorization')
        api_key = None
        
        if auth_header and auth_header.startswith('Bearer '):
            api_key = auth_header[7:]  # Remove 'Bearer ' prefix
        elif request.args.get('api_key'):
            api_key = request.args.get('api_key')
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key required',
                'message': 'Provide API key in Authorization header or api_key parameter'
            }), 401
        
        if api_key not in API_KEYS:
            return jsonify({
                'success': False,
                'error': 'Invalid API key',
                'message': 'The provided API key is not valid'
            }), 401
        
        return f(*args, **kwargs)
    return decorated_function

def check_rate_limit(api_key):
    """Check and update rate limit for API key"""
    key_data = API_KEYS[api_key]
    now = datetime.utcnow()
    
    # Reset monthly usage at the start of each month
    if now.day == 1 and now.hour == 0 and key_data['last_reset'].month != now.month:
        key_data['usage'] = 0
        key_data['last_reset'] = now
    
    # Check rate limit (per minute)
    # Simple implementation - in production, use Redis or similar
    return True  # For now, allow all requests

def log_usage(api_key, email_count=1):
    """Log API key usage"""
    if api_key in API_KEYS:
        API_KEYS[api_key]['usage'] += email_count

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'endpoints': {
            'validate': 'POST /api/v1/validate',
            'batch_validate': 'POST /api/v1/validate/batch',
            'csv_validate': 'POST /api/v1/validate/csv',
            'pricing': 'GET /api/v1/pricing'
        }
    })

@app.route('/api/v1/validate', methods=['POST'])
@require_api_key
def validate_email():
    """
    Validate a single email address with API key authentication
    
    Request body:
    {
        "email": "user@example.com",
        "check_smtp": true  // optional, default true
    }
    
    Headers:
    Authorization: Bearer YOUR_API_KEY
    """
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing email in request body'
            }), 400
        
        # Get API key from request
        auth_header = request.headers.get('Authorization')
        api_key = auth_header[7:] if auth_header and auth_header.startswith('Bearer ') else request.args.get('api_key')
        
        # Check rate limit
        if not check_rate_limit(api_key):
            return jsonify({
                'success': False,
                'error': 'Rate limit exceeded',
                'message': 'You have exceeded your rate limit. Please try again later.'
            }), 429
        
        email = data['email']
        check_smtp = data.get('check_smtp', True)
        
        # Validate email
        result = validator.validate(email, check_smtp=check_smtp)
        
        # Log usage
        log_usage(api_key, 1)
        
        # Add API key info to response
        result['api_key'] = API_KEYS[api_key]['name']
        result['usage_today'] = API_KEYS[api_key]['usage']
        
        return jsonify({
            'success': True,
            'data': result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'message': str(e)
        }), 500

@app.route('/api/v1/validate/batch', methods=['POST'])
@require_api_key
def validate_batch():
    """
    Validate multiple email addresses with API key authentication
    
    Request body:
    {
        "emails": ["user1@example.com", "user2@example.com"],
        "check_smtp": true  // optional, default true
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'emails' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing emails in request body'
            }), 400
        
        # Get API key
        auth_header = request.headers.get('Authorization')
        api_key = auth_header[7:] if auth_header and auth_header.startswith('Bearer ') else request.args.get('api_key')
        
        # Check rate limit for batch
        if not check_rate_limit(api_key):
            return jsonify({
                'success': False,
                'error': 'Rate limit exceeded',
                'message': 'You have exceeded your rate limit. Please try again later.'
            }), 429
        
        emails = data['emails']
        check_smtp = data.get('check_smtp', True)
        
        if not isinstance(emails, list):
            return jsonify({
                'success': False,
                'error': 'emails must be an array'
            }), 400
        
        if len(emails) > 1000:
            return jsonify({
                'success': False,
                'error': 'Batch too large',
                'message': 'Maximum 1000 emails per batch'
            }), 400
        
        # Validate emails
        results = []
        for email in emails:
            result = validator.validate(email, check_smtp=check_smtp)
            results.append(result)
        
        # Log usage
        log_usage(api_key, len(emails))
        
        # Add API key info to response
        response_data = {
            'success': True,
            'data': results,
            'total_validated': len(emails),
            'api_key': API_KEYS[api_key]['name'],
            'usage_today': API_KEYS[api_key]['usage']
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Batch validation error',
            'message': str(e)
        }), 500

@app.route('/api/v1/validate/csv', methods=['POST'])
@require_api_key
def validate_csv():
    """
    Validate emails from CSV upload with API key authentication
    
    Request body (multipart/form-data):
    - file: CSV file with email column
    - email_column: Name of email column (optional, default 'email')
    - check_smtp: Whether to check SMTP (optional, default true)
    """
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Get API key
        auth_header = request.headers.get('Authorization')
        api_key = auth_header[7:] if auth_header and auth_header.startswith('Bearer ') else request.args.get('api_key')
        
        # Check rate limit
        if not check_rate_limit(api_key):
            return jsonify({
                'success': False,
                'error': 'Rate limit exceeded',
                'message': 'You have exceeded your rate limit. Please try again later.'
            }), 429
        
        # Check file size
        if request.content_length > config[env].MAX_FILE_SIZE:
            return jsonify({
                'success': False,
                'error': 'File too large',
                'message': f'Maximum file size is {config[env].MAX_FILE_SIZE / (1024*1024)}MB'
            }), 413
        
        # Get CSV parameters
        email_column = request.form.get('email_column', 'email')
        check_smtp = request.form.get('check_smtp', 'true').lower() == 'true'
        
        # Read CSV
        try:
            df = pd.read_csv(file)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Invalid CSV file',
                'message': str(e)
            }), 400
        
        # Check if email column exists
        if email_column not in df.columns:
            return jsonify({
                'success': False,
                'error': 'Email column not found',
                'message': f'Column "{email_column}" not found in CSV. Available columns: {list(df.columns)}'
            }), 400
        
        # Extract emails
        emails = df[email_column].dropna().tolist()
        
        if not emails:
            return jsonify({
                'success': False,
                'error': 'No valid emails found',
                'message': f'No valid email addresses found in column "{email_column}"'
            }), 400
        
        if len(emails) > 10000:
            return jsonify({
                'success': False,
                'error': 'CSV too large',
                'message': 'Maximum 10,000 emails per CSV file'
            }), 400
        
        # Validate emails
        results = []
        for email in emails:
            result = validator.validate(str(email), check_smtp=check_smtp)
            results.append(result)
        
        # Log usage
        log_usage(api_key, len(emails))
        
        # Create response DataFrame
        response_df = pd.DataFrame(results)
        
        # Add original email and validation status
        response_df['original_email'] = emails
        
        # Calculate total cost
        total_cost = len(emails) * PRICING_PER_EMAIL
        
        # Add API key info
        response_data = {
            'success': True,
            'data': response_df.to_dict('records'),
            'total_emails': len(emails),
            'total_cost': total_cost,
            'cost_per_email': PRICING_PER_EMAIL,
            'monthly_plan_cost': PRICING_MONTHLY_50K if len(emails) >= 50000 else None,
            'api_key': API_KEYS[api_key]['name'],
            'usage_today': API_KEYS[api_key]['usage'],
            'pricing_info': {
                'per_email': PRICING_PER_EMAIL,
                'monthly_50k': PRICING_MONTHLY_50K,
                'emails_included_monthly': 50000
            }
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'CSV validation error',
            'message': str(e)
        }), 500

@app.route('/api/v1/pricing', methods=['GET'])
def get_pricing():
    """Get pricing information"""
    return jsonify({
        'success': True,
        'data': {
            'per_email': PRICING_PER_EMAIL,
            'monthly_plan': {
                'cost': PRICING_MONTHLY_50K,
                'emails_included': 50000,
                'cost_per_email': PRICING_MONTHLY_50K / 50000
            },
            'api_key_required': True,
            'free_tier': False
        }
    })

@app.route('/api/v1/usage', methods=['GET'])
@require_api_key
def get_usage():
    """Get current API key usage"""
    auth_header = request.headers.get('Authorization')
    api_key = auth_header[7:] if auth_header and auth_header.startswith('Bearer ') else request.args.get('api_key')
    
    if api_key not in API_KEYS:
        return jsonify({
            'success': False,
            'error': 'Invalid API key'
        }), 401
    
    key_data = API_KEYS[api_key]
    now = datetime.utcnow()
    
    return jsonify({
        'success': True,
        'data': {
            'api_key_name': key_data['name'],
            'current_usage': key_data['usage'],
            'monthly_limit': key_data['monthly_limit'],
            'rate_limit_per_minute': key_data['rate_limit'],
            'usage_percentage': (key_data['usage'] / key_data['monthly_limit']) * 100,
            'monthly_reset_date': key_data['last_reset'].replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
        }
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Method not allowed',
        'message': 'The HTTP method is not allowed for this endpoint'
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

if __name__ == '__main__':
    app.run(debug=config[env].DEBUG, host='0.0.0.0', port=5000)
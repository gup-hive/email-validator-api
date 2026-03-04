"""
Email Validator API - Main Application
"""
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import io
from datetime import datetime
import os
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

# Pricing constants
PRICING_PER_EMAIL = 0.001
PRICING_MONTHLY_50K = 29.0

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/v1/validate', methods=['POST'])
def validate_email():
    """
    Validate a single email address
    
    Request body:
    {
        "email": "user@example.com",
        "check_smtp": true  // optional, default true
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({
                'error': 'Missing email in request body'
            }), 400
        
        email = data['email']
        check_smtp = data.get('check_smtp', True)
        
        # Validate email
        result = validator.validate(email, check_smtp=check_smtp)
        
        return jsonify({
            'success': True,
            'data': result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/validate/batch', methods=['POST'])
def validate_batch():
    """
    Validate multiple email addresses
    
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
                'error': 'Missing emails in request body'
            }), 400
        
        emails = data['emails']
        check_smtp = data.get('check_smtp', True)
        
        if not isinstance(emails, list):
            return jsonify({
                'error': 'emails must be an array'
            }), 400
        
        # Validate emails
        results = validator.validate_batch(emails, check_smtp=check_smtp)
        
        # Calculate statistics
        total = len(results)
        valid = sum(1 for r in results if r['is_valid'])
        invalid = total - valid
        disposable = sum(1 for r in results if r.get('is_disposable'))
        role_based = sum(1 for r in results if r.get('is_role_based'))
        
        return jsonify({
            'success': True,
            'data': {
                'results': results,
                'statistics': {
                    'total': total,
                    'valid': valid,
                    'invalid': invalid,
                    'disposable': disposable,
                    'role_based': role_based
                }
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/validate/csv', methods=['POST'])
def validate_csv():
    """
    Validate emails from CSV upload
    
    Form data:
    - file: CSV file with email column
    - email_column: Name of column containing emails (default: 'email')
    - check_smtp: Whether to check SMTP (default: true)
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'error': 'No file selected'
            }), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({
                'error': 'File must be a CSV'
            }), 400
        
        email_column = request.form.get('email_column', 'email')
        check_smtp = request.form.get('check_smtp', 'true').lower() == 'true'
        
        # Read CSV
        df = pd.read_csv(file)
        
        # Check if email column exists
        if email_column not in df.columns:
            return jsonify({
                'error': f'Column "{email_column}" not found in CSV'
            }), 400
        
        # Extract emails
        emails = df[email_column].dropna().astype(str).tolist()
        
        # Validate emails
        results = validator.validate_batch(emails, check_smtp=check_smtp)
        
        # Create results DataFrame
        results_df = pd.DataFrame(results)
        
        # Calculate cost
        total_emails = len(emails)
        cost = total_emails * PRICING_PER_EMAIL
        
        # Return JSON results
        return jsonify({
            'success': True,
            'data': {
                'total_emails': total_emails,
                'cost': round(cost, 4),
                'pricing': {
                    'per_email': PRICING_PER_EMAIL,
                    'monthly_50k': PRICING_MONTHLY_50K
                },
                'statistics': {
                    'valid': sum(1 for r in results if r['is_valid']),
                    'invalid': sum(1 for r in results if not r['is_valid']),
                    'disposable': sum(1 for r in results if r.get('is_disposable')),
                    'role_based': sum(1 for r in results if r.get('is_role_based'))
                },
                'results': results[:100],  # Return first 100 results
                'note': f'Showing first 100 of {total_emails} results. Use /api/v1/validate/csv/download to download full results.'
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/validate/csv/download', methods=['POST'])
def validate_csv_download():
    """
    Validate emails from CSV and download results as CSV
    
    Form data:
    - file: CSV file with email column
    - email_column: Name of column containing emails (default: 'email')
    - check_smtp: Whether to check SMTP (default: true)
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'error': 'No file selected'
            }), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({
                'error': 'File must be a CSV'
            }), 400
        
        email_column = request.form.get('email_column', 'email')
        check_smtp = request.form.get('check_smtp', 'true').lower() == 'true'
        
        # Read CSV
        df = pd.read_csv(file)
        
        # Check if email column exists
        if email_column not in df.columns:
            return jsonify({
                'error': f'Column "{email_column}" not found in CSV'
            }), 400
        
        # Extract emails
        emails = df[email_column].dropna().astype(str).tolist()
        
        # Validate emails
        results = validator.validate_batch(emails, check_smtp=check_smtp)
        
        # Create results DataFrame
        results_df = pd.DataFrame(results)
        
        # Flatten the nested structure
        output_df = pd.DataFrame({
            'email': [r['email'] for r in results],
            'is_valid': [r['is_valid'] for r in results],
            'quality_score': [r['quality_score'] for r in results],
            'is_disposable': [r.get('is_disposable', False) for r in results],
            'is_role_based': [r.get('is_role_based', False) for r in results],
            'syntax_valid': [r['checks']['syntax']['valid'] for r in results],
            'domain_valid': [r['checks']['domain']['valid'] for r in results],
            'smtp_valid': [r['checks']['smtp']['valid'] for r in results],
            'syntax_message': [r['checks']['syntax']['message'] for r in results],
            'domain_message': [r['checks']['domain']['message'] for r in results],
            'smtp_message': [r['checks']['smtp']['message'] for r in results]
        })
        
        # Create CSV file
        output = io.StringIO()
        output_df.to_csv(output, index=False)
        output.seek(0)
        
        # Send file
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='email_validation_results.csv'
        )
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/pricing', methods=['GET'])
def get_pricing():
    """Get pricing information"""
    return jsonify({
        'success': True,
        'data': {
            'per_email': PRICING_PER_EMAIL,
            'monthly_plans': [
                {
                    'name': 'Pay as you go',
                    'emails': 0,
                    'price': 0,
                    'price_per_email': PRICING_PER_EMAIL
                },
                {
                    'name': 'Starter',
                    'emails': 50000,
                    'price': PRICING_MONTHLY_50K,
                    'price_per_email': round(PRICING_MONTHLY_50K / 50000, 5)
                }
            ]
        }
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])

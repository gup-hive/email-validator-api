"""
Simple test script for Email Validator API
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validators.email_validator import EmailValidator

def test_validator():
    """Test the email validator"""
    print("=" * 60)
    print("Email Validator API - Test Script")
    print("=" * 60)
    print()
    
    # Initialize validator
    validator = EmailValidator()
    
    # Test emails
    test_emails = [
        "user@example.com",
        "admin@example.com",
        "info@example.com",
        "invalid-email",
        "user@nonexistent-domain-12345.com",
        "test@tempmail.com"
    ]
    
    print("Testing individual emails:")
    print("-" * 60)
    
    for email in test_emails:
        print(f"\nEmail: {email}")
        result = validator.validate(email, check_smtp=False)  # Skip SMTP for faster testing
        print(f"  Valid: {result['is_valid']}")
        print(f"  Quality Score: {result['quality_score']}")
        print(f"  Disposable: {result.get('is_disposable', 'N/A')}")
        print(f"  Role-based: {result.get('is_role_based', 'N/A')}")
        print(f"  Syntax: {result['checks']['syntax']['message']}")
        if 'domain' in result['checks']:
            print(f"  Domain: {result['checks']['domain']['message']}")
        else:
            print(f"  Domain: Skipped (syntax failed)")
        if 'smtp' in result['checks']:
            print(f"  SMTP: {result['checks']['smtp']['message']}")
    
    print("\n" + "=" * 60)
    print("Batch validation test:")
    print("-" * 60)
    
    # Test batch validation
    batch_results = validator.validate_batch(test_emails[:4], check_smtp=False)
    
    for result in batch_results:
        print(f"\n{result['email']}: {'✓' if result['is_valid'] else '✗'} (Score: {result['quality_score']})")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)

if __name__ == '__main__':
    test_validator()

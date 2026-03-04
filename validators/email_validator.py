"""
Main Email Validator - combines all validation checks
"""
from .syntax_validator import SyntaxValidator
from .domain_validator import DomainValidator
from .smtp_validator import SMTPValidator
from .disposable_detector import DisposableEmailDetector
from .role_based_detector import RoleBasedEmailDetector

class EmailValidator:
    """Main email validator that combines all validation checks"""
    
    def __init__(self, smtp_timeout=10, mx_timeout=5, strict_syntax=False):
        """
        Initialize email validator
        
        Args:
            smtp_timeout (int): SMTP connection timeout in seconds
            mx_timeout (int): DNS query timeout in seconds
            strict_syntax (bool): Use strict RFC 5322 syntax validation
        """
        self.syntax_validator = SyntaxValidator(strict=strict_syntax)
        self.domain_validator = DomainValidator(timeout=mx_timeout)
        self.smtp_validator = SMTPValidator(timeout=smtp_timeout)
        self.disposable_detector = DisposableEmailDetector()
        self.role_based_detector = RoleBasedEmailDetector()
    
    def validate(self, email: str, check_smtp=True) -> dict:
        """
        Perform full email validation
        
        Args:
            email (str): Email address to validate
            check_smtp (bool): Whether to perform SMTP verification
            
        Returns:
            dict: Complete validation result with all checks
        """
        if not email or not isinstance(email, str):
            return {
                'email': email,
                'is_valid': False,
                'checks': {
                    'syntax': {'valid': False, 'message': 'Empty or invalid email'}
                }
            }
        
        email = email.strip()
        domain = email.split('@')[-1] if '@' in email else None
        
        # Initialize result structure
        result = {
            'email': email,
            'is_valid': False,
            'is_disposable': False,
            'is_role_based': False,
            'quality_score': 0,
            'checks': {}
        }
        
        # Step 1: Syntax validation
        syntax_result = self.syntax_validator.validate(email)
        result['checks']['syntax'] = syntax_result
        
        if not syntax_result['valid']:
            return result
        
        # Step 2: Domain/MX validation
        domain_result = self.domain_validator.validate(domain)
        result['checks']['domain'] = domain_result
        
        if not domain_result['valid']:
            return result
        
        # Step 3: Disposable email detection
        disposable_result = self.disposable_detector.is_disposable(email)
        result['checks']['disposable'] = disposable_result
        
        # Step 4: Role-based email detection
        role_result = self.role_based_detector.is_role_based(email)
        result['checks']['role_based'] = role_result
        
        # Step 5: SMTP verification (optional)
        if check_smtp:
            mx_records = domain_result.get('mx_records', [])
            smtp_result = self.smtp_validator.validate(email, mx_records)
            result['checks']['smtp'] = smtp_result
        else:
            result['checks']['smtp'] = {
                'valid': None,
                'message': 'SMTP check skipped'
            }
        
        # Determine overall validity
        # Email is valid if:
        # - Syntax is valid
        # - Domain has MX records
        # - Not disposable (optional - depends on use case)
        # - SMTP check either passed or was inconclusive (None)
        
        smtp_valid = result['checks']['smtp']['valid']
        is_disposable = disposable_result['is_disposable']
        is_role_based = role_result['is_role_based']
        
        # Valid syntax + valid domain + (SMTP valid OR SMTP inconclusive)
        result['is_valid'] = (
            syntax_result['valid'] and
            domain_result['valid'] and
            (smtp_valid or smtp_valid is None)
        )
        
        # Add flags
        result['is_disposable'] = is_disposable
        result['is_role_based'] = is_role_based
        
        # Add quality score (0-100)
        result['quality_score'] = self._calculate_quality_score(result)
        
        return result
    
    def _calculate_quality_score(self, result: dict) -> int:
        """Calculate quality score based on validation results"""
        score = 0
        
        checks = result.get('checks', {})
        
        # Syntax: 30 points
        if checks.get('syntax', {}).get('valid'):
            score += 30
        
        # Domain: 30 points
        if checks.get('domain', {}).get('valid'):
            score += 30
        
        # SMTP: 30 points (or 15 if inconclusive)
        smtp_valid = checks.get('smtp', {}).get('valid')
        if smtp_valid is True:
            score += 30
        elif smtp_valid is None:
            score += 15
        
        # Deductions
        if result.get('is_disposable'):
            score -= 30
        
        if result.get('is_role_based'):
            score -= 10
        
        return max(0, min(100, score))
    
    def validate_batch(self, emails: list, check_smtp=True) -> list:
        """
        Validate multiple emails in batch
        
        Args:
            emails (list): List of email addresses
            check_smtp (bool): Whether to perform SMTP verification
            
        Returns:
            list: List of validation results
        """
        results = []
        for email in emails:
            result = self.validate(email, check_smtp=check_smtp)
            results.append(result)
        return results

"""
Email Syntax Validator
"""
import re

class SyntaxValidator:
    """Validates email address syntax according to RFC 5322"""
    
    # RFC 5322 compliant email regex
    EMAIL_REGEX = re.compile(
        r"(^[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*"
        r"@(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+"
        r"[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?$)"
    )
    
    # Simplified regex for better performance
    SIMPLE_REGEX = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    def __init__(self, strict=False):
        """
        Initialize validator
        
        Args:
            strict (bool): Use strict RFC 5322 validation (slower)
        """
        self.strict = strict
        self.pattern = self.EMAIL_REGEX if strict else self.SIMPLE_REGEX
    
    def validate(self, email: str) -> dict:
        """
        Validate email syntax
        
        Args:
            email (str): Email address to validate
            
        Returns:
            dict: Validation result with 'valid' and 'message' keys
        """
        if not email or not isinstance(email, str):
            return {
                'valid': False,
                'message': 'Email is empty or invalid type'
            }
        
        email = email.strip().lower()
        
        # Basic length checks
        if len(email) > 254:
            return {
                'valid': False,
                'message': 'Email exceeds maximum length of 254 characters'
            }
        
        local_part, domain = self._split_email(email)
        
        if not local_part or not domain:
            return {
                'valid': False,
                'message': 'Invalid email format'
            }
        
        if len(local_part) > 64:
            return {
                'valid': False,
                'message': 'Local part exceeds maximum length of 64 characters'
            }
        
        if len(domain) > 255:
            return {
                'valid': False,
                'message': 'Domain exceeds maximum length of 255 characters'
            }
        
        # Pattern validation
        if not self.pattern.match(email):
            return {
                'valid': False,
                'message': 'Invalid email syntax'
            }
        
        return {
            'valid': True,
            'message': 'Valid syntax'
        }
    
    def _split_email(self, email: str) -> tuple:
        """Split email into local part and domain"""
        parts = email.rsplit('@', 1)
        return parts if len(parts) == 2 else (None, None)

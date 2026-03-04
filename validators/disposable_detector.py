"""
Disposable Email Detector
"""
import os
import re
from typing import Set, Dict

class DisposableEmailDetector:
    """Detects disposable email addresses"""
    
    def __init__(self, data_file=None):
        """
        Initialize detector with disposable email domain list
        
        Args:
            data_file (str): Path to disposable email domains file
        """
        self.disposable_domains = set()
        self._load_domains(data_file)
    
    def _load_domains(self, data_file=None):
        """Load disposable email domains from file"""
        if data_file and os.path.exists(data_file):
            with open(data_file, 'r') as f:
                domains = [line.strip() for line in f if line.strip()]
                self.disposable_domains.update(domains)
        
        # Load built-in list (common disposable domains)
        builtin_domains = [
            # Temp mail services
            'tempmail.com', 'guerrillamail.com', 'mailinator.com',
            '10minutemail.com', 'throwawaymail.com', 'yopmail.com',
            'mailnesia.com', 'getairmail.com', 'temp-mail.org',
            'sharklasers.com', 'guerrillamail.net', 'guerrillamail.org',
            'guerrillamail.biz', 'guerrillamail.de', 'spambog.com',
            'trash-mail.com', 'tempmail.de', 'trashmail.com',
            'temporarymail.com', 'temporary-mail.com', 'tempmail.net',
            'trashmail.net', 'trashmail.org', 'trashmail.io',
            'mailtemp.com', 'mailtemp.net', 'mailtemp.org',
            'disposablemail.com', 'disposable-email.com',
            'incognitomail.com', 'anonmail.net', 'anonmail.de',
            'spambox.us', 'spambox.info', 'spambox.co',
            'spambox.org', 'spambox.net', 'spambox.me',
            'spamgourmet.com', 'spamherelots.com', 'spamhereplease.com',
            'recursor.net', 'recursor.org', 'recursor.info',
            'spamfree24.net', 'spamfree24.org', 'spamfree24.info',
            'spamfree24.com', 'spamfree24.de', 'spamfree24.eu',
            'trash-mail.de', 'trash-mail.at', 'trash-mail.ch',
            'trash-mail.fr', 'trash-mail.it', 'trash-mail.nl',
            'trash-mail.pl', 'trash-mail.ru', 'trash-mail.se',
            'trash-mail.es', 'trash-mail.co.uk', 'trash-mail.com.au',
            'throwawaymail.com', 'throwawaymail.net', 'throwawaymail.org',
            'throwawaymail.info', 'throwawaymail.biz', 'throwaway-email.com',
            'throwaway-email.net', 'throwaway-email.org', 'throwaway-email.info',
            'tempmail.net', 'tempmail.org', 'tempmail.info', 'tempmail.biz',
            'tempmail.co', 'tempmail.io', 'tempmail.me', 'tempmail.us',
            'tempmail.ca', 'tempmail.eu', 'tempmail.asia', 'tempmail.de',
            'tempmail.fr', 'tempmail.es', 'tempmail.it', 'tempmail.nl',
            'tempmail.pl', 'tempmail.ru', 'tempmail.se', 'tempmail.co.uk',
            '10minutemail.co', '10minutemail.net', '10minutemail.org',
            '10minutemail.info', '10minutemail.biz', '10minutemail.de',
            '10minutemail.fr', '10minutemail.es', '10minutemail.it',
            '10minutemail.nl', '10minutemail.pl', '10minutemail.ru',
            '10minutemail.se', '10minutemail.co.uk', '10minutemail.com.au',
            'guerrillamailblock.com', 'guerrillamail.com', 'guerrillamail.net',
            'guerrillamail.org', 'guerrillamail.biz', 'guerrillamail.de',
            'guerrillamail.fr', 'guerrillamail.es', 'guerrillamail.it',
            'guerrillamail.nl', 'guerrillamail.pl', 'guerrillamail.ru',
            'guerrillamail.se', 'guerrillamail.co.uk', 'guerrillamail.com.au',
            'mailinator.com', 'mailinator.net', 'mailinator.org', 'mailinator.info',
            'mailinator.biz', 'mailinator.co', 'mailinator.io', 'mailinator.me',
            'mailinator.us', 'mailinator.ca', 'mailinator.eu', 'mailinator.asia',
            'mailinator.de', 'mailinator.fr', 'mailinator.es', 'mailinator.it',
            'mailinator.nl', 'mailinator.pl', 'mailinator.ru', 'mailinator.se',
            'mailinator.co.uk', 'mailinator.com.au', 'suremail.info', 'suremail.net',
            'suremail.org', 'suremail.com', 'suremail.biz', 'suremail.co',
            'suremail.io', 'suremail.me', 'suremail.us', 'suremail.ca',
            'suremail.eu', 'suremail.asia', 'suremail.de', 'suremail.fr',
            'suremail.es', 'suremail.it', 'suremail.nl', 'suremail.pl',
            'suremail.ru', 'suremail.se', 'suremail.co.uk', 'suremail.com.au',
            'trashymail.com', 'trashymail.net', 'trashymail.org', 'trashymail.info',
            'trashymail.biz', 'trashymail.co', 'trashymail.io', 'trashymail.me',
            'trashymail.us', 'trashymail.ca', 'trashymail.eu', 'trashymail.asia',
            'trashymail.de', 'trashymail.fr', 'trashymail.es', 'trashymail.it',
            'trashymail.nl', 'trashymail.pl', 'trashymail.ru', 'trashymail.se',
            'trashymail.co.uk', 'trashymail.com.au'
        ]
        
        self.disposable_domains.update(builtin_domains)
    
    def is_disposable(self, email: str) -> dict:
        """
        Check if email domain is disposable
        
        Args:
            email (str): Email address to check
            
        Returns:
            dict: Result with 'is_disposable' and 'message' keys
        """
        if not email or not isinstance(email, str):
            return {
                'is_disposable': False,
                'message': 'Email is empty or invalid type'
            }
        
        email = email.strip().lower()
        
        # Extract domain from email
        if '@' not in email:
            return {
                'is_disposable': False,
                'message': 'Invalid email format'
            }
        
        domain = email.split('@')[1]
        
        # Check if domain is in disposable list
        if domain in self.disposable_domains:
            return {
                'is_disposable': True,
                'message': f'Domain {domain} is a disposable email service'
            }
        
        return {
            'is_disposable': False,
            'message': f'Domain {domain} is not a disposable email service'
        }
    
    def add_domain(self, domain: str):
        """Add a domain to the disposable list"""
        self.disposable_domains.add(domain.lower().strip())
    
    def remove_domain(self, domain: str):
        """Remove a domain from the disposable list"""
        self.disposable_domains.discard(domain.lower().strip())

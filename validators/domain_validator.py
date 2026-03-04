"""
Domain and MX Record Validator
"""
import dns.resolver
import dns.exception
from typing import List, Dict

class DomainValidator:
    """Validates email domain by checking DNS records"""
    
    COMMON_MX_RECORDS = [
        'smtp.', 'mail.', 'email.', 'mx.', 'exchange.'
    ]
    
    def __init__(self, timeout=5):
        """
        Initialize validator
        
        Args:
            timeout (int): DNS query timeout in seconds
        """
        self.timeout = timeout
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = timeout
        self.resolver.lifetime = timeout
    
    def validate(self, domain: str) -> dict:
        """
        Validate domain by checking DNS records
        
        Args:
            domain (str): Domain to validate
            
        Returns:
            dict: Validation result with 'valid', 'message', and optional 'mx_records'
        """
        if not domain or not isinstance(domain, str):
            return {
                'valid': False,
                'message': 'Domain is empty or invalid type'
            }
        
        domain = domain.strip().lower()
        
        if not domain or '.' not in domain:
            return {
                'valid': False,
                'message': 'Invalid domain format'
            }
        
        # Check MX records first
        mx_result = self._check_mx_records(domain)
        if mx_result['valid']:
            return mx_result
        
        # If no MX records, check A record (some domains use A record for mail)
        a_result = self._check_a_record(domain)
        if a_result['valid']:
            return a_result
        
        return {
            'valid': False,
            'message': f'No MX or A records found for domain {domain}'
        }
    
    def _check_mx_records(self, domain: str) -> dict:
        """Check for MX records"""
        try:
            mx_records = self.resolver.resolve(domain, 'MX', raise_on_no_answer=False)
            
            if not mx_records.rrset:
                return {
                    'valid': False,
                    'message': f'No MX records found for {domain}'
                }
            
            # Extract MX server addresses
            mx_servers = [str(rdata.exchange).rstrip('.') for rdata in mx_records]
            
            return {
                'valid': True,
                'message': f'Domain has {len(mx_servers)} MX record(s)',
                'mx_records': mx_servers
            }
        
        except dns.resolver.NoAnswer:
            # No MX records, might use A record
            return {
                'valid': False,
                'message': f'No MX records for {domain}'
            }
        
        except dns.resolver.NXDOMAIN:
            return {
                'valid': False,
                'message': f'Domain {domain} does not exist'
            }
        
        except (dns.resolver.Timeout, dns.exception.Timeout):
            return {
                'valid': False,
                'message': f'DNS query timed out for {domain}'
            }
        
        except Exception as e:
            return {
                'valid': False,
                'message': f'DNS error: {str(e)}'
            }
    
    def _check_a_record(self, domain: str) -> dict:
        """Check for A record as fallback"""
        try:
            a_records = self.resolver.resolve(domain, 'A', raise_on_no_answer=False)
            
            if not a_records.rrset:
                return {
                    'valid': False,
                    'message': f'No A records found for {domain}'
                }
            
            return {
                'valid': True,
                'message': f'Domain has A record (no MX)',
                'mx_records': [domain]
            }
        
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            return {
                'valid': False,
                'message': f'Domain {domain} has no mail records'
            }
        
        except Exception as e:
            return {
                'valid': False,
                'message': f'DNS A record error: {str(e)}'
            }

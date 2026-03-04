"""
SMTP Mailbox Validator
"""
import smtplib
import socket
from email.utils import parseaddr
import re
from typing import Optional

class SMTPValidator:
    """Validates email mailbox by connecting to SMTP server"""
    
    def __init__(self, timeout=10):
        """
        Initialize validator
        
        Args:
            timeout (int): SMTP connection timeout in seconds
        """
        self.timeout = timeout
    
    def validate(self, email: str, mx_records: list) -> dict:
        """
        Validate mailbox by connecting to SMTP server
        
        Args:
            email (str): Full email address
            mx_records (list): List of MX record domains
            
        Returns:
            dict: Validation result with 'valid', 'message', and optional 'smtp_response'
        """
        if not email or not isinstance(email, str):
            return {
                'valid': False,
                'message': 'Email is empty or invalid type'
            }
        
        if not mx_records:
            return {
                'valid': False,
                'message': 'No MX records provided'
            }
        
        email = email.strip().lower()
        
        # Try each MX server until one works
        for mx_server in mx_records:
            result = self._check_smtp_server(email, mx_server)
            if result['valid'] is not None:
                return result
        
        return {
            'valid': False,
            'message': 'Could not connect to any SMTP server'
        }
    
    def _check_smtp_server(self, email: str, mx_server: str) -> dict:
        """
        Check mailbox on specific SMTP server
        
        Args:
            email (str): Email address to verify
            mx_server (str): SMTP server hostname
            
        Returns:
            dict: Validation result
        """
        try:
            # Create SMTP connection
            with smtplib.SMTP(timeout=self.timeout) as server:
                server.set_debuglevel(0)
                
                # Connect to MX server
                server.connect(mx_server, 25)
                
                # Get server greeting
                greeting = server.docmd('NOOP')[1].decode('utf-8', errors='ignore')
                
                # Start TLS if available
                try:
                    server.starttls()
                except smtplib.SMTPException:
                    # Some servers don't support STARTTLS
                    pass
                
                # Say hello
                server.ehlo_or_helo_if_needed()
                
                # Extract local part from email
                local_part = email.split('@')[0]
                domain = email.split('@')[1]
                
                # Check if server supports VRFY or EXPN
                if server.has_extn('vrfy'):
                    try:
                        response = server.verify(email)
                        if response[0] == 250:
                            return {
                                'valid': True,
                                'message': f'Mailbox exists (VRFY confirmed)',
                                'smtp_response': response[1].decode('utf-8', errors='ignore')
                            }
                    except smtplib.SMTPException:
                        pass
                
                # Try RCPT TO method
                try:
                    # MAIL FROM command
                    server.mail('test@example.com')
                    
                    # RCPT TO command
                    code, response = server.rcpt(email)
                    
                    if code == 250:
                        return {
                            'valid': True,
                            'message': 'Mailbox exists (RCPT TO confirmed)',
                            'smtp_response': response.decode('utf-8', errors='ignore')
                        }
                    elif code == 550 or code == 553:
                        return {
                            'valid': False,
                            'message': 'Mailbox does not exist',
                            'smtp_response': response.decode('utf-8', errors='ignore')
                        }
                    else:
                        # Could be greylisting or temporary issue
                        return {
                            'valid': None,
                            'message': f'Unable to verify (SMTP {code})',
                            'smtp_response': response.decode('utf-8', errors='ignore')
                        }
                
                except smtplib.SMTPException as e:
                    return {
                        'valid': None,
                        'message': f'SMTP error: {str(e)}'
                    }
        
        except socket.timeout:
            return {
                'valid': None,
                'message': f'SMTP connection timeout to {mx_server}'
            }
        
        except socket.gaierror:
            return {
                'valid': False,
                'message': f'Could not resolve SMTP server {mx_server}'
            }
        
        except ConnectionRefusedError:
            return {
                'valid': False,
                'message': f'SMTP server {mx_server} refused connection'
            }
        
        except Exception as e:
            return {
                'valid': None,
                'message': f'SMTP validation error: {str(e)}'
            }
        
        return {
            'valid': None,
            'message': 'Could not verify mailbox'
        }

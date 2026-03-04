"""
Role-based Email Detector
"""
import re

class RoleBasedEmailDetector:
    """Detects role-based email addresses (admin@, info@, etc.)"""
    
    def __init__(self):
        """Initialize detector with role-based email prefixes"""
        self.role_prefixes = [
            # Common administrative roles
            'admin', 'administrator', 'webmaster', 'hostmaster', 'postmaster',
            'abuse', 'spam', 'security', 'support', 'help', 'contact',
            'info', 'information', 'sales', 'billing', 'finance', 'accounting',
            'enquiries', 'inquiry', 'office', 'hr', 'jobs', 'career',
            'marketing', 'advertising', 'promo', 'promotions',
            'tech', 'technical', 'it', 'systems', 'network', 'server',
            'operations', 'ops', 'management', 'manager',
            'noreply', 'no-reply', 'donotreply', 'do-not-reply', 'no_reply',
            'auto-reply', 'auto', 'bot', 'robot', 'daemon',
            'service', 'services', 'notifications', 'alerts',
            'news', 'newsletter', 'updates', 'announce', 'announcements',
            'feedback', 'enquiries', 'questions', 'ask', 'askus',
            'team', 'staff', 'crew', 'company', 'contact-us',
            'customerservice', 'customer-service', 'customer_service',
            'service', 'services', 'support', 'helpdesk',
            'billing', 'accounts', 'accounting', 'finance',
            'legal', 'legal-dept', 'legal_dept', 'legaldepartment',
            'pr', 'press', 'media', 'publicrelations', 'public-relations',
            'privacy', 'dpo', 'gdpr', 'compliance',
            'reception', 'frontdesk', 'front-desk', 'front_desk',
            'booking', 'bookings', 'reservations', 'reservation',
            'orders', 'order', 'sales', 'quote', 'quotes',
            'partner', 'partners', 'partner-relations', 'partnerrelations',
            'affiliate', 'affiliates', 'vendor', 'vendors',
            'supply', 'logistics', 'shipping', 'delivery',
            'returns', 'refund', 'refunds', 'complaints',
            'quality', 'quality-assurance', 'qa', 'testing',
            'development', 'dev', 'engineering', 'engineers',
            'design', 'creative', 'art', 'production',
            'warehouse', 'stock', 'inventory', 'procurement'
        ]
        
        # Create regex pattern for role-based emails
        self.pattern = re.compile(
            r'^(' + '|'.join(self.role_prefixes) + r')$',
            re.IGNORECASE
        )
    
    def is_role_based(self, email: str) -> dict:
        """
        Check if email is role-based
        
        Args:
            email (str): Email address to check
            
        Returns:
            dict: Result with 'is_role_based', 'role' and 'message' keys
        """
        if not email or not isinstance(email, str):
            return {
                'is_role_based': False,
                'role': None,
                'message': 'Email is empty or invalid type'
            }
        
        email = email.strip().lower()
        
        # Extract local part from email
        if '@' not in email:
            return {
                'is_role_based': False,
                'role': None,
                'message': 'Invalid email format'
            }
        
        local_part = email.split('@')[0]
        
        # Check if it matches role-based pattern
        match = self.pattern.match(local_part)
        
        if match:
            role = match.group(1).lower()
            return {
                'is_role_based': True,
                'role': role,
                'message': f'Email is role-based: {role}@'
            }
        
        return {
            'is_role_based': False,
            'role': None,
            'message': 'Email is not role-based'
        }
    
    def get_role_list(self) -> list:
        """Return list of all role-based prefixes"""
        return self.role_prefixes.copy()
    
    def add_role(self, role: str):
        """Add a role prefix to the detector"""
        role = role.lower().strip()
        if role and role not in self.role_prefixes:
            self.role_prefixes.append(role)
            # Update pattern
            self.pattern = re.compile(
                r'^(' + '|'.join(self.role_prefixes) + r')@',
                re.IGNORECASE
            )
    
    def remove_role(self, role: str):
        """Remove a role prefix from the detector"""
        role = role.lower().strip()
        if role in self.role_prefixes:
            self.role_prefixes.remove(role)
            # Update pattern
            self.pattern = re.compile(
                r'^(' + '|'.join(self.role_prefixes) + r')@',
                re.IGNORECASE
            )

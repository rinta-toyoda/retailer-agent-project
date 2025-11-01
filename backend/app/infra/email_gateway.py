"""
Email Gateway - Low Stock Alert Notifications
Used in Low Stock Monitor flow for admin alerts.
Marking Criteria: 4.4 (Incorporation of Advanced Technologies)
"""

import os
from typing import List, Dict
from datetime import datetime


class EmailGateway:
    """
    Mock email gateway for sending low stock alerts.
    In production, this would integrate with services like SendGrid, AWS SES, or SMTP.
    """

    def __init__(self, enabled: bool = None, smtp_host: str = None):
        """
        Initialize email gateway.

        Args:
            enabled: Whether email sending is enabled
            smtp_host: SMTP server host (mock)
        """
        self.enabled = enabled if enabled is not None else os.getenv("EMAIL_ENABLED", "false").lower() == "true"
        self.smtp_host = smtp_host or os.getenv("EMAIL_HOST", "smtp.example.com")
        self.sent_emails = []  # Track sent emails for logging/debugging

    def send_low_stock_alert(self, item_sku: str, current_qty: int, threshold: int, recipients: List[str] = None) -> bool:
        """
        Send low stock alert email to admins.
        Maps to Low Stock Monitor → EmailNotifier in sequence diagram.

        Args:
            item_sku: SKU of low stock item
            current_qty: Current stock quantity
            threshold: Low stock threshold
            recipients: List of email addresses (default: admin emails)

        Returns:
            True if email sent successfully
        """
        if not self.enabled:
            print(f"[EMAIL] Email sending disabled. Would send low stock alert for SKU: {item_sku}")
            return True

        recipients = recipients or self._get_admin_emails()

        email = {
            "to": recipients,
            "subject": f"Low Stock Alert: {item_sku}",
            "body": self._generate_low_stock_body(item_sku, current_qty, threshold),
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Mock sending (in production, use SMTP or email service API)
        self.sent_emails.append(email)
        print(f"[EMAIL] Low stock alert sent for SKU: {item_sku} (qty: {current_qty}/{threshold}) to {len(recipients)} recipients")

        return True

    def _generate_low_stock_body(self, sku: str, current_qty: int, threshold: int) -> str:
        """
        Generate email body for low stock alert.

        Args:
            sku: Product SKU
            current_qty: Current stock level
            threshold: Configured threshold

        Returns:
            Email body text
        """
        return f"""
Low Stock Alert

Product SKU: {sku}
Current Stock: {current_qty} units
Threshold: {threshold} units

Action Required: Please restock this item to maintain inventory levels.

Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

---
Retailer AI Agent System
Automated Inventory Monitoring
        """.strip()

    def _get_admin_emails(self) -> List[str]:
        """
        Get admin email addresses from configuration.

        Returns:
            List of admin email addresses
        """
        admin_email = os.getenv("EMAIL_USER", "admin@retailer.com")
        return [admin_email]

    def get_sent_emails(self) -> List[Dict]:
        """
        Retrieve sent emails (for testing/debugging).

        Returns:
            List of sent email records
        """
        return self.sent_emails


# Global instance
email_gateway = EmailGateway()

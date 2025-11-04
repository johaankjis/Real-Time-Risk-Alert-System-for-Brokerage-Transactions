"""
Alert System
Handles alert notifications via Slack and Email
"""

import os
from datetime import datetime
from typing import Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Alert configuration
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL', '')
ALERT_EMAIL_FROM = os.getenv('ALERT_EMAIL_FROM', 'alerts@brokerage.com')
ALERT_EMAIL_TO = os.getenv('ALERT_EMAIL_TO', 'risk-team@brokerage.com')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')


class AlertSystem:
    """Manages alert notifications"""
    
    def __init__(self):
        self.slack_enabled = bool(SLACK_WEBHOOK_URL)
        self.email_enabled = bool(SMTP_USERNAME and SMTP_PASSWORD)
    
    def format_alert_message(self, alert: Dict) -> str:
        """Format alert message for notifications"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        message = f"""
🚨 RISK ALERT - {alert['severity']}

Type: {alert['alert_type']}
Entity: {alert['entity_type']} - {alert['entity_id']}
Time: {timestamp}

{alert['message']}

Threshold: ${alert.get('threshold_value', 0):,.2f}
Current Value: ${alert.get('current_value', 0):,.2f}
"""
        return message.strip()
    
    def send_slack_alert(self, alert: Dict):
        """Send alert to Slack"""
        if not self.slack_enabled:
            return
        
        try:
            import requests
            
            # Map severity to color
            color_map = {
                'LOW': '#36a64f',
                'MEDIUM': '#ff9900',
                'HIGH': '#ff6600',
                'CRITICAL': '#ff0000'
            }
            
            payload = {
                'attachments': [{
                    'color': color_map.get(alert['severity'], '#808080'),
                    'title': f"🚨 {alert['alert_type']} - {alert['severity']}",
                    'text': alert['message'],
                    'fields': [
                        {
                            'title': 'Entity',
                            'value': f"{alert['entity_type']}: {alert['entity_id']}",
                            'short': True
                        },
                        {
                            'title': 'Threshold',
                            'value': f"${alert.get('threshold_value', 0):,.2f}",
                            'short': True
                        },
                        {
                            'title': 'Current Value',
                            'value': f"${alert.get('current_value', 0):,.2f}",
                            'short': True
                        }
                    ],
                    'footer': 'Risk Alert System',
                    'ts': int(datetime.now().timestamp())
                }]
            }
            
            response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
            response.raise_for_status()
            
        except Exception as e:
            print(f"Error sending Slack alert: {e}")
    
    def send_email_alert(self, alert: Dict):
        """Send alert via email"""
        if not self.email_enabled:
            return
        
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = ALERT_EMAIL_FROM
            msg['To'] = ALERT_EMAIL_TO
            msg['Subject'] = f"🚨 Risk Alert: {alert['alert_type']} - {alert['severity']}"
            
            body = self.format_alert_message(alert)
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)
            
        except Exception as e:
            print(f"Error sending email alert: {e}")
    
    def send_alert(self, alert: Dict):
        """Send alert via all configured channels"""
        # Always log to console
        print(f"[ALERT] {alert['severity']}: {alert['message']}")
        
        # Send to Slack
        if self.slack_enabled:
            self.send_slack_alert(alert)
        
        # Send via email
        if self.email_enabled:
            self.send_email_alert(alert)
        
        # If no external channels configured, just log
        if not self.slack_enabled and not self.email_enabled:
            print("  (No external alert channels configured - check .env file)")


# Test function
if __name__ == "__main__":
    alert_system = AlertSystem()
    
    test_alert = {
        'alert_type': 'HIGH_CLIENT_EXPOSURE',
        'severity': 'HIGH',
        'entity_type': 'CLIENT',
        'entity_id': 'CLIENT_001',
        'message': 'Client CLIENT_001 exposure $1,250,000.00 exceeds threshold $1,000,000.00',
        'threshold_value': 1000000.0,
        'current_value': 1250000.0
    }
    
    print("Testing alert system...")
    alert_system.send_alert(test_alert)
    print("Test complete!")

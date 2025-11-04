"""
Test script for the alert system
Generates test alerts to verify Slack and email integration
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from alert_system import AlertSystem

# Load environment variables
load_dotenv()


def test_alerts():
    """Test all alert types and severities"""
    
    alert_system = AlertSystem()
    
    print("=" * 60)
    print("Alert System Test")
    print("=" * 60)
    print()
    
    # Check configuration
    print("Configuration:")
    print(f"  Slack enabled: {alert_system.slack_enabled}")
    print(f"  Email enabled: {alert_system.email_enabled}")
    print()
    
    if not alert_system.slack_enabled and not alert_system.email_enabled:
        print("⚠️  No external alert channels configured!")
        print("   Alerts will only be logged to console.")
        print("   Configure SLACK_WEBHOOK_URL or SMTP settings in .env")
        print()
    
    # Test alerts
    test_cases = [
        {
            'name': 'High Client Exposure',
            'alert': {
                'alert_type': 'HIGH_CLIENT_EXPOSURE',
                'severity': 'HIGH',
                'entity_type': 'CLIENT',
                'entity_id': 'CLIENT_001',
                'message': 'Client CLIENT_001 exposure $1,250,000.00 exceeds threshold $1,000,000.00',
                'threshold_value': 1000000.0,
                'current_value': 1250000.0
            }
        },
        {
            'name': 'Critical Symbol Exposure',
            'alert': {
                'alert_type': 'HIGH_SYMBOL_EXPOSURE',
                'severity': 'CRITICAL',
                'entity_type': 'SYMBOL',
                'entity_id': 'AAPL',
                'message': 'Symbol AAPL exposure $850,000.00 exceeds threshold $500,000.00',
                'threshold_value': 500000.0,
                'current_value': 850000.0
            }
        },
        {
            'name': 'High Transaction Velocity',
            'alert': {
                'alert_type': 'HIGH_TRANSACTION_VELOCITY',
                'severity': 'HIGH',
                'entity_type': 'CLIENT',
                'entity_id': 'CLIENT_005',
                'message': 'CLIENT CLIENT_005 has 15 transactions in last 60s (threshold: 10)',
                'threshold_value': 10.0,
                'current_value': 15.0
            }
        },
        {
            'name': 'Anomaly Detection',
            'alert': {
                'alert_type': 'ANOMALY_DETECTED',
                'severity': 'MEDIUM',
                'entity_type': 'SYSTEM',
                'entity_id': 'TRANSACTION_MONITOR',
                'message': 'Anomalous transaction value $5,500,000.00 detected (z-score: 4.2)',
                'threshold_value': 2000000.0,
                'current_value': 5500000.0
            }
        }
    ]
    
    print("Sending test alerts...")
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}/{len(test_cases)}: {test_case['name']}")
        alert_system.send_alert(test_case['alert'])
        print()
    
    print("=" * 60)
    print("Test complete!")
    print()
    
    if alert_system.slack_enabled:
        print("✓ Check your Slack channel for test alerts")
    
    if alert_system.email_enabled:
        print("✓ Check your email inbox for test alerts")
    
    if not alert_system.slack_enabled and not alert_system.email_enabled:
        print("ℹ Configure alert channels in .env to receive notifications")
    
    print()


if __name__ == "__main__":
    test_alerts()

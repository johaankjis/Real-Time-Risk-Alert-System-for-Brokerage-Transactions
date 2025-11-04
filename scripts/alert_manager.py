"""
Alert Management System
Provides tools for acknowledging, filtering, and managing alerts
"""

from datetime import datetime
from typing import List, Dict, Optional
from database_config import get_db_connection


class AlertManager:
    """Manages alert lifecycle and operations"""
    
    def __init__(self):
        self.db = get_db_connection()
    
    def get_alerts(self, 
                   severity: Optional[str] = None,
                   entity_type: Optional[str] = None,
                   acknowledged: Optional[bool] = None,
                   limit: int = 100) -> List[Dict]:
        """Get alerts with optional filtering"""
        
        query = "SELECT * FROM alerts WHERE 1=1"
        params = []
        
        if severity:
            query += f" AND severity = {'?' if self.db.db_type == 'sqlite' else '%s'}"
            params.append(severity)
        
        if entity_type:
            query += f" AND entity_type = {'?' if self.db.db_type == 'sqlite' else '%s'}"
            params.append(entity_type)
        
        if acknowledged is not None:
            query += f" AND acknowledged = {'?' if self.db.db_type == 'sqlite' else '%s'}"
            params.append(acknowledged)
        
        query += f" ORDER BY timestamp DESC LIMIT {'?' if self.db.db_type == 'sqlite' else '%s'}"
        params.append(limit)
        
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(query, tuple(params))
                results = cursor.fetchall()
                
                if self.db.db_type == 'sqlite':
                    return [dict(row) for row in results]
                return results
        except Exception as e:
            print(f"Error fetching alerts: {e}")
            return []
    
    def acknowledge_alert(self, alert_id: int, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        try:
            with self.db.get_cursor() as cursor:
                if self.db.db_type == 'postgresql':
                    cursor.execute("""
                        UPDATE alerts 
                        SET acknowledged = TRUE,
                            acknowledged_at = %s,
                            acknowledged_by = %s
                        WHERE alert_id = %s
                    """, (datetime.now(), acknowledged_by, alert_id))
                else:
                    cursor.execute("""
                        UPDATE alerts 
                        SET acknowledged = 1,
                            acknowledged_at = ?,
                            acknowledged_by = ?
                        WHERE alert_id = ?
                    """, (datetime.now(), acknowledged_by, alert_id))
                
                return True
        except Exception as e:
            print(f"Error acknowledging alert: {e}")
            return False
    
    def acknowledge_multiple(self, alert_ids: List[int], acknowledged_by: str) -> int:
        """Acknowledge multiple alerts at once"""
        count = 0
        for alert_id in alert_ids:
            if self.acknowledge_alert(alert_id, acknowledged_by):
                count += 1
        return count
    
    def get_alert_summary(self) -> Dict:
        """Get summary statistics of alerts"""
        try:
            with self.db.get_cursor() as cursor:
                # Total alerts
                cursor.execute("SELECT COUNT(*) as count FROM alerts")
                total = cursor.fetchone()[0] if self.db.db_type == 'sqlite' else cursor.fetchone()['count']
                
                # Unacknowledged alerts
                cursor.execute("SELECT COUNT(*) as count FROM alerts WHERE acknowledged = FALSE")
                unacknowledged = cursor.fetchone()[0] if self.db.db_type == 'sqlite' else cursor.fetchone()['count']
                
                # By severity
                cursor.execute("""
                    SELECT severity, COUNT(*) as count 
                    FROM alerts 
                    WHERE acknowledged = FALSE
                    GROUP BY severity
                """)
                by_severity = {}
                for row in cursor.fetchall():
                    if self.db.db_type == 'sqlite':
                        by_severity[row[0]] = row[1]
                    else:
                        by_severity[row['severity']] = row['count']
                
                # By type
                cursor.execute("""
                    SELECT alert_type, COUNT(*) as count 
                    FROM alerts 
                    WHERE acknowledged = FALSE
                    GROUP BY alert_type
                """)
                by_type = {}
                for row in cursor.fetchall():
                    if self.db.db_type == 'sqlite':
                        by_type[row[0]] = row[1]
                    else:
                        by_type[row['alert_type']] = row['count']
                
                return {
                    'total': total,
                    'unacknowledged': unacknowledged,
                    'by_severity': by_severity,
                    'by_type': by_type
                }
        except Exception as e:
            print(f"Error getting alert summary: {e}")
            return {}
    
    def delete_old_alerts(self, days: int = 30) -> int:
        """Delete alerts older than specified days"""
        try:
            with self.db.get_cursor() as cursor:
                if self.db.db_type == 'postgresql':
                    cursor.execute("""
                        DELETE FROM alerts 
                        WHERE timestamp < NOW() - INTERVAL '%s days'
                        AND acknowledged = TRUE
                    """, (days,))
                else:
                    cursor.execute("""
                        DELETE FROM alerts 
                        WHERE timestamp < datetime('now', '-' || ? || ' days')
                        AND acknowledged = 1
                    """, (days,))
                
                return cursor.rowcount
        except Exception as e:
            print(f"Error deleting old alerts: {e}")
            return 0
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.close()


# CLI tool for alert management
if __name__ == "__main__":
    import sys
    
    manager = AlertManager()
    
    if len(sys.argv) < 2:
        print("Alert Manager CLI")
        print("\nUsage:")
        print("  python alert_manager.py summary              - Show alert summary")
        print("  python alert_manager.py list [severity]      - List alerts")
        print("  python alert_manager.py ack <id> <user>      - Acknowledge alert")
        print("  python alert_manager.py cleanup [days]       - Delete old alerts")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        if command == "summary":
            summary = manager.get_alert_summary()
            print("\n=== Alert Summary ===")
            print(f"Total Alerts: {summary.get('total', 0)}")
            print(f"Unacknowledged: {summary.get('unacknowledged', 0)}")
            print("\nBy Severity:")
            for severity, count in summary.get('by_severity', {}).items():
                print(f"  {severity}: {count}")
            print("\nBy Type:")
            for alert_type, count in summary.get('by_type', {}).items():
                print(f"  {alert_type}: {count}")
        
        elif command == "list":
            severity = sys.argv[2] if len(sys.argv) > 2 else None
            alerts = manager.get_alerts(severity=severity, acknowledged=False)
            
            print(f"\n=== Unacknowledged Alerts {f'({severity})' if severity else ''} ===")
            for alert in alerts:
                print(f"\nID: {alert['alert_id']}")
                print(f"Time: {alert['timestamp']}")
                print(f"Severity: {alert['severity']}")
                print(f"Type: {alert['alert_type']}")
                print(f"Message: {alert['message']}")
                print("-" * 60)
        
        elif command == "ack":
            if len(sys.argv) < 4:
                print("Usage: python alert_manager.py ack <alert_id> <user>")
                sys.exit(1)
            
            alert_id = int(sys.argv[2])
            user = sys.argv[3]
            
            if manager.acknowledge_alert(alert_id, user):
                print(f"Alert {alert_id} acknowledged by {user}")
            else:
                print(f"Failed to acknowledge alert {alert_id}")
        
        elif command == "cleanup":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            deleted = manager.delete_old_alerts(days)
            print(f"Deleted {deleted} old alerts (older than {days} days)")
        
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    
    finally:
        manager.close()

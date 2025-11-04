"""
Real-Time Risk Detection Engine
Monitors transactions and exposures, detects anomalies, and generates alerts
"""

import asyncio
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import numpy as np
from collections import defaultdict, deque
from dotenv import load_dotenv

from database_config import get_db_connection
from alert_system import AlertSystem

# Load environment variables
load_dotenv()

# Risk thresholds from environment
CLIENT_EXPOSURE_THRESHOLD = float(os.getenv('CLIENT_EXPOSURE_THRESHOLD', 1000000))
SYMBOL_EXPOSURE_THRESHOLD = float(os.getenv('SYMBOL_EXPOSURE_THRESHOLD', 500000))
TRANSACTION_VELOCITY_THRESHOLD = int(os.getenv('TRANSACTION_VELOCITY_THRESHOLD', 10))
ANOMALY_DETECTION_THRESHOLD = float(os.getenv('ANOMALY_DETECTION_THRESHOLD', 3.0))

# Monitoring configuration
MONITORING_INTERVAL = 5  # seconds
VELOCITY_WINDOW = 60  # seconds for velocity calculation
ANOMALY_WINDOW = 100  # number of transactions for anomaly detection


class RiskEngine:
    """Real-time risk detection and monitoring engine"""
    
    def __init__(self):
        self.db = None
        self.alert_system = AlertSystem()
        self.running = False
        
        # Transaction velocity tracking
        self.client_transactions = defaultdict(lambda: deque(maxlen=100))
        self.symbol_transactions = defaultdict(lambda: deque(maxlen=100))
        
        # Transaction value history for anomaly detection
        self.transaction_values = deque(maxlen=ANOMALY_WINDOW)
        
        # Last processed transaction ID
        self.last_transaction_id = 0
        
        # Statistics
        self.alerts_generated = 0
        self.transactions_processed = 0
    
    def calculate_risk_level(self, exposure: float, threshold: float) -> str:
        """Calculate risk level based on exposure and threshold"""
        ratio = exposure / threshold
        
        if ratio >= 1.0:
            return 'CRITICAL'
        elif ratio >= 0.75:
            return 'HIGH'
        elif ratio >= 0.5:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def check_client_exposure(self, client_id: str, exposure: float) -> Optional[Dict]:
        """Check if client exposure exceeds threshold"""
        risk_level = self.calculate_risk_level(exposure, CLIENT_EXPOSURE_THRESHOLD)
        
        if exposure > CLIENT_EXPOSURE_THRESHOLD:
            return {
                'alert_type': 'HIGH_CLIENT_EXPOSURE',
                'severity': 'CRITICAL' if exposure > CLIENT_EXPOSURE_THRESHOLD * 1.5 else 'HIGH',
                'entity_type': 'CLIENT',
                'entity_id': client_id,
                'message': f'Client {client_id} exposure ${exposure:,.2f} exceeds threshold ${CLIENT_EXPOSURE_THRESHOLD:,.2f}',
                'threshold_value': CLIENT_EXPOSURE_THRESHOLD,
                'current_value': exposure
            }
        
        # Update risk level in database
        self.update_client_risk_level(client_id, risk_level)
        return None
    
    def check_symbol_exposure(self, symbol: str, exposure: float) -> Optional[Dict]:
        """Check if symbol exposure exceeds threshold"""
        risk_level = self.calculate_risk_level(exposure, SYMBOL_EXPOSURE_THRESHOLD)
        
        if exposure > SYMBOL_EXPOSURE_THRESHOLD:
            return {
                'alert_type': 'HIGH_SYMBOL_EXPOSURE',
                'severity': 'CRITICAL' if exposure > SYMBOL_EXPOSURE_THRESHOLD * 1.5 else 'HIGH',
                'entity_type': 'SYMBOL',
                'entity_id': symbol,
                'message': f'Symbol {symbol} exposure ${exposure:,.2f} exceeds threshold ${SYMBOL_EXPOSURE_THRESHOLD:,.2f}',
                'threshold_value': SYMBOL_EXPOSURE_THRESHOLD,
                'current_value': exposure
            }
        
        # Update risk level in database
        self.update_symbol_risk_level(symbol, risk_level)
        return None
    
    def check_transaction_velocity(self, entity_type: str, entity_id: str, 
                                   transactions: deque) -> Optional[Dict]:
        """Check if transaction velocity exceeds threshold"""
        if len(transactions) < 2:
            return None
        
        # Count transactions in the last minute
        now = datetime.now()
        cutoff = now - timedelta(seconds=VELOCITY_WINDOW)
        recent_count = sum(1 for tx_time in transactions if tx_time > cutoff)
        
        if recent_count > TRANSACTION_VELOCITY_THRESHOLD:
            return {
                'alert_type': 'HIGH_TRANSACTION_VELOCITY',
                'severity': 'HIGH',
                'entity_type': entity_type,
                'entity_id': entity_id,
                'message': f'{entity_type} {entity_id} has {recent_count} transactions in last {VELOCITY_WINDOW}s (threshold: {TRANSACTION_VELOCITY_THRESHOLD})',
                'threshold_value': float(TRANSACTION_VELOCITY_THRESHOLD),
                'current_value': float(recent_count)
            }
        
        return None
    
    def detect_anomaly(self, transaction_value: float) -> Optional[Dict]:
        """Detect anomalous transactions using statistical analysis"""
        if len(self.transaction_values) < 30:  # Need minimum data
            return None
        
        # Calculate mean and standard deviation
        values = np.array(list(self.transaction_values))
        mean = np.mean(values)
        std = np.std(values)
        
        if std == 0:  # Avoid division by zero
            return None
        
        # Calculate z-score
        z_score = abs((transaction_value - mean) / std)
        
        if z_score > ANOMALY_DETECTION_THRESHOLD:
            return {
                'alert_type': 'ANOMALY_DETECTED',
                'severity': 'MEDIUM' if z_score < 4 else 'HIGH',
                'entity_type': 'SYSTEM',
                'entity_id': 'TRANSACTION_MONITOR',
                'message': f'Anomalous transaction value ${transaction_value:,.2f} detected (z-score: {z_score:.2f}, mean: ${mean:,.2f}, std: ${std:,.2f})',
                'threshold_value': mean + (ANOMALY_DETECTION_THRESHOLD * std),
                'current_value': transaction_value
            }
        
        return None
    
    def update_client_risk_level(self, client_id: str, risk_level: str):
        """Update client risk level in database"""
        try:
            with self.db.get_cursor() as cursor:
                if self.db.db_type == 'postgresql':
                    cursor.execute("""
                        UPDATE client_exposures 
                        SET risk_level = %s 
                        WHERE client_id = %s
                    """, (risk_level, client_id))
                else:
                    cursor.execute("""
                        UPDATE client_exposures 
                        SET risk_level = ? 
                        WHERE client_id = ?
                    """, (risk_level, client_id))
        except Exception as e:
            print(f"Error updating client risk level: {e}")
    
    def update_symbol_risk_level(self, symbol: str, risk_level: str):
        """Update symbol risk level in database"""
        try:
            with self.db.get_cursor() as cursor:
                if self.db.db_type == 'postgresql':
                    cursor.execute("""
                        UPDATE symbol_exposures 
                        SET risk_level = %s 
                        WHERE symbol = %s
                    """, (risk_level, symbol))
                else:
                    cursor.execute("""
                        UPDATE symbol_exposures 
                        SET risk_level = ? 
                        WHERE symbol = ?
                    """, (risk_level, symbol))
        except Exception as e:
            print(f"Error updating symbol risk level: {e}")
    
    def create_alert(self, alert_data: Dict):
        """Create alert in database and send notifications"""
        try:
            with self.db.get_cursor() as cursor:
                if self.db.db_type == 'postgresql':
                    cursor.execute("""
                        INSERT INTO alerts 
                        (timestamp, alert_type, severity, entity_type, entity_id, 
                         message, threshold_value, current_value)
                        VALUES (%(timestamp)s, %(alert_type)s, %(severity)s, %(entity_type)s,
                                %(entity_id)s, %(message)s, %(threshold_value)s, %(current_value)s)
                        RETURNING alert_id
                    """, {**alert_data, 'timestamp': datetime.now()})
                    result = cursor.fetchone()
                    alert_id = result['alert_id']
                else:
                    cursor.execute("""
                        INSERT INTO alerts 
                        (timestamp, alert_type, severity, entity_type, entity_id, 
                         message, threshold_value, current_value)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        datetime.now(),
                        alert_data['alert_type'],
                        alert_data['severity'],
                        alert_data['entity_type'],
                        alert_data['entity_id'],
                        alert_data['message'],
                        alert_data.get('threshold_value'),
                        alert_data.get('current_value')
                    ))
                    alert_id = cursor.lastrowid
            
            # Send alert notifications
            self.alert_system.send_alert(alert_data)
            self.alerts_generated += 1
            
            print(f"\n{'='*60}")
            print(f"🚨 ALERT #{alert_id} - {alert_data['severity']}")
            print(f"Type: {alert_data['alert_type']}")
            print(f"Message: {alert_data['message']}")
            print(f"{'='*60}\n")
            
            return alert_id
        
        except Exception as e:
            print(f"Error creating alert: {e}")
            return None
    
    def process_new_transactions(self):
        """Process new transactions and check for risks"""
        try:
            with self.db.get_cursor() as cursor:
                # Get new transactions
                if self.db.db_type == 'postgresql':
                    cursor.execute("""
                        SELECT * FROM transactions 
                        WHERE transaction_id > %s 
                        ORDER BY transaction_id
                    """, (self.last_transaction_id,))
                else:
                    cursor.execute("""
                        SELECT * FROM transactions 
                        WHERE transaction_id > ? 
                        ORDER BY transaction_id
                    """, (self.last_transaction_id,))
                
                transactions = cursor.fetchall()
                
                for tx in transactions:
                    # Convert to dict if needed
                    if self.db.db_type == 'sqlite':
                        tx = dict(tx)
                    
                    # Update tracking
                    self.client_transactions[tx['client_id']].append(datetime.now())
                    self.symbol_transactions[tx['symbol']].append(datetime.now())
                    self.transaction_values.append(float(tx['total_value']))
                    
                    # Check for anomalies
                    anomaly_alert = self.detect_anomaly(float(tx['total_value']))
                    if anomaly_alert:
                        self.create_alert(anomaly_alert)
                    
                    # Check transaction velocity
                    client_velocity_alert = self.check_transaction_velocity(
                        'CLIENT', tx['client_id'], 
                        self.client_transactions[tx['client_id']]
                    )
                    if client_velocity_alert:
                        self.create_alert(client_velocity_alert)
                    
                    symbol_velocity_alert = self.check_transaction_velocity(
                        'SYMBOL', tx['symbol'],
                        self.symbol_transactions[tx['symbol']]
                    )
                    if symbol_velocity_alert:
                        self.create_alert(symbol_velocity_alert)
                    
                    self.transactions_processed += 1
                    self.last_transaction_id = tx['transaction_id']
        
        except Exception as e:
            print(f"Error processing transactions: {e}")
    
    def check_exposures(self):
        """Check all client and symbol exposures"""
        try:
            with self.db.get_cursor() as cursor:
                # Check client exposures
                cursor.execute("SELECT client_id, total_exposure FROM client_exposures")
                for row in cursor.fetchall():
                    if self.db.db_type == 'sqlite':
                        row = dict(row)
                    
                    alert = self.check_client_exposure(row['client_id'], float(row['total_exposure']))
                    if alert:
                        self.create_alert(alert)
                
                # Check symbol exposures
                cursor.execute("SELECT symbol, total_exposure FROM symbol_exposures")
                for row in cursor.fetchall():
                    if self.db.db_type == 'sqlite':
                        row = dict(row)
                    
                    alert = self.check_symbol_exposure(row['symbol'], float(row['total_exposure']))
                    if alert:
                        self.create_alert(alert)
        
        except Exception as e:
            print(f"Error checking exposures: {e}")
    
    def update_risk_metrics(self):
        """Update aggregated risk metrics"""
        try:
            with self.db.get_cursor() as cursor:
                # Get current metrics
                cursor.execute("SELECT COUNT(*) as count FROM transactions")
                total_transactions = cursor.fetchone()[0] if self.db.db_type == 'sqlite' else cursor.fetchone()['count']
                
                cursor.execute("SELECT SUM(total_exposure) as total FROM client_exposures")
                result = cursor.fetchone()
                total_exposure = float(result[0] if self.db.db_type == 'sqlite' else result['total']) if result else 0
                
                cursor.execute("SELECT COUNT(DISTINCT client_id) as count FROM client_exposures WHERE total_exposure > 0")
                active_clients = cursor.fetchone()[0] if self.db.db_type == 'sqlite' else cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(DISTINCT symbol) as count FROM symbol_exposures WHERE total_exposure > 0")
                active_symbols = cursor.fetchone()[0] if self.db.db_type == 'sqlite' else cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM client_exposures WHERE risk_level IN ('HIGH', 'CRITICAL')")
                high_risk_clients = cursor.fetchone()[0] if self.db.db_type == 'sqlite' else cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM symbol_exposures WHERE risk_level IN ('HIGH', 'CRITICAL')")
                high_risk_symbols = cursor.fetchone()[0] if self.db.db_type == 'sqlite' else cursor.fetchone()['count']
                
                # Insert metrics
                if self.db.db_type == 'postgresql':
                    cursor.execute("""
                        INSERT INTO risk_metrics 
                        (timestamp, total_transactions, total_exposure, active_clients, 
                         active_symbols, high_risk_clients, high_risk_symbols, alerts_generated)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (datetime.now(), total_transactions, total_exposure, active_clients,
                          active_symbols, high_risk_clients, high_risk_symbols, self.alerts_generated))
                else:
                    cursor.execute("""
                        INSERT INTO risk_metrics 
                        (timestamp, total_transactions, total_exposure, active_clients, 
                         active_symbols, high_risk_clients, high_risk_symbols, alerts_generated)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (datetime.now(), total_transactions, total_exposure, active_clients,
                          active_symbols, high_risk_clients, high_risk_symbols, self.alerts_generated))
        
        except Exception as e:
            print(f"Error updating risk metrics: {e}")
    
    async def monitor_loop(self):
        """Main monitoring loop"""
        print("Starting risk monitoring engine...")
        print(f"Thresholds: Client=${CLIENT_EXPOSURE_THRESHOLD:,.0f}, "
              f"Symbol=${SYMBOL_EXPOSURE_THRESHOLD:,.0f}, "
              f"Velocity={TRANSACTION_VELOCITY_THRESHOLD} tx/min")
        print(f"Monitoring interval: {MONITORING_INTERVAL}s")
        print("-" * 60)
        
        self.running = True
        iteration = 0
        
        while self.running:
            try:
                iteration += 1
                
                # Process new transactions
                self.process_new_transactions()
                
                # Check exposures every iteration
                self.check_exposures()
                
                # Update metrics every 10 iterations
                if iteration % 10 == 0:
                    self.update_risk_metrics()
                    print(f"\n--- Monitoring Stats: {self.transactions_processed} transactions processed, "
                          f"{self.alerts_generated} alerts generated ---\n")
                
                # Wait for next iteration
                await asyncio.sleep(MONITORING_INTERVAL)
            
            except KeyboardInterrupt:
                print("\nStopping risk engine...")
                self.running = False
                break
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                await asyncio.sleep(MONITORING_INTERVAL)
    
    async def run(self):
        """Start the risk engine"""
        try:
            # Connect to database
            self.db = get_db_connection()
            print("Connected to database")
            
            # Run monitoring loop
            await self.monitor_loop()
        
        except Exception as e:
            print(f"Fatal error: {e}")
        finally:
            if self.db:
                self.db.close()
                print("Database connection closed")


async def main():
    """Main entry point"""
    engine = RiskEngine()
    await engine.run()


if __name__ == "__main__":
    asyncio.run(main())

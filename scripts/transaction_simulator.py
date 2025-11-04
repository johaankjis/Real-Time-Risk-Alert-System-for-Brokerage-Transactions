"""
Transaction Data Simulator
Generates realistic brokerage transactions for testing the risk alert system
"""

import asyncio
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict
import os
from dotenv import load_dotenv

from database_config import get_db_connection

# Load environment variables
load_dotenv()

# Simulation configuration
SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'BAC', 'WMT']
CLIENTS = [f'CLIENT_{str(i).zfill(3)}' for i in range(1, 21)]  # 20 clients
BROKERS = ['BROKER_A', 'BROKER_B', 'BROKER_C']
MARKETS = ['NYSE', 'NASDAQ', 'AMEX']

# Price ranges for symbols (realistic ranges)
SYMBOL_PRICES = {
    'AAPL': (150, 200),
    'GOOGL': (120, 160),
    'MSFT': (350, 420),
    'AMZN': (140, 180),
    'TSLA': (200, 300),
    'META': (300, 400),
    'NVDA': (400, 600),
    'JPM': (140, 170),
    'BAC': (30, 40),
    'WMT': (150, 170)
}

# Transaction generation rates
NORMAL_TPS = 2  # Transactions per second (normal)
SPIKE_TPS = 10  # Transactions per second (spike)
SPIKE_PROBABILITY = 0.05  # 5% chance of spike
ANOMALY_PROBABILITY = 0.02  # 2% chance of anomalous transaction


class TransactionSimulator:
    """Simulates realistic brokerage transactions"""
    
    def __init__(self):
        self.db = None
        self.running = False
        self.transaction_count = 0
        self.start_time = None
    
    def generate_transaction(self, anomaly: bool = False) -> Dict:
        """Generate a single transaction"""
        client_id = random.choice(CLIENTS)
        symbol = random.choice(SYMBOLS)
        transaction_type = random.choice(['BUY', 'SELL'])
        
        # Get price range for symbol
        min_price, max_price = SYMBOL_PRICES[symbol]
        price = round(random.uniform(min_price, max_price), 2)
        
        # Normal quantity: 10-1000 shares
        # Anomaly: 5000-10000 shares (unusually large)
        if anomaly:
            quantity = random.randint(5000, 10000)
        else:
            quantity = random.randint(10, 1000)
        
        total_value = round(price * quantity, 2)
        
        return {
            'client_id': client_id,
            'symbol': symbol,
            'transaction_type': transaction_type,
            'quantity': quantity,
            'price': price,
            'total_value': total_value,
            'broker_id': random.choice(BROKERS),
            'market': random.choice(MARKETS),
            'timestamp': datetime.now()
        }
    
    def insert_transaction(self, transaction: Dict):
        """Insert transaction into database"""
        try:
            with self.db.get_cursor() as cursor:
                if self.db.db_type == 'postgresql':
                    cursor.execute("""
                        INSERT INTO transactions 
                        (timestamp, client_id, symbol, transaction_type, quantity, 
                         price, total_value, broker_id, market)
                        VALUES (%(timestamp)s, %(client_id)s, %(symbol)s, %(transaction_type)s,
                                %(quantity)s, %(price)s, %(total_value)s, %(broker_id)s, %(market)s)
                        RETURNING transaction_id
                    """, transaction)
                    result = cursor.fetchone()
                    return result['transaction_id']
                else:  # sqlite
                    cursor.execute("""
                        INSERT INTO transactions 
                        (timestamp, client_id, symbol, transaction_type, quantity, 
                         price, total_value, broker_id, market)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        transaction['timestamp'],
                        transaction['client_id'],
                        transaction['symbol'],
                        transaction['transaction_type'],
                        transaction['quantity'],
                        transaction['price'],
                        transaction['total_value'],
                        transaction['broker_id'],
                        transaction['market']
                    ))
                    return cursor.lastrowid
        except Exception as e:
            print(f"Error inserting transaction: {e}")
            return None
    
    def update_exposures(self, transaction: Dict):
        """Update client and symbol exposures"""
        try:
            with self.db.get_cursor() as cursor:
                # Update client exposure
                if self.db.db_type == 'postgresql':
                    cursor.execute("""
                        INSERT INTO client_exposures (client_id, total_exposure, position_count, last_updated)
                        VALUES (%(client_id)s, %(total_value)s, 1, %(timestamp)s)
                        ON CONFLICT (client_id) 
                        DO UPDATE SET 
                            total_exposure = client_exposures.total_exposure + %(total_value)s,
                            position_count = client_exposures.position_count + 1,
                            last_updated = %(timestamp)s
                    """, transaction)
                    
                    # Update symbol exposure
                    cursor.execute("""
                        INSERT INTO symbol_exposures (symbol, total_exposure, transaction_count, last_updated)
                        VALUES (%(symbol)s, %(total_value)s, 1, %(timestamp)s)
                        ON CONFLICT (symbol)
                        DO UPDATE SET
                            total_exposure = symbol_exposures.total_exposure + %(total_value)s,
                            transaction_count = symbol_exposures.transaction_count + 1,
                            last_updated = %(timestamp)s
                    """, transaction)
                else:  # sqlite
                    # Check if client exposure exists
                    cursor.execute(
                        "SELECT total_exposure, position_count FROM client_exposures WHERE client_id = ?",
                        (transaction['client_id'],)
                    )
                    result = cursor.fetchone()
                    
                    if result:
                        cursor.execute("""
                            UPDATE client_exposures 
                            SET total_exposure = total_exposure + ?,
                                position_count = position_count + 1,
                                last_updated = ?
                            WHERE client_id = ?
                        """, (transaction['total_value'], transaction['timestamp'], transaction['client_id']))
                    else:
                        cursor.execute("""
                            INSERT INTO client_exposures (client_id, total_exposure, position_count, last_updated)
                            VALUES (?, ?, 1, ?)
                        """, (transaction['client_id'], transaction['total_value'], transaction['timestamp']))
                    
                    # Check if symbol exposure exists
                    cursor.execute(
                        "SELECT total_exposure, transaction_count FROM symbol_exposures WHERE symbol = ?",
                        (transaction['symbol'],)
                    )
                    result = cursor.fetchone()
                    
                    if result:
                        cursor.execute("""
                            UPDATE symbol_exposures
                            SET total_exposure = total_exposure + ?,
                                transaction_count = transaction_count + 1,
                                last_updated = ?
                            WHERE symbol = ?
                        """, (transaction['total_value'], transaction['timestamp'], transaction['symbol']))
                    else:
                        cursor.execute("""
                            INSERT INTO symbol_exposures (symbol, total_exposure, transaction_count, last_updated)
                            VALUES (?, ?, 1, ?)
                        """, (transaction['symbol'], transaction['total_value'], transaction['timestamp']))
        
        except Exception as e:
            print(f"Error updating exposures: {e}")
    
    async def simulate_transactions(self):
        """Main simulation loop"""
        print("Starting transaction simulator...")
        print(f"Normal rate: {NORMAL_TPS} TPS, Spike rate: {SPIKE_TPS} TPS")
        print(f"Symbols: {len(SYMBOLS)}, Clients: {len(CLIENTS)}")
        print("-" * 60)
        
        self.running = True
        self.start_time = time.time()
        
        while self.running:
            try:
                # Determine if this is a spike period
                is_spike = random.random() < SPIKE_PROBABILITY
                tps = SPIKE_TPS if is_spike else NORMAL_TPS
                
                # Generate transactions for this second
                for _ in range(tps):
                    # Determine if this is an anomalous transaction
                    is_anomaly = random.random() < ANOMALY_PROBABILITY
                    
                    # Generate and insert transaction
                    transaction = self.generate_transaction(anomaly=is_anomaly)
                    transaction_id = self.insert_transaction(transaction)
                    
                    if transaction_id:
                        # Update exposures
                        self.update_exposures(transaction)
                        
                        self.transaction_count += 1
                        
                        # Log transaction
                        status = "ANOMALY" if is_anomaly else "SPIKE" if is_spike else "NORMAL"
                        print(f"[{status}] TX#{transaction_id}: {transaction['client_id']} "
                              f"{transaction['transaction_type']} {transaction['quantity']} "
                              f"{transaction['symbol']} @ ${transaction['price']} "
                              f"= ${transaction['total_value']:,.2f}")
                
                # Wait for next second
                await asyncio.sleep(1)
                
                # Print statistics every 10 seconds
                if self.transaction_count % (NORMAL_TPS * 10) == 0:
                    elapsed = time.time() - self.start_time
                    avg_tps = self.transaction_count / elapsed if elapsed > 0 else 0
                    print(f"\n--- Stats: {self.transaction_count} transactions, "
                          f"Avg TPS: {avg_tps:.2f}, Runtime: {elapsed:.0f}s ---\n")
            
            except KeyboardInterrupt:
                print("\nStopping simulator...")
                self.running = False
                break
            except Exception as e:
                print(f"Error in simulation loop: {e}")
                await asyncio.sleep(1)
    
    async def run(self):
        """Start the simulator"""
        try:
            # Connect to database
            self.db = get_db_connection()
            print("Connected to database")
            
            # Run simulation
            await self.simulate_transactions()
        
        except Exception as e:
            print(f"Fatal error: {e}")
        finally:
            if self.db:
                self.db.close()
                print("Database connection closed")


async def main():
    """Main entry point"""
    simulator = TransactionSimulator()
    await simulator.run()


if __name__ == "__main__":
    # Run the simulator
    asyncio.run(main())

"""
Convenience script to run all components of the Risk Alert System
Starts the simulator, risk engine, and dashboard in separate processes
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def run_component(script_name, name):
    """Run a Python script as a subprocess"""
    print(f"Starting {name}...")
    
    # Get the scripts directory
    scripts_dir = Path(__file__).parent
    script_path = scripts_dir / script_name
    
    # Start the process
    process = subprocess.Popen(
        [sys.executable, str(script_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    return process


def main():
    """Main function to orchestrate all components"""
    print("=" * 60)
    print("Real-Time Risk Alert System")
    print("=" * 60)
    print()
    
    # Check if database is initialized
    db_type = os.getenv('DB_TYPE', 'sqlite')
    if db_type == 'sqlite':
        db_path = os.getenv('SQLITE_DB_PATH', 'risk_alert_system.db')
        if not os.path.exists(db_path):
            print("Initializing SQLite database...")
            subprocess.run([sys.executable, 'scripts/database_config.py'])
            time.sleep(2)
    
    processes = []
    
    try:
        # Start Risk Engine
        risk_engine = run_component('risk_engine.py', 'Risk Engine')
        processes.append(('Risk Engine', risk_engine))
        time.sleep(2)
        
        # Start Transaction Simulator
        simulator = run_component('transaction_simulator.py', 'Transaction Simulator')
        processes.append(('Transaction Simulator', simulator))
        time.sleep(2)
        
        # Start Streamlit Dashboard
        print("Starting Streamlit Dashboard...")
        dashboard = subprocess.Popen(
            [sys.executable, '-m', 'streamlit', 'run', 'scripts/streamlit_dashboard.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        processes.append(('Streamlit Dashboard', dashboard))
        
        print()
        print("=" * 60)
        print("All components started successfully!")
        print("=" * 60)
        print()
        print("Access the dashboard at: http://localhost:8501")
        print()
        print("Press Ctrl+C to stop all components")
        print()
        
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
            # Check if any process has died
            for name, process in processes:
                if process.poll() is not None:
                    print(f"\n{name} has stopped unexpectedly!")
                    raise KeyboardInterrupt
    
    except KeyboardInterrupt:
        print("\n\nStopping all components...")
        
        # Terminate all processes
        for name, process in processes:
            print(f"Stopping {name}...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        
        print("\nAll components stopped.")
        print("Goodbye!")


if __name__ == "__main__":
    main()

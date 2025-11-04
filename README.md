# Real-Time Risk Alert System for Brokerage Transactions

A comprehensive risk monitoring and alerting system for brokerage transactions with real-time detection, interactive dashboards, and automated alerts.

## Features

- **Real-time Risk Monitoring**: Continuous monitoring of client and symbol exposures
- **Anomaly Detection**: Statistical analysis to detect unusual trading patterns
- **Interactive Dashboards**: Streamlit-based visualization with Plotly charts
- **Automated Alerts**: Slack and email notifications for risk events
- **Transaction Simulation**: Built-in simulator for testing and demonstration

## Architecture

\`\`\`
risk-alert-system/
├── scripts/
│   ├── 01_create_schema.sql       # Database schema
│   ├── 02_seed_initial_data.sql   # Initial data
│   ├── database_config.py         # Database connection management
│   ├── transaction_simulator.py   # Transaction data generator
│   ├── risk_engine.py             # Risk detection engine
│   ├── alert_system.py            # Alert management
│   └── streamlit_dashboard.py     # Interactive dashboard
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
└── README.md                      # This file
\`\`\`

## Setup Instructions

### 1. Install Dependencies

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 2. Configure Environment

Copy `.env.example` to `.env` and configure your settings:

\`\`\`bash
cp .env.example .env
\`\`\`

Edit `.env` with your database and alert configurations.

### 3. Initialize Database

**For SQLite (default, easiest for testing):**
\`\`\`bash
python scripts/database_config.py
\`\`\`

**For PostgreSQL:**
\`\`\`bash
# Create database
createdb risk_alert_system

# Run schema scripts
psql -U postgres -d risk_alert_system -f scripts/01_create_schema.sql
psql -U postgres -d risk_alert_system -f scripts/02_seed_initial_data.sql
\`\`\`

### 4. Run the System

**Start the Risk Engine (in one terminal):**
\`\`\`bash
python scripts/risk_engine.py
\`\`\`

**Start the Transaction Simulator (in another terminal):**
\`\`\`bash
python scripts/transaction_simulator.py
\`\`\`

**Launch the Dashboard (in a third terminal):**
\`\`\`bash
streamlit run scripts/streamlit_dashboard.py
\`\`\`

Access the dashboard at: http://localhost:8501

## Risk Detection Rules

1. **Client Exposure Threshold**: Alert when client exposure exceeds $1M
2. **Symbol Exposure Threshold**: Alert when symbol exposure exceeds $500K
3. **Transaction Velocity**: Alert when >10 transactions in 1 minute
4. **Anomaly Detection**: Statistical outlier detection using z-scores (>3σ)

## Database Schema

- **transactions**: All brokerage transactions
- **client_exposures**: Real-time client exposure tracking
- **symbol_exposures**: Real-time symbol exposure tracking
- **alerts**: Generated risk alerts
- **risk_metrics**: Aggregated system metrics

## Alert Types

- **HIGH_CLIENT_EXPOSURE**: Client exceeds exposure limit
- **HIGH_SYMBOL_EXPOSURE**: Symbol exceeds concentration limit
- **HIGH_TRANSACTION_VELOCITY**: Unusual transaction frequency
- **ANOMALY_DETECTED**: Statistical anomaly in transaction patterns

## Technology Stack

- **Backend**: Python 3.9+ with asyncio
- **Database**: PostgreSQL or SQLite
- **Dashboard**: Streamlit + Plotly
- **Alerts**: Slack SDK, SMTP email
- **Data Processing**: Pandas, NumPy

## Next Steps

After setup, the system will:
1. Generate simulated transactions continuously
2. Monitor exposures in real-time
3. Detect and alert on risk events
4. Display live metrics in the dashboard

## Troubleshooting

- **Database connection errors**: Check your `.env` configuration
- **Port conflicts**: Change `STREAMLIT_SERVER_PORT` in `.env`
- **Alert failures**: Verify Slack webhook URL and SMTP credentials

# Real-Time Risk Alert System for Brokerage Transactions

A comprehensive risk monitoring and alerting system for brokerage transactions with real-time detection, interactive dashboards, and automated alerts.

## Quick Start

For the fastest way to get started, see [QUICKSTART.md](QUICKSTART.md) which provides a 3-step guide to run the system in minutes.

For production deployment options, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Features

- **Real-time Risk Monitoring**: Continuous monitoring of client and symbol exposures
- **Anomaly Detection**: Statistical analysis to detect unusual trading patterns
- **Interactive Dashboards**: Streamlit-based visualization with Plotly charts
- **Automated Alerts**: Slack and email notifications for risk events
- **Transaction Simulation**: Built-in simulator for testing and demonstration

## Architecture

```
risk-alert-system/
├── scripts/
│   ├── 01_create_schema.sql       # Database schema
│   ├── 02_seed_initial_data.sql   # Initial data
│   ├── database_config.py         # Database connection management
│   ├── transaction_simulator.py   # Transaction data generator
│   ├── risk_engine.py             # Risk detection engine
│   ├── alert_system.py            # Alert management (legacy)
│   ├── alert_manager.py           # Alert manager (main alert handler)
│   ├── streamlit_dashboard.py     # Interactive dashboard
│   ├── run_all.py                 # Runs all components together
│   └── test_alert_system.py       # Alert system tests
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker container definition
├── docker-compose.yml             # Docker Compose configuration
├── QUICKSTART.md                  # Quick start guide
├── DEPLOYMENT.md                  # Deployment guide
└── README.md                      # This file
```

**Note**: The `package.json` file in the root directory is not used by this Python-based system and can be ignored.

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)

The system works out-of-the-box with SQLite and default settings. For custom configuration:

```bash
# Create a .env file with your settings
cat > .env << EOF
# Database Configuration
DB_TYPE=sqlite  # or postgresql
SQLITE_DB_PATH=risk_alert_system.db

# Risk Thresholds
CLIENT_EXPOSURE_THRESHOLD=1000000
SYMBOL_EXPOSURE_THRESHOLD=500000
TRANSACTION_VELOCITY_THRESHOLD=10
ANOMALY_DETECTION_THRESHOLD=3.0

# Alert Configuration (optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
ALERT_EMAIL_FROM=alerts@yourdomain.com
ALERT_EMAIL_TO=risk-team@yourdomain.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
EOF
```

See `DEPLOYMENT.md` for detailed configuration options.

### 3. Initialize Database

**For SQLite (default, easiest for testing):**
```bash
python scripts/database_config.py
```

**For PostgreSQL:**
```bash
# Create database
createdb risk_alert_system

# Run schema scripts
psql -U postgres -d risk_alert_system -f scripts/01_create_schema.sql
psql -U postgres -d risk_alert_system -f scripts/02_seed_initial_data.sql
```

### 4. Run the System

**Option A: Run All Components Together (Recommended)**

```bash
python scripts/run_all.py
```

This single command starts all three components:
- Risk monitoring engine
- Transaction simulator
- Interactive dashboard at http://localhost:8501

Press `Ctrl+C` to stop all components.

**Option B: Run Components Separately**

If you need more control, run each component in a separate terminal:

**Terminal 1 - Start the Risk Engine:**
```bash
python scripts/risk_engine.py
```

**Terminal 2 - Start the Transaction Simulator:**
```bash
python scripts/transaction_simulator.py
```

**Terminal 3 - Launch the Dashboard:**
```bash
streamlit run scripts/streamlit_dashboard.py
```

Access the dashboard at: http://localhost:8501

## Docker Deployment

You can also run the system using Docker:

```bash
# Build and start all services (includes PostgreSQL)
docker-compose up -d

# Access the dashboard at http://localhost:8501

# View logs
docker-compose logs -f risk-system

# Stop services
docker-compose down
```

For more deployment options, see [DEPLOYMENT.md](DEPLOYMENT.md).

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

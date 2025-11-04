# Quick Start Guide

Get the Risk Alert System running in 3 simple steps!

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

## Step 1: Install Dependencies

\`\`\`bash
pip install -r requirements.txt
\`\`\`

## Step 2: Configure Environment (Optional)

The system works out-of-the-box with SQLite. For custom configuration:

\`\`\`bash
cp .env.example .env
# Edit .env with your preferred settings
\`\`\`

## Step 3: Run the System

### Option A: Run All Components Together (Recommended)

\`\`\`bash
python scripts/run_all.py
\`\`\`

This starts:
- Risk monitoring engine
- Transaction simulator
- Interactive dashboard at http://localhost:8501

### Option B: Run Components Separately

**Terminal 1 - Risk Engine:**
\`\`\`bash
python scripts/risk_engine.py
\`\`\`

**Terminal 2 - Transaction Simulator:**
\`\`\`bash
python scripts/transaction_simulator.py
\`\`\`

**Terminal 3 - Dashboard:**
\`\`\`bash
streamlit run scripts/streamlit_dashboard.py
\`\`\`

## What You'll See

1. **Transaction Simulator**: Generates realistic trades (2-10 per second)
2. **Risk Engine**: Monitors exposures and detects anomalies
3. **Dashboard**: Real-time visualization at http://localhost:8501

## Default Thresholds

- Client Exposure: $1,000,000
- Symbol Exposure: $500,000
- Transaction Velocity: 10 transactions/minute
- Anomaly Detection: 3 standard deviations

## Stopping the System

Press `Ctrl+C` in the terminal to stop all components.

## Troubleshooting

**Port 8501 already in use?**
\`\`\`bash
# Change port in .env
STREAMLIT_SERVER_PORT=8502
\`\`\`

**Database errors?**
\`\`\`bash
# Reinitialize database
rm risk_alert_system.db
python scripts/database_config.py
\`\`\`

## Next Steps

- Adjust thresholds in `.env` file
- Configure Slack/Email alerts
- Switch to PostgreSQL for production use

For detailed documentation, see README.md

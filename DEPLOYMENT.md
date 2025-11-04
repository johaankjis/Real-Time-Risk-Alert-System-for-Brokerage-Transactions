# Deployment Guide

This guide covers deploying the Risk Alert System in various environments.

## Docker Deployment

### Quick Start with Docker Compose

1. **Build and start all services:**
   \`\`\`bash
   docker-compose up -d
   \`\`\`

2. **Access the dashboard:**
   Open http://localhost:8501

3. **View logs:**
   \`\`\`bash
   docker-compose logs -f risk-system
   \`\`\`

4. **Stop services:**
   \`\`\`bash
   docker-compose down
   \`\`\`

### Using SQLite (Simpler)

Edit `docker-compose.yml` to use SQLite:

\`\`\`yaml
services:
  risk-system:
    build: .
    environment:
      DB_TYPE: sqlite
      SQLITE_DB_PATH: /app/data/risk_alert_system.db
    ports:
      - "8501:8501"
    volumes:
      - ./scripts:/app/scripts
      - risk_data:/app/data
\`\`\`

Then run:
\`\`\`bash
docker-compose up -d risk-system
\`\`\`

## Production Deployment

### Environment Variables

Create a `.env` file with production settings:

\`\`\`env
# Database
DB_TYPE=postgresql
DB_HOST=your-db-host.com
DB_PORT=5432
DB_NAME=risk_alert_system
DB_USER=your_user
DB_PASSWORD=your_secure_password

# Risk Thresholds
CLIENT_EXPOSURE_THRESHOLD=1000000
SYMBOL_EXPOSURE_THRESHOLD=500000
TRANSACTION_VELOCITY_THRESHOLD=10
ANOMALY_DETECTION_THRESHOLD=3.0

# Slack Alerts
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Email Alerts
ALERT_EMAIL_FROM=alerts@yourdomain.com
ALERT_EMAIL_TO=risk-team@yourdomain.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Streamlit
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
\`\`\`

### PostgreSQL Setup

1. **Create database:**
   \`\`\`bash
   createdb risk_alert_system
   \`\`\`

2. **Run schema scripts:**
   \`\`\`bash
   psql -U postgres -d risk_alert_system -f scripts/01_create_schema.sql
   psql -U postgres -d risk_alert_system -f scripts/02_seed_initial_data.sql
   \`\`\`

### Running as System Services

#### Using systemd (Linux)

Create service files:

**risk-engine.service:**
\`\`\`ini
[Unit]
Description=Risk Alert Engine
After=network.target postgresql.service

[Service]
Type=simple
User=risk-system
WorkingDirectory=/opt/risk-alert-system
Environment="PATH=/opt/risk-alert-system/venv/bin"
ExecStart=/opt/risk-alert-system/venv/bin/python scripts/risk_engine.py
Restart=always

[Install]
WantedBy=multi-user.target
\`\`\`

**transaction-simulator.service:**
\`\`\`ini
[Unit]
Description=Transaction Simulator
After=network.target postgresql.service

[Service]
Type=simple
User=risk-system
WorkingDirectory=/opt/risk-alert-system
Environment="PATH=/opt/risk-alert-system/venv/bin"
ExecStart=/opt/risk-alert-system/venv/bin/python scripts/transaction_simulator.py
Restart=always

[Install]
WantedBy=multi-user.target
\`\`\`

**streamlit-dashboard.service:**
\`\`\`ini
[Unit]
Description=Risk Alert Dashboard
After=network.target postgresql.service

[Service]
Type=simple
User=risk-system
WorkingDirectory=/opt/risk-alert-system
Environment="PATH=/opt/risk-alert-system/venv/bin"
ExecStart=/opt/risk-alert-system/venv/bin/streamlit run scripts/streamlit_dashboard.py
Restart=always

[Install]
WantedBy=multi-user.target
\`\`\`

Enable and start services:
\`\`\`bash
sudo systemctl enable risk-engine transaction-simulator streamlit-dashboard
sudo systemctl start risk-engine transaction-simulator streamlit-dashboard
\`\`\`

## Cloud Deployment

### AWS Deployment

1. **RDS for PostgreSQL**
2. **EC2 or ECS for application**
3. **CloudWatch for monitoring**
4. **SNS for alerts**

### Azure Deployment

1. **Azure Database for PostgreSQL**
2. **Azure Container Instances**
3. **Azure Monitor**
4. **Logic Apps for alerts**

### GCP Deployment

1. **Cloud SQL for PostgreSQL**
2. **Cloud Run or GKE**
3. **Cloud Monitoring**
4. **Pub/Sub for alerts**

## Monitoring

### Health Checks

- Database connectivity
- Transaction processing rate
- Alert delivery status
- Dashboard availability

### Metrics to Monitor

- Transactions per second
- Alert generation rate
- Database query performance
- System resource usage

## Security Considerations

1. **Database Security:**
   - Use strong passwords
   - Enable SSL/TLS connections
   - Restrict network access

2. **Application Security:**
   - Keep dependencies updated
   - Use environment variables for secrets
   - Implement authentication for dashboard

3. **Alert Security:**
   - Secure webhook URLs
   - Use app passwords for email
   - Encrypt sensitive data

## Backup and Recovery

### Database Backups

\`\`\`bash
# PostgreSQL backup
pg_dump -U postgres risk_alert_system > backup.sql

# SQLite backup
cp risk_alert_system.db backup.db
\`\`\`

### Restore

\`\`\`bash
# PostgreSQL restore
psql -U postgres -d risk_alert_system < backup.sql

# SQLite restore
cp backup.db risk_alert_system.db
\`\`\`

## Scaling

### Horizontal Scaling

- Run multiple risk engine instances
- Use message queue for coordination
- Load balance dashboard instances

### Vertical Scaling

- Increase database resources
- Optimize queries with indexes
- Cache frequently accessed data

## Troubleshooting

See README.md for common issues and solutions.
\`\`\`

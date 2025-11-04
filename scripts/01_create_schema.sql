-- Real-Time Risk Alert System Database Schema
-- Creates tables for transactions, exposures, alerts, and risk metrics

-- Transactions table: stores all brokerage transactions
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    client_id VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('BUY', 'SELL')),
    quantity INTEGER NOT NULL,
    price DECIMAL(15, 2) NOT NULL,
    total_value DECIMAL(15, 2) NOT NULL,
    broker_id VARCHAR(50) NOT NULL,
    market VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Client exposures table: tracks real-time exposure per client
CREATE TABLE IF NOT EXISTS client_exposures (
    exposure_id SERIAL PRIMARY KEY,
    client_id VARCHAR(50) NOT NULL UNIQUE,
    total_exposure DECIMAL(15, 2) NOT NULL DEFAULT 0,
    position_count INTEGER NOT NULL DEFAULT 0,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    risk_level VARCHAR(20) DEFAULT 'LOW' CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'))
);

-- Symbol exposures table: tracks exposure per trading symbol
CREATE TABLE IF NOT EXISTS symbol_exposures (
    exposure_id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    total_exposure DECIMAL(15, 2) NOT NULL DEFAULT 0,
    transaction_count INTEGER NOT NULL DEFAULT 0,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    risk_level VARCHAR(20) DEFAULT 'LOW' CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'))
);

-- Alerts table: stores all risk alerts generated
CREATE TABLE IF NOT EXISTS alerts (
    alert_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    entity_type VARCHAR(20) NOT NULL CHECK (entity_type IN ('CLIENT', 'SYMBOL', 'SYSTEM')),
    entity_id VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    threshold_value DECIMAL(15, 2),
    current_value DECIMAL(15, 2),
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at TIMESTAMP,
    acknowledged_by VARCHAR(100)
);

-- Risk metrics table: stores aggregated risk metrics over time
CREATE TABLE IF NOT EXISTS risk_metrics (
    metric_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_transactions INTEGER NOT NULL DEFAULT 0,
    total_exposure DECIMAL(15, 2) NOT NULL DEFAULT 0,
    active_clients INTEGER NOT NULL DEFAULT 0,
    active_symbols INTEGER NOT NULL DEFAULT 0,
    high_risk_clients INTEGER NOT NULL DEFAULT 0,
    high_risk_symbols INTEGER NOT NULL DEFAULT 0,
    alerts_generated INTEGER NOT NULL DEFAULT 0
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_client ON transactions(client_id);
CREATE INDEX IF NOT EXISTS idx_transactions_symbol ON transactions(symbol);
CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_acknowledged ON alerts(acknowledged);
CREATE INDEX IF NOT EXISTS idx_client_exposures_risk ON client_exposures(risk_level);
CREATE INDEX IF NOT EXISTS idx_symbol_exposures_risk ON symbol_exposures(risk_level);

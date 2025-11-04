-- Seed initial data for testing
-- Creates sample client and symbol exposure records

-- Initialize some client exposure records
INSERT INTO client_exposures (client_id, total_exposure, position_count, risk_level)
VALUES 
    ('CLIENT_001', 0, 0, 'LOW'),
    ('CLIENT_002', 0, 0, 'LOW'),
    ('CLIENT_003', 0, 0, 'LOW'),
    ('CLIENT_004', 0, 0, 'LOW'),
    ('CLIENT_005', 0, 0, 'LOW')
ON CONFLICT (client_id) DO NOTHING;

-- Initialize some symbol exposure records
INSERT INTO symbol_exposures (symbol, total_exposure, transaction_count, risk_level)
VALUES 
    ('AAPL', 0, 0, 'LOW'),
    ('GOOGL', 0, 0, 'LOW'),
    ('MSFT', 0, 0, 'LOW'),
    ('AMZN', 0, 0, 'LOW'),
    ('TSLA', 0, 0, 'LOW'),
    ('META', 0, 0, 'LOW'),
    ('NVDA', 0, 0, 'LOW')
ON CONFLICT (symbol) DO NOTHING;

-- Initialize risk metrics with baseline
INSERT INTO risk_metrics (
    timestamp,
    total_transactions,
    total_exposure,
    active_clients,
    active_symbols,
    high_risk_clients,
    high_risk_symbols,
    alerts_generated
)
VALUES (
    CURRENT_TIMESTAMP,
    0,
    0,
    0,
    0,
    0,
    0,
    0
);

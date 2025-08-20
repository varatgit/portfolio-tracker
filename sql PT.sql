-- Table for storing asset classes (e.g., Equities, Fixed Income, Crypto)
CREATE TABLE asset_classes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

-- Table for user's assets/holdings
CREATE TABLE assets (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL UNIQUE,
    asset_class_id INTEGER REFERENCES asset_classes(id),
    name VARCHAR(100)
);

-- Table for all financial transactions
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER REFERENCES assets(id),
    transaction_date DATE NOT NULL,
    transaction_type VARCHAR(20) NOT NULL, -- e.g., 'BUY', 'SELL', 'DIVIDEND'
    quantity NUMERIC(15, 6) NOT NULL,
    price_per_share NUMERIC(15, 6) NOT NULL,
    total_cost NUMERIC(15, 6) NOT NULL
);

-- Insert initial asset classes
INSERT INTO asset_classes (name) VALUES
('Equities'),
('Fixed Income'),
('Cryptocurrency'),
('Cash');
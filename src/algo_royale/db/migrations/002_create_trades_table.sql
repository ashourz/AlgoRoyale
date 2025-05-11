-- db\migrations\002_create_trades_table.sql

-- Trades table
CREATE TABLE
    trades (
        id SERIAL PRIMARY KEY,
        symbol TEXT NOT NULL,
        direction TEXT CHECK (direction IN ('long', 'short')) NOT NULL,
        entry_price NUMERIC(10, 4),
        exit_price NUMERIC(10, 4),
        shares INTEGER,
        entry_time TIMESTAMP,
        exit_time TIMESTAMP,
        strategy_phase TEXT CHECK (
            strategy_phase IN ('breakout', 'momentum', 'mean_reversion')
        ),
        pnl NUMERIC(10, 4),
        notes TEXT
    );
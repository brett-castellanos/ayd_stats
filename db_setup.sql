CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    kgs_id VARCHAR(64) UNIQUE NOT NULL,
    ayd BOOLEAN DEFAULT false,
    eyd BOOLEAN DEFAULT false
);

CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    black VARCHAR(64) REFERENCES users(kgs_id),
    white VARCHAR(64) REFERENCES users(kgs_id),
    b_win BOOLEAN DEFAULT false,
    w_win BOOLEAN DEFAULT false,
    tmstmp DATE DEFAULT NULL,
    yd_game BOOLEAN DEFAULT false
);
-- enable UUID support
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- USERS
CREATE TABLE IF NOT EXISTS users(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    login BOOLEAN DEFAULT TRUE,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    display_name TEXT
);

-- ACCOUNTS
CREATE TABLE IF NOT EXISTS accounts(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) on DELETE CASCADE
);

-- SCHEDULE
CREATE TABLE IF NOT EXISTS schedules(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    arguments SMALLINT[]
);

-- CATEGORY
CREATE TABLE IF NOT EXISTS categories(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    next_occurance_id UUID,
    reoccurance_schedule_id UUID,
    name TEXT NOT NULL,
    priority SMALLINT DEFAULT 0 NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (next_occurance_id) REFERENCES categories(id),
    FOREIGN KEY (reoccurance_schedule_id) REFERENCES schedules(id)
);

-- TRANSACTIONS
CREATE TABLE IF NOT EXISTS transactions(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL,
    spent_from UUID,
    amount NUMERIC NOT NULL,
    description TEXT,
    payee TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (spent_from) REFERENCES categories(id)
);

-- SHARED USERS
CREATE TABLE IF NOT EXISTS shared_users(
    single_user_id UUID NOT NULL,
    shared_user_id UUID NOT NULL,
    PRIMARY KEY (single_user_id, shared_user_id),
    FOREIGN KEY (single_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (shared_user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    level VARCHAR(20) DEFAULT 'A1',
    memory TEXT DEFAULT '',
    mistake TEXT DEFAULT '',
    error_counters JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    participant VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);

CREATE TABLE IF NOT EXISTS user_topics (
    id                  SERIAL PRIMARY KEY,
    user_id             BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    topic_key           VARCHAR(100) NOT NULL,
    status              VARCHAR(20) DEFAULT 'new',        -- new / practicing / mastered / weak
    mastery_streak      INTEGER DEFAULT 0,
    times_correct       INTEGER DEFAULT 0,
    times_mistake       INTEGER DEFAULT 0,
    first_seen          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_mastered       TIMESTAMP,
    last_mistake        TIMESTAMP,
    last_practiced     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_type VARCHAR(50),
    UNIQUE(user_id, topic_key)
);

CREATE INDEX IF NOT EXISTS idx_user_topics_user_id ON user_topics(user_id);
CREATE INDEX IF NOT EXISTS idx_user_topics_status ON user_topics(status);
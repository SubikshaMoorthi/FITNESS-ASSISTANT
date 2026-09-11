CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_profile (
    user_id INTEGER PRIMARY KEY REFERENCES users(user_id),
    age INTEGER,
    height_cm DECIMAL(5,2),
    weight_kg DECIMAL(5,2),
    fitness_level VARCHAR(50),
    goal VARCHAR(100),
    preferences JSONB,
    constraints JSONB,
    available_workout_minutes INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE daily_health_data (
    health_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    date DATE NOT NULL,
    sleep_hours DECIMAL(4,2),
    activity_level VARCHAR(50),
    steps INTEGER,
    calories INTEGER,
    fatigue_score INTEGER,
    recovery_score INTEGER,
    workout_intensity INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workout_history (
    workout_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    date DATE NOT NULL,
    workout_type VARCHAR(100),
    duration_minutes INTEGER,
    intensity INTEGER,
    notes TEXT
);

CREATE TABLE recommendations (
    recommendation_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    date DATE NOT NULL,
    predicted_state VARCHAR(50),
    intervention VARCHAR(100),
    suitability_score DECIMAL(5,2),
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE feedback (
    feedback_id SERIAL PRIMARY KEY,
    recommendation_id INTEGER REFERENCES recommendations(recommendation_id),
    completed BOOLEAN,
    difficulty_rating INTEGER,
    user_feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE progress (
    progress_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    date DATE NOT NULL,
    weight_kg DECIMAL(5,2),
    steps INTEGER,
    workout_count INTEGER,
    calories_burned INTEGER,
    notes TEXT
);

-- Explainable Violence Incitation Detection Platform
-- Database Schema for PostgreSQL

-- Create Custom ENUM types
CREATE TYPE user_role AS ENUM ('Admin', 'Moderator', 'Analyst');
CREATE TYPE prediction_level1 AS ENUM ('Violence', 'Non-Violence');
CREATE TYPE prediction_level2 AS ENUM ('Gender', 'Economic', 'Ethnic', 'Political', 'Religious', 'General', 'None');
CREATE TYPE run_status AS ENUM ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED');

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'Analyst',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Datasets Table
CREATE TABLE IF NOT EXISTS datasets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Dataset Versions Table
CREATE TABLE IF NOT EXISTS dataset_versions (
    id SERIAL PRIMARY KEY,
    dataset_id INTEGER REFERENCES datasets(id) ON DELETE CASCADE NOT NULL,
    version_tag VARCHAR(50) NOT NULL,
    dvc_hash VARCHAR(255),
    file_path VARCHAR(512) NOT NULL,
    record_count INTEGER DEFAULT 0,
    metadata JSONB,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_dataset_version UNIQUE (dataset_id, version_tag)
);

-- Models Table
CREATE TABLE IF NOT EXISTS models (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    version_tag VARCHAR(50) NOT NULL,
    mlflow_run_id VARCHAR(255),
    is_active BOOLEAN DEFAULT FALSE,
    accuracy FLOAT,
    f1_score FLOAT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_model_version UNIQUE (name, version_tag)
);

-- Training Runs Table
CREATE TABLE IF NOT EXISTS training_runs (
    id SERIAL PRIMARY KEY,
    model_id INTEGER REFERENCES models(id) ON DELETE SET NULL,
    dataset_version_id INTEGER REFERENCES dataset_versions(id) ON DELETE SET NULL,
    status run_status DEFAULT 'PENDING',
    mlflow_run_id VARCHAR(255),
    metrics JSONB,
    logs TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL
);

-- Predictions Table
CREATE TABLE IF NOT EXISTS predictions (
    id BIGSERIAL PRIMARY KEY,
    text_content TEXT NOT NULL,
    normalized_content TEXT,
    level1_pred prediction_level1 NOT NULL,
    level1_conf FLOAT NOT NULL,
    level2_pred prediction_level2 DEFAULT 'None',
    level2_conf FLOAT,
    model_id INTEGER REFERENCES models(id) ON DELETE SET NULL,
    moderator_override prediction_level1,
    moderator_override_level2 prediction_level2,
    overridden_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Explanations Table
CREATE TABLE IF NOT EXISTS explanations (
    id BIGSERIAL PRIMARY KEY,
    prediction_id BIGINT REFERENCES predictions(id) ON DELETE CASCADE UNIQUE NOT NULL,
    lime_explanation JSONB, -- Word importance mapping
    shap_explanation JSONB, -- SHAP values mapping
    attention_weights JSONB, -- Attention maps per head/token
    human_explanation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Audit Logs Table
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(255),
    details JSONB,
    ip_address VARCHAR(45),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- System Metrics Table
CREATE TABLE IF NOT EXISTS system_metrics (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    cpu_utilization FLOAT NOT NULL,
    memory_utilization FLOAT NOT NULL,
    gpu_utilization FLOAT,
    gpu_memory_utilization FLOAT,
    request_latency_ms FLOAT NOT NULL,
    error_count INTEGER DEFAULT 0,
    drift_score FLOAT
);

-- Indexing for high-throughput prediction logs and searches
CREATE INDEX idx_predictions_level1 ON predictions(level1_pred);
CREATE INDEX idx_predictions_created_at ON predictions(created_at);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_system_metrics_timestamp ON system_metrics(timestamp);

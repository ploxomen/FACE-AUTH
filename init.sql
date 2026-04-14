--CREAMOS LA BASE DE DATOS
CREATE DATABASE IF NOT EXISTS face_auth;

-- Habilitar la extensión pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    embedding VECTOR(128) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de latencias detalladas del logeo
CREATE TABLE IF NOT EXISTS login_latency_details (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    success BOOLEAN NOT NULL,

    upload_time_ms FLOAT,
    preprocess_time_ms FLOAT,
    detection_time_ms FLOAT,
    embedding_time_ms FLOAT,
    db_query_time_ms FLOAT,
    decision_time_ms FLOAT,
    total_latency_ms FLOAT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice para acelerar la búsqueda vectorial
CREATE INDEX IF NOT EXISTS idx_users_embedding
ON users USING hnsw (embedding vector_l2_ops);

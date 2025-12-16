-- 🎲 KAYOSCRYPTO DATABASE SETUP - SIMPLIFIED
CREATE DATABASE k_crypto ENCODING 'UTF8';

\c k_crypto;

CREATE USER kayos WITH PASSWORD 'kayopass';
GRANT ALL PRIVILEGES ON DATABASE k_crypto TO kayos;
GRANT CREATE ON DATABASE k_crypto TO kayos;

CREATE SCHEMA IF NOT EXISTS kayos_enterprise;
GRANT USAGE ON SCHEMA kayos_enterprise TO kayos;
GRANT ALL ON ALL TABLES IN SCHEMA kayos_enterprise TO kayos;
GRANT ALL ON ALL SEQUENCES IN SCHEMA kayos_enterprise TO kayos;

ALTER DATABASE k_crypto SET search_path TO kayos_enterprise, public;

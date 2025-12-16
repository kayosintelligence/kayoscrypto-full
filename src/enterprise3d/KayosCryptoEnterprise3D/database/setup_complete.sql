-- 🎲 KAYOSCRYPTO 3D ENTERPRISE - COMPLETE DATABASE SETUP
-- Setup completo em um único arquivo

-- Criar database
DROP DATABASE IF EXISTS k_crypto;
CREATE DATABASE k_crypto ENCODING 'UTF8';

-- Conectar ao database
\c k_crypto;

-- Criar usuário se não existir
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'kayos') THEN
        CREATE USER kayos WITH PASSWORD 'kayopass';
    END IF;
END
\$\$;

-- Conceder permissões
GRANT ALL PRIVILEGES ON DATABASE k_crypto TO kayos;
GRANT CREATE ON DATABASE k_crypto TO kayos;

-- Criar schema enterprise
CREATE SCHEMA IF NOT EXISTS kayos_enterprise;
GRANT USAGE ON SCHEMA kayos_enterprise TO kayos;
GRANT ALL ON ALL TABLES IN SCHEMA kayos_enterprise TO kayos;
GRANT ALL ON ALL SEQUENCES IN SCHEMA kayos_enterprise TO kayos;

-- Definir schema padrão
SET search_path TO kayos_enterprise;

-- 🎲 TABELA: CUBOS SATOR 3D
CREATE TABLE sator_cubes (
    cube_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cube_name VARCHAR(100) NOT NULL UNIQUE,
    security_level VARCHAR(20) NOT NULL DEFAULT 'enterprise',
    current_rotation_state JSONB NOT NULL,
    tenet_center_hash BYTEA NOT NULL,
    faces_configuration JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100) DEFAULT 'system',
    is_active BOOLEAN DEFAULT TRUE,
    rotation_count INTEGER DEFAULT 0
);

-- 🔑 TABELA: CHAVES CRIPTOGRÁFICAS 4D
CREATE TABLE cryptographic_keys_4d (
    key_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cube_id UUID NOT NULL REFERENCES sator_cubes(cube_id) ON DELETE CASCADE,
    meeting_point_data JSONB NOT NULL,
    master_secret_encrypted BYTEA NOT NULL,
    kyber_public_key BYTEA,
    kyber_secret_encrypted BYTEA,
    ecc_public_key_pem TEXT,
    ecc_private_encrypted BYTEA,
    key_size_bits INTEGER NOT NULL,
    algorithm_combination VARCHAR(100) NOT NULL,
    security_level VARCHAR(50) NOT NULL,
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    next_rotation_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    hsm_key_id VARCHAR(200),
    hsm_provider VARCHAR(50),
    generation_context JSONB
);

-- 🔒 TABELA: OPERAÇÕES CRIPTOGRÁFICAS
CREATE TABLE crypto_operations (
    operation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key_id UUID NOT NULL REFERENCES cryptographic_keys_4d(key_id),
    cube_id UUID NOT NULL REFERENCES sator_cubes(cube_id),
    operation_type VARCHAR(20) NOT NULL,
    input_data_hash BYTEA,
    output_data_hash BYTEA,
    cube_rotation_state JSONB NOT NULL,
    tenet_signature BYTEA NOT NULL,
    operation_duration_ms INTEGER,
    data_size_bytes INTEGER,
    client_ip INET,
    user_agent TEXT,
    auth_context JSONB,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'completed',
    error_message TEXT
);

-- 📊 TABELA: AUDITORIA
CREATE TABLE audit_trail (
    audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(50) NOT NULL,
    event_timestamp TIMESTAMPTZ DEFAULT NOW(),
    severity VARCHAR(10) NOT NULL DEFAULT 'INFO',
    user_id VARCHAR(100),
    cube_id UUID REFERENCES sator_cubes(cube_id),
    key_id UUID REFERENCES cryptographic_keys_4d(key_id),
    event_data JSONB NOT NULL,
    event_hash BYTEA NOT NULL,
    blockchain_tx_hash VARCHAR(100),
    previous_audit_hash BYTEA,
    client_ip INET,
    user_agent TEXT
);

-- 👥 TABELA: USUÁRIOS
CREATE TABLE enterprise_users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash BYTEA NOT NULL,
    salt BYTEA NOT NULL,
    mfa_secret_encrypted BYTEA,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    backup_codes_encrypted BYTEA,
    full_name VARCHAR(200),
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    permissions JSONB,
    last_login_at TIMESTAMPTZ,
    failed_login_attempts INTEGER DEFAULT 0,
    account_locked_until TIMESTAMPTZ,
    password_changed_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 🎲 TABELA: ROTATION HISTORY
CREATE TABLE cube_rotation_history (
    rotation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cube_id UUID NOT NULL REFERENCES sator_cubes(cube_id),
    rotation_sequence JSONB NOT NULL,
    axes_rotated JSONB NOT NULL,
    previous_state JSONB,
    new_state JSONB,
    tenet_signature BYTEA NOT NULL,
    rotation_hash BYTEA NOT NULL,
    rotated_by VARCHAR(100),
    rotation_timestamp TIMESTAMPTZ DEFAULT NOW(),
    rotation_duration_ms INTEGER
);

-- 🔐 TABELA: ENCRYPTED PAYLOADS
CREATE TABLE encrypted_payloads_3d (
    payload_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key_id UUID NOT NULL REFERENCES cryptographic_keys_4d(key_id),
    cube_id UUID NOT NULL REFERENCES sator_cubes(cube_id),
    ciphertext BYTEA NOT NULL,
    metadata_encrypted BYTEA NOT NULL,
    encryption_algorithm VARCHAR(50) NOT NULL,
    security_level VARCHAR(50) NOT NULL,
    access_policy JSONB,
    allowed_users JSONB,
    encrypted_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    last_accessed_at TIMESTAMPTZ,
    access_count INTEGER DEFAULT 0,
    is_compromised BOOLEAN DEFAULT FALSE
);

-- 🏦 TABELA: HSM MANAGEMENT
CREATE TABLE hsm_keys (
    hsm_key_id VARCHAR(200) PRIMARY KEY,
    provider VARCHAR(50) NOT NULL,
    key_type VARCHAR(50) NOT NULL,
    key_size_bits INTEGER NOT NULL,
    key_arn TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    rotation_count INTEGER DEFAULT 0,
    compliance_level VARCHAR(20) DEFAULT 'FIPS_140_3',
    key_usage JSONB,
    backup_enabled BOOLEAN DEFAULT TRUE,
    backup_location TEXT
);

-- 🔍 TABELA: THREAT DETECTION
CREATE TABLE threat_events (
    threat_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    threat_type VARCHAR(50) NOT NULL,
    threat_level VARCHAR(10) NOT NULL,
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    cube_id UUID REFERENCES sator_cubes(cube_id),
    key_id UUID REFERENCES cryptographic_keys_4d(key_id),
    user_id VARCHAR(100),
    threat_data JSONB NOT NULL,
    anomaly_score DECIMAL(5,4),
    auto_mitigated BOOLEAN DEFAULT FALSE,
    mitigation_action VARCHAR(100),
    analyst_notes TEXT,
    status VARCHAR(20) DEFAULT 'detected'
);

-- 🔄 TABELA: KEY ROTATION SCHEDULE
CREATE TABLE key_rotation_schedule (
    schedule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key_id UUID NOT NULL REFERENCES cryptographic_keys_4d(key_id),
    rotation_interval_days INTEGER NOT NULL,
    last_rotated_at TIMESTAMPTZ,
    next_rotation_at TIMESTAMPTZ NOT NULL,
    rotation_strategy VARCHAR(50) DEFAULT 'in_place',
    auto_rotation_enabled BOOLEAN DEFAULT TRUE,
    total_rotations INTEGER DEFAULT 0,
    last_rotation_status VARCHAR(20)
);

-- 🚀 CRIAÇÃO DE ÍNDICES

-- Índices para sator_cubes
CREATE INDEX idx_sator_cubes_name ON sator_cubes(cube_name);
CREATE INDEX idx_sator_cubes_active ON sator_cubes(is_active);

-- Índices para cryptographic_keys_4d
CREATE INDEX idx_keys_cube_id ON cryptographic_keys_4d(cube_id);
CREATE INDEX idx_keys_active ON cryptographic_keys_4d(is_active);
CREATE INDEX idx_keys_expiration ON cryptographic_keys_4d(expires_at);

-- Índices para crypto_operations
CREATE INDEX idx_operations_key_id ON crypto_operations(key_id);
CREATE INDEX idx_operations_cube_id ON crypto_operations(cube_id);
CREATE INDEX idx_operations_type ON crypto_operations(operation_type);
CREATE INDEX idx_operations_timestamp ON crypto_operations(started_at);

-- Índices para audit_trail
CREATE INDEX idx_audit_event_type ON audit_trail(event_type);
CREATE INDEX idx_audit_timestamp ON audit_trail(event_timestamp);

-- Índices para enterprise_users
CREATE INDEX idx_users_username ON enterprise_users(username);
CREATE INDEX idx_users_email ON enterprise_users(email);

-- Índices para cube_rotation_history
CREATE INDEX idx_rotations_cube_id ON cube_rotation_history(cube_id);
CREATE INDEX idx_rotations_timestamp ON cube_rotation_history(rotation_timestamp);

-- Índices para encrypted_payloads_3d
CREATE INDEX idx_payloads_key_id ON encrypted_payloads_3d(key_id);
CREATE INDEX idx_payloads_cube_id ON encrypted_payloads_3d(cube_id);

-- Índices para threat_events
CREATE INDEX idx_threats_type ON threat_events(threat_type);
CREATE INDEX idx_threats_timestamp ON threat_events(detected_at);

-- 🎲 DADOS INICIAIS

-- Inserir Cubo Sator 3D padrão
INSERT INTO sator_cubes (
    cube_id,
    cube_name,
    security_level,
    current_rotation_state,
    tenet_center_hash,
    faces_configuration
) VALUES (
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'::uuid,
    'kayos_enterprise_cube_1',
    'enterprise',
    '{"x": 0, "y": 0, "z": 0, "w": 0}'::jsonb,
    decode('a0eebc999c0b4ef8bb6d6bb9bd380a11a0eebc999c0b4ef8bb6d6bb9bd380a11', 'hex'),
    '{
        "north": {"verso": "Kyber512", "anverso": "Kyber1024"},
        "south": {"verso": "P-256", "anverso": "P-521"},
        "east": {"verso": "AES-128-GCM", "anverso": "AES-256-GCM"},
        "west": {"verso": "SHA-256", "anverso": "SHA3-512"},
        "top": {"verso": "ChaCha20", "anverso": "XChaCha20"},
        "bottom": {"verso": "HMAC-SHA256", "anverso": "BLAKE2b"}
    }'::jsonb
);

-- Inserir usuário admin inicial
INSERT INTO enterprise_users (
    user_id,
    username,
    email,
    password_hash,
    salt,
    full_name,
    role,
    mfa_enabled
) VALUES (
    'b1ffc99-9c0b-4ef8-bb6d-6bb9bd380a12'::uuid,
    'admin',
    'admin@kayoscrypto.com',
    decode('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'hex'),
    decode('salt1234', 'hex'),
    'Administrador KayosCrypto',
    'admin',
    true
);

-- 📊 VIEWS PARA MONITORING

-- View para dashboard de segurança
CREATE VIEW security_dashboard AS
SELECT 
    sc.cube_name,
    COUNT(ck.key_id) as active_keys,
    COUNT(CASE WHEN ck.expires_at < NOW() THEN 1 END) as expired_keys,
    COUNT(co.operation_id) as operations_24h
FROM sator_cubes sc
LEFT JOIN cryptographic_keys_4d ck ON sc.cube_id = ck.cube_id AND ck.is_active = true
LEFT JOIN crypto_operations co ON sc.cube_id = co.cube_id AND co.started_at > NOW() - INTERVAL '24 hours'
GROUP BY sc.cube_id, sc.cube_name;

-- View para compliance reporting
CREATE VIEW compliance_report AS
SELECT 
    sc.cube_name,
    ck.algorithm_combination,
    ck.security_level,
    ck.generated_at,
    ck.expires_at,
    CASE 
        WHEN ck.expires_at < NOW() THEN 'EXPIRED'
        WHEN ck.expires_at < NOW() + INTERVAL '7 days' THEN 'EXPIRING_SOON'
        ELSE 'VALID'
    END as key_status
FROM cryptographic_keys_4d ck
JOIN sator_cubes sc ON ck.cube_id = sc.cube_id
WHERE ck.is_active = true;

-- ✅ CONFIGURAÇÕES FINAIS

-- Função para updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS \$\$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
\$\$ LANGUAGE plpgsql;

-- Triggers para updated_at
CREATE TRIGGER update_sator_cubes_updated_at 
    BEFORE UPDATE ON sator_cubes 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_enterprise_users_updated_at 
    BEFORE UPDATE ON enterprise_users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant final permissions
GRANT ALL ON ALL TABLES IN SCHEMA kayos_enterprise TO kayos;
GRANT ALL ON ALL SEQUENCES IN SCHEMA kayos_enterprise TO kayos;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA kayos_enterprise TO kayos;

-- Configurar search_path para o database
ALTER DATABASE k_crypto SET search_path TO kayos_enterprise, public;

-- 🎉 CONCLUSÃO
COMMIT;

-- Mensagem de sucesso
\echo ''
\echo '🎲 ========================================================'
\echo '🎲 KAYOSCRYPTO 3D ENTERPRISE DATABASE CRIADO COM SUCESSO!'
\echo '🎲 ========================================================'
\echo '📊 Database: k_crypto'
\echo '👤 Usuário: kayos'
\echo '🔐 Senha: kayopass'
\echo '🏗️ Schema: kayos_enterprise'
\echo '📈 Tabelas: 10 tabelas enterprise'
\echo '🚀 Views: 2 views de monitoring'
\echo '⚡ Pronto para uso enterprise!'
\echo ''
\echo 'Para conectar: psql -d k_crypto -U kayos'
\echo 'Para Python: dbname=k_crypto user=kayos password=kayopass host=localhost'
\echo ''

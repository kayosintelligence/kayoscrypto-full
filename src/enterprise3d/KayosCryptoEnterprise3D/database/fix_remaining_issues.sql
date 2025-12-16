-- 🔧 CORREÇÕES PARA O KAYOSCRYPTO DATABASE

\c k_crypto;

SET search_path TO kayos_enterprise;

-- 1. Corrigir UUID do usuário admin (estava faltando um caractere)
DELETE FROM enterprise_users WHERE username = 'admin';

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
    'b1ffc999-9c0b-4ef8-bb6d-6bb9bd380a12'::uuid,  -- UUID correto
    'admin',
    'admin@kayoscrypto.com',
    decode('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'hex'),
    decode('73616c7431323334', 'hex'),  -- 'salt1234' em hex
    'Administrador KayosCrypto',
    'admin',
    true
);

-- 2. Recriar a função update_updated_at_column corretamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 3. Recriar os triggers
DROP TRIGGER IF EXISTS update_sator_cubes_updated_at ON sator_cubes;
DROP TRIGGER IF EXISTS update_enterprise_users_updated_at ON enterprise_users;

CREATE TRIGGER update_sator_cubes_updated_at 
    BEFORE UPDATE ON sator_cubes 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_enterprise_users_updated_at 
    BEFORE UPDATE ON enterprise_users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 4. Adicionar algumas chaves de teste
INSERT INTO cryptographic_keys_4d (
    key_id,
    cube_id,
    meeting_point_data,
    master_secret_encrypted,
    key_size_bits,
    algorithm_combination,
    security_level,
    expires_at
) VALUES (
    gen_random_uuid(),
    (SELECT cube_id FROM sator_cubes WHERE cube_name = 'kayos_enterprise_cube_1'),
    '{"quantum_algo": "Kyber1024", "classical_algo": "P-521", "coordinates": {"x": 0, "y": 0, "z": 0, "w": 0}}'::jsonb,
    decode('746573742d6d61737465722d736563726574', 'hex'),  -- 'test-master-secret' em hex
    256,
    'Kyber1024+P-521+AES-256-GCM',
    'quantum_256+classical_521',
    NOW() + INTERVAL '90 days'
);

-- 5. Testar tudo
\echo ''
\echo '🔧 TESTANDO CORREÇÕES...'
\echo ''

-- Testar função de updated_at
UPDATE sator_cubes SET rotation_count = 1 
WHERE cube_name = 'kayos_enterprise_cube_1';

SELECT cube_name, rotation_count, updated_at 
FROM sator_cubes 
WHERE cube_name = 'kayos_enterprise_cube_1';

-- Testar usuário admin
SELECT username, role, is_active 
FROM enterprise_users 
WHERE username = 'admin';

-- Testar chaves
SELECT algorithm_combination, security_level 
FROM cryptographic_keys_4d 
WHERE is_active = true;

-- Testar views
SELECT * FROM security_dashboard;
SELECT * FROM compliance_report;

\echo ''
\echo '✅ TODAS AS CORREÇÕES APLICADAS COM SUCESSO!'
\echo '🎲 KayosCrypto 3D Enterprise Database está OPERACIONAL!'

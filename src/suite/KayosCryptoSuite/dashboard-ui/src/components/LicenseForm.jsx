// dashboard-ui/src/components/LicenseForm.jsx

import React, { useState } from 'react';
import axios from 'axios';

// Define URL da API backend com fallback configurável via Vite
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_PREFIX = `${API_BASE_URL.replace(/\/$/, '')}/api/v1`;

function LicenseForm() {
    // Estados para armazenar os dados do formulário
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [level, setLevel] = useState('standard');
    const [expirationDate, setExpirationDate] = useState('');

    // Estado para armazenar a resposta da API
    const [licenseResult, setLicenseResult] = useState(null);
    const [error, setError] = useState('');

    const handleSubmit = async (event) => {
        event.preventDefault(); // Impede o recarregamento da página
        setError('');
        setLicenseResult(null);

        const licenseData = {
            user_data: { name, email },
            level: level,
            expiration_date: expirationDate,
            metadata: {
                source: 'dashboard',
                issued_at: new Date().toISOString(),
            },
        };

        try {
            console.log("Enviando para a API:", licenseData);
            const response = await axios.post(`${API_PREFIX}/licenses/generate`, licenseData);
            setLicenseResult(response.data);
            console.log("Resposta da API:", response.data);
        } catch (err) {
            console.error("Erro ao gerar licença:", err.response ? err.response.data : err.message);
            const detail = err.response?.data?.detail || err.response?.data?.error || err.message;
            setError(detail || 'Não foi possível conectar à API.');
        }
    };

    return (
        <section className="widget-card license-form-container">
            <h2>Gerar Nova Licença</h2>
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label>Nome do Usuário:</label>
                    <input type="text" value={name} onChange={(e) => setName(e.target.value)} required />
                </div>
                <div className="form-group">
                    <label>Email do Usuário:</label>
                    <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
                </div>
                <div className="form-group">
                    <label>Nível da Licença:</label>
                    <input type="text" value={level} onChange={(e) => setLevel(e.target.value)} required />
                </div>
                <div className="form-group">
                    <label>Data de Expiração:</label>
                    <input type="date" value={expirationDate} onChange={(e) => setExpirationDate(e.target.value)} required />
                </div>
                <button type="submit">Gerar Licença</button>
            </form>

            {error && (
                <div className="result-error">
                    <h3>Erro:</h3>
                    <pre>{error}</pre>
                </div>
            )}

            {licenseResult && (
                <div className="result-success">
                    <h3>Licença Gerada com Sucesso</h3>
                    <div className="license-summary">
                        <p><strong>ID:</strong> {licenseResult.license_data?.license_id}</p>
                        <p><strong>Emitido em:</strong> {licenseResult.license_data?.issued_at}</p>
                        <p><strong>Válido até:</strong> {licenseResult.license_data?.expires_at}</p>
                        <p><strong>Nível:</strong> {licenseResult.license_data?.license_level}</p>
                    </div>
                    <div className="license-string">
                        <label>License JSON:</label>
                        <textarea
                            readOnly
                            value={licenseResult.license_string}
                            rows={8}
                            onFocus={(e) => e.target.select()}
                        />
                    </div>
                </div>
            )}
        </section>
    );
}

export default LicenseForm;

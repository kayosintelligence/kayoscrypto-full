import React, { useEffect, useState } from 'react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const TELEMETRY_URL = `${API_BASE_URL.replace(/\/$/, '')}/api/v1/telemetry/quantum-dashboard`;

function formatNumber(value, digits = 2, multiplier = 1) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return 'N/A';
  }
  return (Number(value) * multiplier).toFixed(digits);
}

function QuantumDashboardWidget() {
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchTelemetry = async (withSpinner = true) => {
    if (withSpinner) {
      setLoading(true);
    }
    setError('');
    try {
      const { data } = await axios.get(TELEMETRY_URL);
      setResponse(data);
    } catch (err) {
      const message = err.response?.data?.detail || err.response?.data?.error || err.message;
      setError(message);
      setResponse(null);
    } finally {
      if (withSpinner) {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    fetchTelemetry();
    const intervalId = window.setInterval(() => fetchTelemetry(false), 60000);
    return () => window.clearInterval(intervalId);
  }, []);

  const available = Boolean(response?.available);
  const summary = response?.summary || {};
  const entropy = summary.entropy || {};
  const resistance = summary.resistance || {};
  const certifications = summary.certifications || {};
  const highRisk = response?.high_risk || summary.high_risk || null;

  const generatedAt = response?.generated_at
    ? new Date(response.generated_at).toLocaleString()
    : 'Sem dados';

  return (
    <section className="widget-card quantum-dashboard-widget">
      <div className="widget-header">
        <h2>Resumo Quântico</h2>
        <button type="button" onClick={() => fetchTelemetry()} className="refresh-button">
          Atualizar
        </button>
      </div>

      {loading && <p className="widget-status">Carregando telemetria…</p>}
      {error && <p className="widget-status error">Erro: {error}</p>}

      {!loading && !error && !available && (
        <div className="widget-status">
          <p>Resumo ainda não disponível. Execute os scripts de telemetria para gerar os artefatos.</p>
          {response?.artifact_path && (
            <p><strong>Artefato esperado:</strong> {response.artifact_path}</p>
          )}
          {response?.error && (
            <p><strong>Detalhe:</strong> {response.error}</p>
          )}
        </div>
      )}

      {!loading && !error && available && (
        <div className="telemetry-body">
          <div className="snapshot-meta">
            <p><strong>Gerado em:</strong> {generatedAt}</p>
            {response?.artifact_path && (
              <p><strong>Arquivo:</strong> {response.artifact_path}</p>
            )}
          </div>

          <div className="widget-section">
            <h3>Entropia Geométrica</h3>
            <div className="metrics-grid">
              <div className="metric-item">
                <span className="metric-label">Snapshots</span>
                <span className="metric-value">{entropy.snapshots ?? '0'}</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Entropia média (bits)</span>
                <span className="metric-value">{formatNumber(entropy.entropy_bits_avg, 2)}</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Entropia por byte (avg)</span>
                <span className="metric-value">{formatNumber(entropy.entropy_per_byte_avg, 3)}</span>
              </div>
            </div>
            {entropy.latest_snapshot && (
              <p className="widget-status">Último snapshot: {entropy.latest_snapshot}</p>
            )}
          </div>

          <div className="widget-section">
            <h3>Resistência Quântica</h3>
            <div className="metrics-grid">
              <div className="metric-item">
                <span className="metric-label">Relatórios</span>
                <span className="metric-value">{resistance.reports ?? '0'}</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Score médio</span>
                <span className="metric-value">{formatNumber(resistance.overall_score_avg, 2, 100)}%</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Readiness médio</span>
                <span className="metric-value">{formatNumber(resistance.readiness_index_avg, 2, 100)}%</span>
              </div>
            </div>
            {resistance.latest_report && (
              <p className="widget-status">Último relatório: {resistance.latest_report}</p>
            )}
          </div>

          {highRisk && (
            <div className="widget-section">
              <h3>Prontidão Alto Risco</h3>
              <div className="metrics-grid">
                <div className="metric-item">
                  <span className="metric-label">Score geral</span>
                  <span className="metric-value">{formatNumber(highRisk.overall_score, 2, 100)}%</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Shor</span>
                  <span className="metric-value">{formatNumber(highRisk.shor_resistance, 2, 100)}%</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Grover</span>
                  <span className="metric-value">{formatNumber(highRisk.grover_resistance, 2, 100)}%</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Throughput</span>
                  <span className="metric-value">{highRisk.throughput_mb_s?.toFixed(2)} MB/s</span>
                </div>
              </div>
              <p className="widget-status">
                Status: {highRisk.high_risk_ready ? '✅ Pronto para alto risco' : '⚠️ Em preparação' }
              </p>
              {Array.isArray(highRisk.recommendations) && highRisk.recommendations.length > 0 && (
                <ul>
                  {highRisk.recommendations.map((rec, index) => (
                    <li key={index}>{rec}</li>
                  ))}
                </ul>
              )}
            </div>
          )}

          <div className="widget-section">
            <h3>Certificações</h3>
            <div className="metrics-grid">
              <div className="metric-item">
                <span className="metric-label">Snapshots</span>
                <span className="metric-value">{certifications.snapshots ?? '0'}</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Última readiness</span>
                <span className="metric-value">{formatNumber(certifications.latest_readiness_percent, 1)}%</span>
              </div>
            </div>
            {certifications.latest_snapshot && (
              <p className="widget-status">Último snapshot: {certifications.latest_snapshot}</p>
            )}
            {certifications.latest_certification && (
              <p className="widget-status">Certificação foco: {certifications.latest_certification}</p>
            )}
            {certifications.latest_status && (
              <p className="widget-status">Status: {certifications.latest_status}</p>
            )}
          </div>
        </div>
      )}
    </section>
  );
}

export default QuantumDashboardWidget;

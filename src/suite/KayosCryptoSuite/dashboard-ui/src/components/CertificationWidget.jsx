import React, { useEffect, useState } from 'react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const SNAPSHOT_URL = `${API_BASE_URL.replace(/\/$/, '')}/api/v1/certifications/latest`;

function formatNumber(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return 'N/A';
  }
  return Number(value).toFixed(digits);
}

function CertificationWidget() {
  const [snapshot, setSnapshot] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchSnapshot = async (withSpinner = true) => {
    if (withSpinner) {
      setLoading(true);
    }
    setError('');
    try {
      const { data } = await axios.get(SNAPSHOT_URL);
      if (data?.available && data.snapshot) {
        setSnapshot(data.snapshot);
      } else {
        setSnapshot(null);
      }
    } catch (err) {
      const message = err.response?.data?.detail || err.response?.data?.error || err.message;
      setError(message);
    } finally {
      if (withSpinner) {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    fetchSnapshot();
    const intervalId = window.setInterval(() => fetchSnapshot(false), 60000);
    return () => window.clearInterval(intervalId);
  }, []);

  const renderedTimestamp = snapshot?.timestamp
    ? new Date(snapshot.timestamp).toLocaleString()
    : 'Sem dados';
  const quantumScore = snapshot?.quantum_score;
  const performance = snapshot?.performance_kbps;
  const scorecard = snapshot?.scorecard || null;
  const findings = Array.isArray(snapshot?.findings) ? snapshot.findings : [];
  const targetDelta = typeof snapshot?.target_delta === 'number'
    ? snapshot.target_delta
    : typeof scorecard?.target_delta === 'number'
      ? scorecard.target_delta
      : undefined;
  const semaphore = snapshot?.quantum_semaphore || scorecard?.semaphore;

  return (
    <section className="widget-card certification-widget">
      <div className="widget-header">
        <h2>Estado de Certificação</h2>
        <button type="button" onClick={() => fetchSnapshot()} className="refresh-button">
          Atualizar
        </button>
      </div>

      {loading && <p className="widget-status">Carregando snapshot…</p>}
      {error && <p className="widget-status error">Erro: {error}</p>}

      {!loading && !error && !snapshot && (
        <p className="widget-status">Nenhum snapshot disponível ainda. Gere uma operação com assurance.</p>
      )}

      {!loading && !error && snapshot && (
        <div className="certification-body">
          <div className="snapshot-meta">
            <p><strong>Última atualização:</strong> {renderedTimestamp}</p>
            <p>
              <strong>Quantum Score:</strong> {quantumScore === undefined ? 'N/A' : `${formatNumber(quantumScore * 100, 1)}%`}
            </p>
            <p>
              <strong>Performance:</strong> {performance === undefined ? 'N/A' : `${formatNumber(performance, 2)} KB/s`}
            </p>
            {targetDelta !== undefined && (
              <p>
                <strong>Delta para 0.95:</strong> {formatNumber(targetDelta, 3)}
              </p>
            )}
            {semaphore && (
              <p><strong>Semáforo:</strong> {semaphore}</p>
            )}
            {snapshot.context?.quantum_mode && (
              <p><strong>Modo:</strong> {snapshot.context.quantum_mode}</p>
            )}
          </div>

          {snapshot.metrics && (
            <div className="metrics-grid">
              {Object.entries(snapshot.metrics).map(([key, value]) => (
                <div key={key} className="metric-item">
                  <span className="metric-label">{key}</span>
                  <span className="metric-value">{formatNumber(value, 3)}</span>
                </div>
              ))}
            </div>
          )}

          {scorecard && (
            <div className="widget-section">
              <h3>Quantum Scorecard</h3>
              <div className="metrics-grid">
                {Object.entries(scorecard.phase_scores || {}).map(([key, value]) => (
                  <div key={key} className="metric-item">
                    <span className="metric-label">Fase {key}</span>
                    <span className="metric-value">{formatNumber(Number(value) * 100, 2)}%</span>
                  </div>
                ))}
              </div>
              <div className="scorecard-meta">
                <span>Composite: {formatNumber(Number(scorecard.composite_score) * 100, 2)}%</span>
                <span>Readiness: {formatNumber(Number(scorecard.readiness_index) * 100, 2)}%</span>
                <span>Δ alvo: {formatNumber(Number(targetDelta ?? 0), 3)}</span>
                {scorecard.semaphore && <span>Semáforo: {scorecard.semaphore}</span>}
              </div>
              {scorecard.threat_scores && (
                <div className="metrics-grid threat-grid">
                  {Object.entries(scorecard.threat_scores).map(([key, value]) => (
                    <div key={key} className="metric-item">
                      <span className="metric-label">{key}</span>
                      <span className="metric-value">{formatNumber(Number(value) * 100, 2)}%</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {snapshot.suggestions && snapshot.suggestions.length > 0 && (
            <div className="widget-section">
              <h3>Sugestões</h3>
              <ul>
                {snapshot.suggestions.map((suggestion, index) => (
                  <li key={index}>{suggestion}</li>
                ))}
              </ul>
            </div>
          )}

          {findings.length > 0 && (
            <div className="widget-section">
              <h3>Findings</h3>
              <ul>
                {findings.map((finding, index) => (
                  <li key={index}>{finding}</li>
                ))}
              </ul>
            </div>
          )}

          {snapshot.roadmap?.certifications && snapshot.roadmap.certifications.length > 0 && (
            <div className="widget-section">
              <h3>Roadmap de Certificações</h3>
              <ul className="roadmap-list">
                {snapshot.roadmap.certifications.map((item) => {
                  const cost = typeof item.cost_usd === 'number'
                    ? `$${item.cost_usd.toLocaleString('en-US')}`
                    : 'N/A';
                  const effort = item.effort_weeks !== undefined
                    ? `${item.effort_weeks} semanas`
                    : 'Sem estimativa';

                  return (
                    <li key={item.name}>
                    <div className="roadmap-item">
                      <span className="roadmap-name">{item.name}</span>
                      <span className="roadmap-readiness">{item.readiness}</span>
                      <span className="roadmap-status">{item.status}</span>
                    </div>
                    <div className="roadmap-meta">
                      <span>{effort}</span>
                      <span>{cost}</span>
                    </div>
                  </li>
                  );
                })}
              </ul>
            </div>
          )}
        </div>
      )}
    </section>
  );
}

export default CertificationWidget;

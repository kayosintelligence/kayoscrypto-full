// dashboard-ui/src/App.jsx

import React from 'react';
import LicenseForm from './components/LicenseForm';
import CertificationWidget from './components/CertificationWidget';
import QuantumDashboardWidget from './components/QuantumDashboardWidget';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>KayosCryptoSuite Dashboard</h1>
      </header>
      <main className="dashboard-grid">
        <LicenseForm />
        <CertificationWidget />
        <QuantumDashboardWidget />
      </main>
    </div>
  );
}

export default App;

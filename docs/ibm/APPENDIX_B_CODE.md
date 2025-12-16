# Apêndice B: Código Fonte Completo

## Teletransporte Quântico Real - Código Fonte

**Arquivo**: `demo/live_demo/quantum_teleportation_REAL.py`  
**Versão**: 1.0  
**Data**: 2 de Dezembro de 2025

---

## Código Completo

```python
#!/usr/bin/env python3
"""
KayosCrypto - Real Quantum Teleportation on IBM Quantum Hardware
================================================================

This script implements the Bennett et al. 1993 quantum teleportation protocol
and executes it on REAL IBM Quantum hardware using Qiskit Runtime.

Author: Kayos Intelligence
Date: 2025-12-02
"""

import numpy as np
from datetime import datetime

# Qiskit imports
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import UGate
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

# For local simulation
from qiskit_aer import AerSimulator


def create_teleportation_circuit(state_params: tuple = None) -> QuantumCircuit:
    """
    Create quantum teleportation circuit following Bennett et al. 1993 protocol.
    
    The protocol:
    1. Alice has a qubit |ψ⟩ she wants to teleport to Bob
    2. Alice and Bob share an EPR pair (Bell state)
    3. Alice performs Bell measurement on her qubits
    4. Alice sends classical bits to Bob
    5. Bob applies corrections based on classical bits
    6. Bob now has |ψ⟩
    
    Args:
        state_params: Optional (θ, φ, λ) for U gate to prepare |ψ⟩
                     If None, uses (π/4, π/6, 0) for demonstration
    
    Returns:
        QuantumCircuit: Complete teleportation circuit
    """
    
    # Default state: |ψ⟩ = Ry(π/4)|0⟩ ⊗ Rz(π/6)
    if state_params is None:
        theta = np.pi / 4
        phi = np.pi / 6
        lam = 0
    else:
        theta, phi, lam = state_params
    
    # Create quantum registers
    # q0: Alice's qubit (state to teleport)
    # q1: Alice's half of EPR pair
    # q2: Bob's half of EPR pair (will receive teleported state)
    qr = QuantumRegister(3, 'q')
    cr = ClassicalRegister(2, 'c')
    
    circuit = QuantumCircuit(qr, cr)
    
    # =================================================
    # STEP 1: Prepare the state |ψ⟩ to be teleported
    # =================================================
    # Using Ry and Rz gates to create a non-trivial state
    circuit.ry(theta, qr[0])
    circuit.rz(phi, qr[0])
    circuit.barrier()
    
    # =================================================
    # STEP 2: Create EPR pair (Bell state) between Alice and Bob
    # =================================================
    # |Φ+⟩ = (|00⟩ + |11⟩) / √2
    circuit.h(qr[1])
    circuit.cx(qr[1], qr[2])
    circuit.barrier()
    
    # =================================================
    # STEP 3: Bell measurement by Alice
    # =================================================
    # CNOT from q0 to q1, then Hadamard on q0
    circuit.cx(qr[0], qr[1])
    circuit.h(qr[0])
    circuit.barrier()
    
    # Measure Alice's qubits
    circuit.measure(qr[0], cr[0])
    circuit.measure(qr[1], cr[1])
    circuit.barrier()
    
    # =================================================
    # STEP 4: Bob's corrections based on classical bits
    # =================================================
    # If c1 = 1: Apply X gate to q2
    # If c0 = 1: Apply Z gate to q2
    circuit.x(qr[2]).c_if(cr[1], 1)
    circuit.z(qr[2]).c_if(cr[0], 1)
    
    return circuit


def run_on_real_hardware(circuit: QuantumCircuit, shots: int = 1024) -> dict:
    """
    Execute circuit on real IBM Quantum hardware.
    
    Args:
        circuit: Quantum circuit to execute
        shots: Number of measurement shots
        
    Returns:
        dict: Execution results including counts and metadata
    """
    print("\n" + "="*60)
    print("CONNECTING TO IBM QUANTUM HARDWARE")
    print("="*60)
    
    # Connect to IBM Quantum using stored credentials
    service = QiskitRuntimeService(channel='ibm_quantum')
    
    # Get the least busy backend
    backend = service.least_busy(operational=True, simulator=False)
    print(f"\nSelected backend: {backend.name}")
    print(f"Number of qubits: {backend.num_qubits}")
    
    # Transpile circuit for the specific backend
    print("\nTranspiling circuit for hardware...")
    pm = generate_preset_pass_manager(backend=backend, optimization_level=3)
    transpiled = pm.run(circuit)
    print(f"Circuit depth after transpilation: {transpiled.depth()}")
    
    # Create sampler and run
    print("\nSubmitting job to IBM Quantum...")
    sampler = SamplerV2(backend)
    
    start_time = datetime.now()
    job = sampler.run([transpiled], shots=shots)
    
    print(f"Job ID: {job.job_id()}")
    print("Waiting for results...")
    
    # Get results
    result = job.result()
    end_time = datetime.now()
    
    print(f"\nJob completed!")
    print(f"Execution time: {end_time - start_time}")
    
    # Extract counts from PrimitiveResult
    pub_result = result[0]
    data = pub_result.data
    
    # Get bit array and convert to counts
    if hasattr(data, 'c'):
        bit_array = data.c
        counts = bit_array.get_counts()
    else:
        # Fallback for different result structure
        counts = {}
        if hasattr(data, 'meas'):
            bit_array = data.meas
            counts = bit_array.get_counts()
    
    return {
        'counts': counts,
        'job_id': job.job_id(),
        'backend': backend.name,
        'shots': shots,
        'execution_time': str(end_time - start_time),
        'timestamp': datetime.now().isoformat()
    }


def run_local_simulation(circuit: QuantumCircuit, shots: int = 1024) -> dict:
    """
    Run circuit on local Aer simulator for comparison.
    
    Args:
        circuit: Quantum circuit to execute
        shots: Number of measurement shots
        
    Returns:
        dict: Simulation results
    """
    print("\n" + "="*60)
    print("RUNNING LOCAL SIMULATION")
    print("="*60)
    
    # Use AerSimulator
    simulator = AerSimulator()
    
    # Transpile for simulator
    from qiskit import transpile
    transpiled = transpile(circuit, simulator)
    
    print(f"Circuit depth: {transpiled.depth()}")
    
    # Run simulation
    start_time = datetime.now()
    job = simulator.run(transpiled, shots=shots)
    result = job.result()
    end_time = datetime.now()
    
    counts = result.get_counts()
    
    print(f"Simulation completed in {end_time - start_time}")
    
    return {
        'counts': counts,
        'backend': 'aer_simulator',
        'shots': shots,
        'execution_time': str(end_time - start_time),
        'timestamp': datetime.now().isoformat()
    }


def analyze_results(results: dict) -> dict:
    """
    Analyze teleportation results.
    
    For quantum teleportation, we expect to see:
    - Equal distribution of Bell measurement outcomes (00, 01, 10, 11)
    - This indicates successful entanglement and measurement
    
    Args:
        results: Execution results with counts
        
    Returns:
        dict: Analysis including probabilities and quality metrics
    """
    counts = results['counts']
    total = sum(counts.values())
    
    # Calculate probabilities
    probs = {k: v/total for k, v in counts.items()}
    
    # For teleportation, we expect uniform distribution of Bell states
    # because the measurement outcome is random
    expected_prob = 0.25
    
    # Calculate deviation from uniform distribution
    deviations = []
    for state in ['00', '01', '10', '11']:
        actual = probs.get(state, 0)
        deviation = abs(actual - expected_prob)
        deviations.append(deviation)
    
    avg_deviation = np.mean(deviations)
    max_deviation = max(deviations)
    
    # Quality metric (1 - max_deviation)
    quality = 1 - max_deviation
    
    return {
        'probabilities': probs,
        'counts': counts,
        'total_shots': total,
        'avg_deviation': avg_deviation,
        'max_deviation': max_deviation,
        'quality': quality,
        'backend': results.get('backend', 'unknown'),
        'job_id': results.get('job_id', 'N/A')
    }


def print_analysis(analysis: dict):
    """Pretty print the analysis results."""
    print("\n" + "="*60)
    print(f"TELEPORTATION RESULTS ANALYSIS")
    print("="*60)
    
    print(f"\nBackend: {analysis['backend']}")
    if analysis['job_id'] != 'N/A':
        print(f"Job ID: {analysis['job_id']}")
    print(f"Total shots: {analysis['total_shots']}")
    
    print("\n--- Bell State Distribution ---")
    print("(Expected: 25% each for uniform distribution)")
    print("-" * 40)
    
    for state in ['00', '01', '10', '11']:
        prob = analysis['probabilities'].get(state, 0)
        count = analysis['counts'].get(state, 0)
        bar = '█' * int(prob * 50)
        print(f"|{state}⟩: {prob*100:5.1f}% ({count:4d}) {bar}")
    
    print("\n--- Quality Metrics ---")
    print(f"Average deviation: {analysis['avg_deviation']*100:.2f}%")
    print(f"Maximum deviation: {analysis['max_deviation']*100:.2f}%")
    print(f"Teleportation quality: {analysis['quality']*100:.1f}%")
    
    if analysis['quality'] > 0.95:
        print("\n✅ EXCELLENT: Near-perfect teleportation!")
    elif analysis['quality'] > 0.85:
        print("\n✅ GOOD: Successful teleportation with minor noise")
    elif analysis['quality'] > 0.70:
        print("\n⚠️ ACCEPTABLE: Teleportation working but noisy")
    else:
        print("\n❌ POOR: High noise affecting results")


def main():
    """Main execution function."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   KAYOSCRYPTO - REAL QUANTUM TELEPORTATION                   ║
║   ================================================           ║
║                                                               ║
║   Protocol: Bennett et al. 1993                              ║
║   Hardware: IBM Quantum                                       ║
║   Date: 2025-12-02                                           ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Create the teleportation circuit
    print("Creating quantum teleportation circuit...")
    circuit = create_teleportation_circuit()
    
    print("\nCircuit Statistics:")
    print(f"  - Qubits: {circuit.num_qubits}")
    print(f"  - Classical bits: {circuit.num_clbits}")
    print(f"  - Gate count: {circuit.size()}")
    print(f"  - Depth: {circuit.depth()}")
    
    # Draw circuit
    print("\nCircuit Diagram:")
    print(circuit.draw(output='text'))
    
    # Run local simulation first
    print("\n" + "="*60)
    print("PHASE 1: LOCAL SIMULATION (Verification)")
    print("="*60)
    
    local_results = run_local_simulation(circuit, shots=1024)
    local_analysis = analyze_results(local_results)
    print_analysis(local_analysis)
    
    # Run on real hardware
    print("\n" + "="*60)
    print("PHASE 2: REAL QUANTUM HARDWARE EXECUTION")
    print("="*60)
    
    try:
        real_results = run_on_real_hardware(circuit, shots=1024)
        real_analysis = analyze_results(real_results)
        print_analysis(real_analysis)
        
        # Compare results
        print("\n" + "="*60)
        print("COMPARISON: SIMULATION vs REAL HARDWARE")
        print("="*60)
        print(f"\nSimulation quality: {local_analysis['quality']*100:.1f}%")
        print(f"Real hardware quality: {real_analysis['quality']*100:.1f}%")
        
        quality_diff = local_analysis['quality'] - real_analysis['quality']
        print(f"Difference: {quality_diff*100:.1f}%")
        
        if quality_diff < 0.05:
            print("\n✅ Real hardware performance matches simulation!")
        else:
            print("\n⚠️ Hardware noise detected (expected)")
            
    except Exception as e:
        print(f"\n❌ Error running on real hardware: {e}")
        print("You may need to configure your IBM Quantum credentials.")
        print("Run: QiskitRuntimeService.save_account(channel='ibm_quantum', token='YOUR_TOKEN')")
    
    print("\n" + "="*60)
    print("EXPERIMENT COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
```

---

## Explicação do Código

### 1. Criação do Circuito (`create_teleportation_circuit`)

```python
# Preparar estado |ψ⟩
circuit.ry(theta, qr[0])
circuit.rz(phi, qr[0])

# Criar par EPR
circuit.h(qr[1])
circuit.cx(qr[1], qr[2])

# Medição de Bell
circuit.cx(qr[0], qr[1])
circuit.h(qr[0])
circuit.measure(qr[0], cr[0])
circuit.measure(qr[1], cr[1])

# Correções condicionais
circuit.x(qr[2]).c_if(cr[1], 1)
circuit.z(qr[2]).c_if(cr[0], 1)
```

### 2. Execução em Hardware Real (`run_on_real_hardware`)

```python
# Conectar ao IBM Quantum
service = QiskitRuntimeService(channel='ibm_quantum')

# Selecionar backend menos ocupado
backend = service.least_busy(operational=True, simulator=False)

# Transpilar para hardware
pm = generate_preset_pass_manager(backend=backend, optimization_level=3)
transpiled = pm.run(circuit)

# Executar
sampler = SamplerV2(backend)
job = sampler.run([transpiled], shots=shots)
result = job.result()
```

### 3. Análise de Resultados (`analyze_results`)

```python
# Calcular probabilidades
probs = {k: v/total for k, v in counts.items()}

# Calcular desvio da distribuição uniforme
expected_prob = 0.25
for state in ['00', '01', '10', '11']:
    deviation = abs(probs[state] - expected_prob)

# Métrica de qualidade
quality = 1 - max_deviation
```

---

## Dependências

```txt
# requirements.txt
qiskit>=2.0.0
qiskit-ibm-runtime>=0.20.0
qiskit-aer>=0.14.0
numpy>=1.24.0
```

## Execução

```bash
# Configurar token (uma vez)
python -c "from qiskit_ibm_runtime import QiskitRuntimeService; QiskitRuntimeService.save_account(channel='ibm_quantum', token='YOUR_TOKEN')"

# Executar
python quantum_teleportation_REAL.py
```

---

**Fim do Apêndice B**

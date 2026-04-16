import cirq
import random

def build_oracle(input_qubits, output_qubit, secret_s, secret_b=0):
    """
    Build the oracle gate Uf for f(x) = s · x ⊕ b.

    Args:
        input_qubits: The n input qubits.
        output_qubit: The target qubit.
        secret_s: The secret bitstring (list of 0s and 1s).
        secret_b: The secret bias bit (0 or 1).
    """
    oracle_ops = []
    
    # If secret_b is 1, flip the output qubit
    if secret_b == 1:
        oracle_ops.append(cirq.X(output_qubit))
        
    # For each bit in s that is 1, apply a CNOT from the corresponding input to output
    for i, bit in enumerate(secret_s):
        if bit == 1:
            oracle_ops.append(cirq.CNOT(input_qubits[i], output_qubit))
            
    return oracle_ops

def build_circuit(n, secret_s, secret_b=0):
    """
    Build the Bernstein-Vazirani circuit.
    """
    input_qubits = cirq.LineQubit.range(n)
    output_qubit = cirq.LineQubit(n)

    circuit = cirq.Circuit()

    # Step 1: Initialize output qubit to |1>
    circuit.append(cirq.X(output_qubit))

    # Step 2: Apply Hadamard to all qubits
    circuit.append(cirq.H.on_each(*input_qubits, output_qubit))

    # Step 3: Apply oracle
    circuit.append(build_oracle(input_qubits, output_qubit, secret_s, secret_b))

    # Step 4: Apply Hadamard to input qubits
    circuit.append(cirq.H.on_each(*input_qubits))

    # Step 5: Measure input qubits
    circuit.append(cirq.measure(*input_qubits, key='result'))

    return circuit

def run_bv(n, secret_s, secret_b=0):
    circuit = build_circuit(n, secret_s, secret_b)
    
    # Simulate the circuit
    simulator = cirq.Simulator()
    result = simulator.run(circuit, repetitions=1)
    
    # Extract measured bits
    measured_bits = result.measurements['result'][0]
    
    print(f"Secret bitstring (s): {secret_s}")
    print(f"Secret bias (b):      {secret_b}")
    print(f"Measured bitstring:   {list(measured_bits)}")
    print(circuit)
    
    success = list(measured_bits) == secret_s
    print(f"Success: {success}\n")
    
    return success

if __name__ == '__main__':
    # Test with a 3-bit secret string
    run_bv(3, [1, 0, 1], 0)
    
    # Test with a 5-bit random secret string and random bias
    n = 5
    s = [random.randint(0, 1) for _ in range(n)]
    b = random.randint(0, 1)
    run_bv(n, s, b)

import cirq


def build_oracle(input_qubits, output_qubit, oracle_type):
    """
    Build the oracle gate Uf for a given function type.

    oracle_type options:
      'constant_0' — f(x) = 0 for all x (no-op on output qubit)
      'constant_1' — f(x) = 1 for all x (flip output qubit)
      'balanced'   — f(x) = XOR of all input bits (CNOT chain)
    """
    if oracle_type == 'constant_0':
        return []
    elif oracle_type == 'constant_1':
        return [cirq.X(output_qubit)]
    elif oracle_type == 'balanced':
        # XOR of all input qubits into the output qubit
        return [cirq.CNOT(q, output_qubit) for q in input_qubits]
    else:
        raise ValueError(f"Unknown oracle_type: '{oracle_type}'")


def build_circuit(n, oracle_type):
    """
    Build the Deutsch-Jozsa circuit for an n-bit input function.

    Steps:
      1. Initialise n input qubits |0...0> and 1 output qubit |1>
      2. Apply H to all qubits  →  uniform superposition
      3. Apply oracle Uf
      4. Apply H to input qubits
      5. Measure input qubits — all-zeros ⟹ constant, any 1 ⟹ balanced
    """
    input_qubits = cirq.LineQubit.range(n)
    output_qubit = cirq.LineQubit(n)

    circuit = cirq.Circuit()

    # Step 1: put the output qubit into |1>
    circuit.append(cirq.X(output_qubit))

    # Step 2: Hadamard on all qubits
    circuit.append(cirq.H.on_each(*input_qubits, output_qubit))

    # Step 3: oracle
    circuit.append(build_oracle(input_qubits, output_qubit, oracle_type))

    # Step 4: Hadamard on input qubits
    circuit.append(cirq.H.on_each(*input_qubits))

    # Step 5: measure input qubits
    circuit.append(cirq.measure(*input_qubits, key='result'))

    return circuit


def run(n, oracle_type):
    circuit = build_circuit(n, oracle_type)
    result = cirq.Simulator().simulate(circuit)

    # Read the measurement from the final state vector via a separate run
    measurement = cirq.Simulator().run(circuit, repetitions=1)
    bits = measurement.measurements['result'][0]

    is_constant = all(b == 0 for b in bits)
    verdict = 'constant' if is_constant else 'balanced'

    print(f"Oracle : {oracle_type}")
    print(f"Circuit ({n} input qubit{'s' if n != 1 else ''}):")
    print(circuit)
    print(f"Measured input qubits: {list(bits)}")
    print(f"Function is: {verdict}\n")
    return verdict


if __name__ == '__main__':
    # n=1 (classic Deutsch problem)
    run(1, 'constant_0')
    run(1, 'constant_1')
    run(1, 'balanced')

    # n=3
    run(3, 'constant_0')
    run(3, 'constant_1')
    run(3, 'balanced')

    run(10, 'constant_0')
    run(10, 'constant_1')
    run(10, 'balanced') 

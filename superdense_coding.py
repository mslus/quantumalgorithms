import cirq


def build_circuit_and_simulate(bits):
    # Generate a qubit pair and entangle it
    q0, q1 = cirq.LineQubit.range(2)

    circuit = cirq.Circuit()
    circuit.append(cirq.H(q0))
    circuit.append(cirq.CNOT(q0, q1))

    # Apply X/Z gates for various bit pairs we can be sending
    if bits[1] == 1:
        circuit.append(cirq.X(q0))
    if bits[0] == 1:
        circuit.append(cirq.Z(q0))

    # Decode and measure the state of qbits
    circuit.append(cirq.CNOT(q0, q1))
    circuit.append(cirq.H(q0))
    circuit.append(cirq.measure(q0, q1))

    # run the simulation - we would like to measure the end state
    sim = cirq.Simulator().run(circuit)
    return sim

if __name__ == '__main__':
    # Pair of bits to be sent
    bits = [1, 0]

    print("Coding the following bit pair:", bits)
    print(build_circuit_and_simulate(bits))


import cirq
import numpy as np

def make_oracle(input_qubits, output_qubits, secret_s):
    """Creates an oracle for Simon's algorithm.
    
    The oracle implements a function f(x) such that f(x) = f(y) 
    iff y = x ^ secret_s.
    """
    n = len(input_qubits)
    circuit = cirq.Circuit()
    
    # Copy input to output register
    for i in range(n):
        circuit.append(cirq.CNOT(input_qubits[i], output_qubits[i]))
        
    # Find the first '1' in secret_s to use as a control
    # This is a standard way to construct a simple Simon oracle
    first_one = -1
    for i, bit in enumerate(secret_s):
        if bit:
            first_one = i
            break
            
    if first_one != -1:
        for i, bit in enumerate(secret_s):
            if bit and i != first_one:
                # If secret_s[i] is 1, XOR input[first_one] into output[i]
                circuit.append(cirq.CNOT(input_qubits[first_one], output_qubits[i]))
                
    return circuit

def simon_algorithm(secret_s):
    n = len(secret_s)
    input_qubits = [cirq.GridQubit(0, i) for i in range(n)]
    output_qubits = [cirq.GridQubit(1, i) for i in range(n)]
    
    circuit = cirq.Circuit()
    
    # 1. Initialize input qubits to superposition
    circuit.append(cirq.H.on_each(*input_qubits))
    
    # 2. Apply the oracle
    circuit.append(make_oracle(input_qubits, output_qubits, secret_s))
    
    # 3. Apply H again to the input register
    circuit.append(cirq.H.on_each(*input_qubits))
    
    # 4. Measure the input register
    circuit.append(cirq.measure(*input_qubits, key='result'))
    
    # Simulate the circuit
    simulator = cirq.Simulator()
    
    # We need enough linear independent equations to solve for s
    # Usually ~n measurements are sufficient
    results = []
    print(f"Secret s: {secret_s}")
    print("Sampling equations (y such that y · s = 0 mod 2):")
    
    for _ in range(n + 5):
        sample = simulator.run(circuit)
        # Convert measurement to bitstring
        y = sample.measurements['result'][0]
        results.append(y)
        print(f"  y = {y}")
        
    return results

if __name__ == '__main__':
    # Define a secret bitstring s (e.g., 110)
    s = [1, 1, 0]
    measured_ys = simon_algorithm(s)
    
    print("\nNote: Each measured y satisfies the condition: sum(y_i * s_i) % 2 == 0.")
    print("To find 's', you would classically solve this system of linear equations.")

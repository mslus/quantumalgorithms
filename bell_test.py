import cirq

def create_bell_circuit():
    alice_query = cirq.GridQubit(0,0)
    alice_response = cirq.GridQubit(0,1)
    bob_query = cirq.GridQubit(1,0)
    bob_response = cirq.GridQubit(1,1)

    circuit = cirq.Circuit()
    circuit.append(cirq.H(alice_response))
    circuit.append(cirq.CNOT(alice_response, bob_response))
    circuit.append(cirq.H(alice_response)**(-0.25))

    # code random states for queries
    circuit.append([cirq.H(alice_query), cirq.H(bob_query)])

    # apply CNOTs between quesries and responses
    circuit.append(cirq.CNOT(alice_query, alice_response)**0.5)
    circuit.append(cirq.CNOT(bob_query, bob_response)**0.5)

    circuit.append([
        cirq.measure(alice_query, key='a'),
        cirq.measure(bob_query, key='b'),
        cirq.measure(alice_response, key='x'),
        cirq.measure(bob_response, key='y')
    ])

    return circuit

def run_simulation(iterations):
    circuit = create_bell_circuit()

    result = cirq.Simulator().run(circuit, repetitions=iterations)
    return result

def collect_results(iterations=1000):
    result = run_simulation(iterations)

    x = result.measurements['x'].flatten().tolist()
    y = result.measurements['y'].flatten().tolist()
    a = result.measurements['a'].flatten().tolist()
    b = result.measurements['b'].flatten().tolist()

    wons = [i^j == k*l for (i,j,k,l) in zip(x,y,a,b)].count(True)
    return wons/iterations

if __name__ == '__main__':
    ratio = collect_results(100)
    print(ratio)
import cirq
import random

def create_random_state(randX, randY):

  q = cirq.LineQubit(0)

  circuit = cirq.Circuit([cirq.X(q)**randX, cirq.Y(q)**randY])

  sim = cirq.Simulator().simulate(circuit)
  return sim.final_state_vector;


def create_circuit(randX, randY):
  msg, alice, bob = cirq.LineQubit.range(3)

  circuit = cirq.Circuit()
  circuit.append(cirq.H(alice))
  circuit.append(cirq.CNOT(alice, bob))

  # Create state that will be sent to Bob
  circuit.append([cirq.X(msg)**randX, cirq.Y(msg)**randY])

  circuit.append(cirq.CNOT(msg, alice))
  circuit.append(cirq.H(msg))
  circuit.append(cirq.measure(msg, alice))

  circuit.append(cirq.CNOT(alice, bob))
  circuit.append(cirq.CZ(msg, bob))

  sim = cirq.Simulator().simulate(circuit, qubit_order=[msg, alice, bob])

  return sim


if __name__ == '__main__':

  randX = random.random()
  randY = random.random()

  initial_state = create_random_state(randX, randY)
  final_state = create_circuit(randX, randY)

  print("Initial state:")
  print(initial_state)
  print("Final state:")
  print(final_state)




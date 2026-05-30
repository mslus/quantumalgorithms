import cirq
import math
import random
import fractions


# --- Classical helpers ---

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(math.isqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


def classical_order_finding(a, N):
    """Brute-force order r such that a^r ≡ 1 (mod N)."""
    r = 1
    val = a
    while val != 1:
        val = (val * a) % N
        r += 1
        if r > N:
            return None
    return r


# --- Quantum phase estimation for modular exponentiation ---

def build_qpe_circuit(a, N, n_count):
    """
    Quantum Phase Estimation circuit for the unitary U|y> = |ay mod N>.

    n_count : number of counting qubits (precision bits)
    The target register needs ceil(log2(N)) qubits.
    """
    n_target = math.ceil(math.log2(N + 1))
    counting = [cirq.LineQubit(i) for i in range(n_count)]
    target = [cirq.LineQubit(n_count + i) for i in range(n_target)]

    circuit = cirq.Circuit()

    # Hadamard on all counting qubits
    circuit.append(cirq.H.on_each(*counting))

    # Initialise target register to |1>
    circuit.append(cirq.X(target[0]))

    # Controlled-U^(2^k) gates — implemented classically via modular exponentiation
    for k, ctrl in enumerate(counting):
        exp = pow(a, 2 ** k, N)
        circuit.append(_controlled_modmul(ctrl, target, exp, N))

    # Inverse QFT on counting register
    circuit.append(_inverse_qft(counting))

    # Measure counting qubits
    circuit.append(cirq.measure(*counting, key='phase'))

    return circuit, counting


class ModularMultiplicationGate(cirq.Gate):
    """Unitary gate implementing |y> -> |a*y mod N> on an n-qubit register."""

    def __init__(self, a, N, n):
        self.a = a
        self.N = N
        self.n = n

    def _num_qubits_(self):
        return self.n

    def _unitary_(self):
        dim = 2 ** self.n
        import numpy as np
        mat = np.zeros((dim, dim), dtype=complex)
        for y in range(dim):
            out = (self.a * y) % self.N if y < self.N else y
            mat[out, y] = 1.0
        return mat

    def _circuit_diagram_info_(self, _):
        return [f'Mul({self.a} mod {self.N})'] + ['|'] * (self.n - 1)


def _controlled_modmul(ctrl, target_qubits, multiplier, N):
    gate = ModularMultiplicationGate(multiplier, N, len(target_qubits))
    return cirq.ControlledGate(gate).on(ctrl, *target_qubits)


def _inverse_qft(qubits):
    """Inverse Quantum Fourier Transform on the given qubits."""
    ops = []
    n = len(qubits)
    for i in range(n // 2):
        ops.append(cirq.SWAP(qubits[i], qubits[n - 1 - i]))
    for i in range(n):
        ops.append(cirq.H(qubits[i]))
        for j in range(i + 1, n):
            angle = -math.pi / (2 ** (j - i))
            ops.append(cirq.CZPowGate(exponent=angle / math.pi).on(qubits[j], qubits[i]))
    return ops


# --- Period finding via simulated QPE ---

def quantum_period_finding(a, N, n_count=8):
    """
    Run QPE simulation to estimate the order r of a mod N.
    Returns r if found, else None.
    """
    circuit, counting = build_qpe_circuit(a, N, n_count)
    sim = cirq.Simulator()
    result = sim.run(circuit, repetitions=10)

    candidates = set()
    for row in result.measurements['phase']:
        # Convert bit array to integer (little-endian)
        measured = sum(int(b) << i for i, b in enumerate(row))
        if measured == 0:
            continue
        # Phase = measured / 2^n_count  ->  continued fraction -> denominator = order
        phase = measured / (2 ** n_count)
        frac = fractions.Fraction(phase).limit_denominator(N)
        candidates.add(frac.denominator)

    for r in sorted(candidates):
        if r > 0 and pow(a, r, N) == 1:
            return r
    return None


# --- Main Shor's algorithm ---

def shors_factor(N, use_quantum=True):
    """
    Factor N using Shor's algorithm.
    Returns a non-trivial factor, or None if unsuccessful.
    """
    if N % 2 == 0:
        return 2
    if is_prime(N):
        print(f"{N} is prime — nothing to factor.")
        return None

    for _ in range(20):
        a = random.randint(2, N - 1)
        g = gcd(a, N)
        if g != 1:
            print(f"Lucky GCD shortcut: gcd({a}, {N}) = {g}")
            return g

        print(f"Trying a = {a} ...")

        if use_quantum:
            r = quantum_period_finding(a, N)
        else:
            r = classical_order_finding(a, N)

        if r is None or r % 2 != 0:
            print(f"  Order r={r} not useful, retrying.")
            continue

        candidate = pow(a, r // 2, N)
        if candidate == N - 1:
            print(f"  a^(r/2) ≡ -1 (mod N), retrying.")
            continue

        p = gcd(candidate - 1, N)
        q = gcd(candidate + 1, N)

        for factor in (p, q):
            if 1 < factor < N:
                print(f"  Found factor: {factor}")
                return factor

        print(f"  No useful factor from r={r}, retrying.")

    return None


if __name__ == '__main__':
    for N in [15, 21, 35]:
        print(f"\n{'='*40}")
        print(f"Factoring N = {N}")
        print(f"{'='*40}")

        # Use classical order finding for a clean, reliable demo
        factor = shors_factor(N, use_quantum=False)
        if factor:
            other = N // factor
            print(f"Result: {N} = {factor} x {other}")
        else:
            print("Failed to find a factor.")

        # Show the QPE circuit structure for N=15
        if N == 15:
            a = 7
            print(f"\nQPE circuit for a={a}, N={N}:")
            circuit, _ = build_qpe_circuit(a, N, n_count=4)
            print(circuit)

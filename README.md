# Key Relay Protocol (KRP) Verification Framework

This repository contains a Python-based framework for the simulation and verification of the **Key Relay Protocol (KRP)**, a cryptographic protocol designed to extend the reach of secure communication networks like Quantum Key Distribution (QKD) systems. The framework exhaustively tests the protocol's security properties on small, undirected graphs against a defined adversarial model.

## Table of Contents
1. [Mathematical Foundations](#mathematical-foundations)
   - [Network Model](#network-model)
   - [The Protocol](#the-protocol)
   - [Adversarial Model](#adversarial-model)
   - [Security Conditions](#security-conditions)
2. [Framework Components](#framework-components)
   - [`krp.py` - The Simulation Engine](#krppy---the-simulation-engine)
   - [`test_krp.py` - The Testing Suite](#test_krppy---the-testing-suite)
3. [How to Run](#how-to-run)
   - [Running the Simulation](#running-the-simulation)
   - [Running the Tests](#running-the-tests)

---

## Mathematical Foundations

The security of the KRP is analyzed using concepts from graph theory and linear algebra over the finite field of two elements, GF(2).

### Network Model

The communication network is modeled as a simple, undirected graph:

$$ G = (V, E) $$

- **V**: A set of nodes, representing users or network relays.
- **E**: A set of edges, representing secure communication links (e.g., QKD links) where local keys can be established.

### The Protocol

The KRP enables a user pair, $(u_1, u_2)$, to establish a shared secret key by leveraging the network's relay nodes.

1.  **Local Key Generation**: For each edge $e \in E$, a random local key $k_e \in \{0, 1\}$ is generated and shared securely between the two nodes connected by $e$. All operations are performed in GF(2), where addition corresponds to the XOR operation.

2.  **Shared Key Computation**: The user pair finds a path $P$ between $u_1$ and $u_2$. A path is a sequence of edges, $P = \{e_1, e_2, ..., e_m\}$. The final shared key, $K$, is computed by XORing the local keys of all edges along this path:

    $$ K = \bigoplus_{e \in P} k_e = k_{e_1} \oplus k_{e_2} \oplus ... \oplus k_{e_m} $$

    Since the same path is used (or any two paths that form a cycle), both users arrive at the identical key $K$.

### Adversarial Model

An adversary is defined by the set of edges they can wiretap.

- **Adversary($E_A$)**: An adversary who has compromised a subset of edges $E_A \subseteq E$.
- **Knowledge**: The adversary learns the local keys of all wiretapped edges: $\{k_e | e \in E_A\}$.
- **Goal**: To determine the shared key $K$ established between a non-compromised user pair.

### Security Conditions

The correctness of the KRP rests on two fundamental properties: soundness and secrecy.

#### Soundness

**Soundness** ensures that both users in a pair successfully establish the *exact same* key. The protocol is sound for a user pair $(u_1, u_2)$ if and only if they are in the same connected component of the graph $G$. If no path exists, no key can be formed.

#### Secrecy

**Secrecy** ensures that the adversary gains zero information about the final shared key. This is analyzed using linear algebra over GF(2).

- Let the set of all edges $E$ form a basis for a vector space of dimension $|E|$. Each edge $e_i$ is a basis vector.
- The user's path $P$ can be represented as a **path vector**, $\vec{p}$, where the $i$-th component is 1 if $e_i \in P$ and 0 otherwise.
- The adversary's knowledge corresponds to a **subspace**, $W$, spanned by the basis vectors of the wiretapped edges in $E_A$.

Information-theoretic secrecy holds if and only if the path vector $\vec{p}$ is linearly independent of the adversary's subspace $W$. Mathematically:

$$ \vec{p} \notin \text{span}(E_A) $$

This is equivalent to checking if the rank of the adversary's subspace increases when the path vector is added to its basis:

$$ \text{rank}(\{\vec{e} | e \in E_A\} \cup \{\vec{p}\}) = \text{rank}(\{\vec{e} | e \in E_A\}) + 1 $$

If the rank does not increase, the path vector can be constructed from the adversary's known vectors, and the key is compromised. The implementation in `krp.py` uses a helper function, `_rank_gf2`, to perform this rank comparison over GF(2) and verify secrecy.

---

## Framework Components

The project is divided into a simulation engine and a test suite.

### `krp.py` - The Simulation Engine

This file contains the core logic for the KRP simulation.

- **Data Structures**:
  - `UserPair`: Represents a user pair `(u1, u2)` and stores their computed keys.
  - `Adversary`: Represents the adversary and stores the set of wiretapped edges.

- **Key Functions**:
  - `enumerate_all_graphs(n_nodes)`: Exhaustively generates all non-isomorphic undirected graphs for a given number of nodes. This is crucial for testing the protocol on all possible small network topologies.
  - `simulate_krp(G, user_pairs, adversary, ...)`: The main simulation function. It takes a graph, user pairs, and an adversary, then executes the KRP and returns a dictionary containing:
    - `sound`: A boolean indicating if the soundness property holds.
    - `secrecy`: A boolean indicating if the secrecy property holds (currently a placeholder).
    - `log`: A detailed log of the simulation steps.

### `test_krp.py` - The Testing Suite

This file uses Python's `unittest` framework to verify the correctness of the simulation engine.

The test cases ensure that:

- `test_enumerate_all_graphs_small`: The graph enumeration function produces the correct number of graphs for small `n` (n=2, n=3).
- `test_simulate_krp_sound`: The protocol is correctly identified as **sound** when users are connected.
- `test_simulate_krp_no_path`: The protocol is correctly identified as **not sound** when users are in disconnected components of the graph.
- `test_adversary_observation`: The simulation log correctly records the keys observed by the adversary.

---

## How to Run

### Running the Simulation

To run the main simulation script, which will enumerate all graphs for 3 nodes and simulate the KRP on each, execute the following command:

```bash
python3 krp.py
```

The script's `if __name__ == "__main__":` block is configured to run a default scenario.

### Running the Tests

To run the unit tests and verify the framework's components, execute:

```bash
python3 -m unittest test_krp.py
```

All tests should pass, confirming that the simulation engine behaves as expected under the tested conditions.

---

## Example Simulation

Running `python3 krp.py` will enumerate all non-isomorphic graphs with 3 nodes, simulate the KRP on each, and save a visualization to the `plots/` directory. The adversary is assumed to have wiretapped all edges.

Below is the output for the complete graph on 3 nodes (K3):

```
--- Graph 4 ---
Plot saved to plots/graph_4_nodes_3.png
Local key for edge (0, 1): 1
Local key for edge (0, 2): 1
Local key for edge (1, 2): 1
UserPair (0,1) path: [0, 1], key: 1
Adversary wiretapped edges: {(0, 1), (0, 2), (1, 2)}, observed keys: [1, 1, 1]
SECRECY BREACH: Path for UserPair (0,1) is in adversary's subspace.
```

### Graph Visualization

The script generates the following visualization for the K3 graph. The user pair (0, 1) is highlighted in blue, and all edges are marked as wiretapped (red, dashed) because the adversary has compromised the entire network.

![K3 Graph Visualization](plots/graph_4_nodes_3.png)


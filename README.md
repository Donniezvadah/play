# Key Relay Protocol (KRP) Verification Framework

This repository contains a Python-based framework for the simulation and verification of a Key Relay Protocol (KRP). It is designed to exhaustively test the protocol's properties on small, undirected graphs against a defined adversarial model. The framework includes utilities for graph enumeration, protocol simulation, and property verification (soundness and secrecy).

## Table of Contents
1. [Core Concepts](#core-concepts)
   - [The Network Model](#the-network-model)
   - [The Key Relay Protocol](#the-key-relay-protocol)
   - [The Adversarial Model](#the-adversarial-model)
2. [Mathematical Foundations](#mathematical-foundations)
   - [Soundness Condition](#soundness-condition)
   - [Secrecy Condition](#secrecy-condition)
3. [Framework Components](#framework-components)
   - [`krp.py` - The Simulation Engine](#krppy---the-simulation-engine)
   - [`test_krp.py` - The Testing Suite](#test_krppy---the-testing-suite)
4. [How to Run](#how-to-run)
   - [Running the Simulation](#running-the-simulation)
   - [Running the Tests](#running-the-tests)

---

## Core Concepts

The framework is built around three core concepts: the network structure, the protocol itself, and the adversary who attempts to break it.

### The Network Model

The communication network is modeled as a simple, undirected graph:

**G = (V, E)**

- **V**: A set of nodes, representing users or network relays.
- **E**: A set of edges, representing communication links between nodes.

### The Key Relay Protocol

The KRP enables two users, `u1` and `u2`, to establish a shared secret key by leveraging the network's relay nodes.

The protocol proceeds in two main steps:

1.  **Local Key Distribution**: A random local key, `k_e`, is generated for each edge `e` in the network. In this implementation, these keys are single bits (elements from the finite field GF(2)).

2.  **Shared Key Computation**: The user pair `(u1, u2)` computes their shared key, `K`, by finding a path between them and combining the local keys along that path. The combination operation is the bitwise XOR (exclusive OR).

    For a path `P` consisting of edges `{e_1, e_2, ..., e_m}`, the shared key is:

    **K = k_e1 ⊕ k_e2 ⊕ ... ⊕ k_em**

    where `⊕` denotes the XOR operation.

### The Adversarial Model

An adversary is defined by the set of edges they can wiretap. 

- **Adversary(E_A)**: An adversary who has access to a subset of edges `E_A ⊆ E`.
- **Observation**: The adversary learns the local keys `{k_e | e ∈ E_A}` for all edges they have wiretapped.
- **Goal**: The adversary's goal is to determine the shared key `K` established between a non-wiretapped user pair.

---

## Mathematical Foundations

The correctness of the KRP rests on two fundamental properties: soundness and secrecy.

### Soundness Condition

**Soundness** ensures that both users in a pair successfully establish the *exact same* key.

> The protocol is **sound** for a user pair `(u1, u2)` if and only if there exists at least one path in the graph `G` connecting `u1` and `u2`.

If the users are in disconnected components of the graph, they cannot compute a key, and the protocol fails for that pair.

### Secrecy Condition

**Secrecy** ensures that the adversary cannot gain any information about the final shared key, even with knowledge of the wiretapped local keys.

Let's represent the graph's structure using linear algebra over the finite field `GF(2)`.

- Each edge `e_i` can be represented as a standard basis vector in an `|E|`-dimensional vector space.
- A path `P` is the sum of the vectors of the edges it contains.
- The adversary's knowledge can be represented as a subspace, `W`, spanned by the vectors of the wiretapped edges `E_A`.

> The key `K` is **information-theoretically secret** if the path vector `P` is linearly independent of the adversary's subspace `W`. Mathematically:

> **P ∉ span(E_A)**

In simpler terms, secrecy holds if the adversary cannot reconstruct the path's key by XORing together any combination of the keys they have observed. This is guaranteed if the path `P` does not form a cycle with any subset of the wiretapped edges `E_A`.

*Note: The current implementation in `krp.py` has a placeholder for the secrecy check (`secrecy = True`). A full verification would involve checking this linear independence condition.*

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

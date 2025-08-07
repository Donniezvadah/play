# Key Relay Protocol (KRP) Verification Framework

**Welcome to the Key Relay Protocol (KRP) Verification Framework Documentation and Pipeline**


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
   - [Algorithm Overview](#algorithm-overview)

---


# Key Relay Protocol (KRP) Graph Verification

This repository contains a Python implementation of the **Key Relay Protocol (KRP)** verification algorithm. Given a graph topology, a set of communicating user pairs, and potential wiretap sets, the algorithm determines whether secure key distribution is possible under the KRP model. The implementation is based on a rigorous linear algebraic formulation of KRP, and is intended as both a validator and an experimental tool for generating counterexamples that differentiate KRP from Secure Network Coding (SNC).

## 📘 Theoretical Background

The Key Relay Protocol allows secure key establishment between user pairs in a graph-based network using **edge-local random keys** and **node-local public announcements**. Each edge in the graph generates a random bit, and public information is formed from linear combinations of these bits. The protocol operates over the finite field $\mathbb{Z}_2$, and each piece of information (secret keys, public announcements, wiretap knowledge) is represented as a **vector in the vector space $\mathbb{Z}_2^{|E|}$**, where $|E|$ is the number of edges in the graph.

A key is considered **secure** if it is linearly independent of any adversarial knowledge, which includes both:
- The **primitive edge secrets** in the wiretap set $E_w$, and
- The set of all **public announcements** made during the protocol.
- The **adversarial knowledge** $E_A$.

Mathematically, for a key $k$, the condition for security is:
$$k\notin \text{span}\left( \{v_e \mid e \in E_w\} \cup P \right)$$




## Mathematical Foundations

The security of the KRP is analyzed using concepts from graph theory and linear algebra over the finite field of two elements, GF(2).

### Network Model

The communication network is modeled as a simple, undirected graph:

$$ G = (V, E) $$

- **V**: A set of nodes, representing users or network relays.
- **E**: A set of edges, representing secure communication links (e.g., QKD links) where local keys can be established.



### 🔐 The Protocol

The **Key Relay Protocol (KRP)** enables each user pair $(u_i, u_j)$ to establish a shared secret key by leveraging a combination of locally generated random bits on edges and public announcements made by intermediate relay nodes. The protocol operates in the finite field $\mathbb{Z}_2$, with all operations being linear combinations (bitwise XOR) over the space of edge secrets.

Each edge $e \in E$ independently generates a random bit $k_e \in \{0,1\}$, and this collection of bits forms the basis vectors of the ambient vector space $\mathbb{Z}_2^{|E|}$. These bits are distributed to the nodes incident to each edge. Each node $n_i \in V$ is then allowed to make a public announcement $p_i$, chosen as a linear combination of the random bits on its incident edges and the public information already broadcast:

$$p_i \in \text{span}( \{v_e \mid n_i \in e\} \cup P_{<i} )$$

where $v_e \in \mathbb{Z}_2^{|E|}$ is the incidence vector of edge $e$, and $P_{<i}$ denotes all previous public announcements.

A shared key $k \in \mathbb{Z}_2^{|E|}$ is then chosen as a linear combination of all primitive edge keys:

$$
k \in \text{span}(E)
$$

The design of the public announcements must guarantee that the key $k$ is reconstructible by both endpoints $u_i$ and $u_j$ of the user pair. That is, each user must be able to compute $k$ from their local edge information and the global public announcements:
But also making sure the adversary cannot compute the key $k$ from their wiretapped edges and the global public announcements.
There has to be Linear Independence between the key $k$ and the adversary's knowledge + Public Announcements.

$$k \in \text{span}(\{v_e \mid u_i \in e\} \cup P) \quad \text{and} \quad k \in \text{span}(\{v_e \mid u_j \in e\} \cup P)$$

To ensure information-theoretic secrecy against an adversary with access to a wiretap set $E_w \subseteq E$, the key $k$ must be linearly independent of all information accessible to the adversary. The adversary’s knowledge is captured by the subspace:

$$
A_{E_w} = \text{span}\left( \{v_e \mid e \in E_w\} \cup P \right)
$$

The protocol guarantees secrecy if and only if:

$$
k \notin A_{E_w} \quad \Leftrightarrow \quad \text{rank}(A_{E_w} \cup \{k\}) > \text{rank}(A_{E_w})
$$

This formulation avoids any dependency on specific paths between user pairs and instead defines keys and announcements purely as combinations of edge secrets. The flexibility of public announcements—subject to local constraints—defines the expressive power of KRP and forms the basis for comparing it with other protocols such as Secure Network Coding (SNC).
_________________________________________________________________________________________
_________________________________________________________________________________________

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

**Secrecy** ensures that the adversary gains zero information about the final shared key, $K$. This property is formally defined using concepts from information theory. Let $K$ be the random variable for the final key and $\mathbf{k}_{E_A}$ be the set of random variables for the local keys on the adversary's wiretapped edges, $E_A$.

Perfect secrecy is achieved if the mutual information between the key and the adversary's knowledge is zero:

$$ I(K; \mathbf{k}_{E_A}) = 0 $$

This implies that the adversary's observations provide no information about the key. In terms of entropy, this is equivalent to the conditional entropy of the key given the adversary's knowledge being equal to the key's total entropy:

$$ H(K | \mathbf{k}_{E_A}) = H(K) $$

Since each local key is an independent and uniformly random bit, the final key $K$ is also uniformly random, meaning $H(K) = 1$ bit. Thus, for perfect secrecy, the adversary must remain completely uncertain about the key.

This information-theoretic condition translates directly into a problem of **linear algebra over GF(2)**:

- The set of all edges $E$ forms a basis for a vector space of dimension $|E|$. Each edge $e_i$ corresponds to a basis vector.
- The user's path $P$ is represented as a **path vector**, $\vec{p}$, where the $i$-th component is 1 if $e_i \in P$ and 0 otherwise.
- The adversary's knowledge, $\mathbf{k}_{E_A}$, corresponds to a **subspace**, $W$, spanned by the basis vectors of the wiretapped edges in $E_A$.

Information-theoretic secrecy holds if and only if the path vector $\vec{p}$ is linearly independent of the adversary's subspace $W$. Mathematically:

$$ \vec{p} \notin \text{span}(E_A) $$

This is equivalent to checking if the rank of the adversary's subspace increases when the path vector is added to its basis:

$$ \text{rank}(\{\vec{e} | e \in E_A\} \cup \{\vec{p}\}) = \text{rank}(\{\vec{e} | e \in E_A\}) + 1 $$

If the rank does not increase, the path vector can be constructed from the adversary's known vectors, and the key is compromised. The implementation in `krp.py` uses a helper function, `_rank_gf2`, to perform this rank comparison over GF(2) and verify secrecy.

#### The Min-Cut Condition

As a critical prerequisite to the linear independence check, the set of edges controlled by the adversary must form a **minimum edge cut** (or *min-cut*) between the user pair. This condition ensures that the adversary has just enough access to potentially compromise the key, without having redundant information.

- **Edge Cut**: A set of edges is a cut between a user pair $(u_i, u_j)$ if removing those edges from the graph disconnects the users, meaning there is no longer a path between them.
- **Minimum Edge Cut**: An edge cut is a *minimum* cut if it has the smallest possible number of edges among all possible cuts that separate the users.

The framework verifies this condition using the `verify_min_cut_condition` function, which confirms two things:
1. That the adversary's set of wiretapped edges is indeed a cut.
2. That the size of this set is equal to the size of the minimum cut for the user pair.

Only if this condition is met does the simulation proceed to the final secrecy verification using linear algebra. This two-step process ensures a more rigorous and accurate security analysis.

---

## Framework Components

The project is divided into a simulation engine and a test suite.

### `krp.py` - The Simulation Engine

This file contains the core logic for the KRP simulation.

- **Data Structures**:
  - `UserPair`: Represents a user pair $(u_i, u_j)$ and stores their computed keys.
  - `Adversary`: Represents the adversary and stores the set of wiretapped edges.

- **Key Functions**:
  - `enumerate_all_graphs(n_nodes)`: Exhaustively generates all non-isomorphic undirected graphs for a given number of nodes. This is crucial for testing the protocol on all possible small network topologies.
  - `simulate_krp(G, user_pairs, adversary, ...)`: The main simulation function. It takes a graph, user pairs, and an adversary, then executes the KRP and returns a dictionary containing:
    - `sound`: A boolean indicating if the soundness property holds.
    - `secrecy`: A boolean indicating if the secrecy property holds (currently a placeholder).
    - `log`: A detailed log of the simulation steps.
____

## How to Run

### Running the Simulation

To run the main simulation script, which will enumerate all graphs for 3 nodes and simulate the KRP on each, execute the following command:

```bash
python3 krp.py #This is for linux 
python krp.py #This is for windows
```

The user will be asked between 1 Interactive or 2 Batch mode.

1 Interactive mode will allow the user to input their own graph and user pairs.
2 Batch mode will run the simulation on some predefine graph and user pairs.

## Interactive Mode

In interactive mode, the user will be asked to input the number of nodes and the number of user pairs.
Make use of instruction from the input requestions ie "Enter the number of nodes: " to input the number of nodes.


The script's `if __name__ == "__main__":` block is configured to run a default scenario.

### Running the Tests

To run the unit tests and verify the framework's components, execute:

```bash
python3 -m unittest test_krp.py
```

All tests should pass, confirming that the simulation engine behaves as expected under the tested conditions.

---

## 🧮 Algorithm Overview

The algorithm (detailed in [Algorithm Appendix A](#)) proceeds in five main stages:

1. **Graph Validation**:
   - Ensures the graph is connected.
   - Checks whether the min-cut condition holds for all user pairs.

2. **Key Generation**:
   - Generates random edge keys $r_e \in \mathbb{Z}_2$.
   - Distributes keys to incident nodes.

3. **Public Announcement Simulation**:
   - Nodes generate public information from local edge keys.
   - Ensures consistency and spans local information spaces.

4. **Security Verification**:
   - Checks if user keys are linearly independent of adversary's span.
   - Confirms whether both users in each pair can recover the key.

5. **Visualization**:
   - Plots the graph with user pairs and wiretap sets highlighted.

   ## Cloning the repository
   ```bash
   git clone https://github.com/Donniezvadah/play.git
   cd play
   ```




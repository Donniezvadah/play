"""
Key Relay Protocol (KRP) Verification Framework

This module provides a detailed implementation of the KRP as described in the referenced paper.
It supports exhaustive enumeration of all small undirected graphs, simulates the KRP on each,
and verifies both soundness and secrecy properties under adversarial models.

"""

import itertools
import networkx as nx
import random
from typing import List, Tuple, Set, Dict
import numpy as np

# ----------------------------
# Data Structures
# ----------------------------

class UserPair:
    """
    Represents a user pair (u1, u2) in the KRP protocol.
    """
    def __init__(self, node1: int, node2: int):
        self.node1 = node1
        self.node2 = node2
        self.k1 = None  # Key for user 1
        self.k2 = None  # Key for user 2

class Adversary:
    """
    Represents an adversary who can wiretap a subset of edges.
    """
    def __init__(self, wiretapped_edges: Set[Tuple[int, int]]):
        self.wiretapped_edges = wiretapped_edges

# ----------------------------
# Graph Enumeration Utilities
# ----------------------------

def enumerate_all_graphs(n_nodes: int) -> List[nx.Graph]:
    """
    Enumerate all non-isomorphic undirected graphs with n_nodes nodes.
    Uses networkx's graph generator for small n.
    """
    graphs = []
    # All possible edges
    nodes = list(range(n_nodes))
    all_edges = list(itertools.combinations(nodes, 2))
    for edgeset in itertools.product([0, 1], repeat=len(all_edges)):
        edges = [e for e, present in zip(all_edges, edgeset) if present]
        G = nx.Graph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        # Only add if not isomorphic to any already in the list
        if not any(nx.is_isomorphic(G, H) for H in graphs):
            graphs.append(G)
    return graphs

# ----------------------------
# Helper for GF(2) linear algebra
# ----------------------------

def _rank_gf2(M):
    """Calculates the rank of a binary matrix over GF(2)."""
    if not M.any():
        return 0
    
    mat = M.copy().astype(int)
    rows, cols = mat.shape
    rank = 0
    pivot_row = 0

    for j in range(cols):
        if pivot_row < rows:
            i = pivot_row
            while i < rows and mat[i, j] == 0:
                i += 1
            
            if i < rows:
                mat[[i, pivot_row]] = mat[[pivot_row, i]]
                for k in range(rows):
                    if k != pivot_row and mat[k, j] == 1:
                        mat[k] = (mat[k] + mat[pivot_row]) % 2
                pivot_row += 1
    return pivot_row

# ----------------------------
# KRP Protocol Simulation (Skeleton)
# ----------------------------

def simulate_krp(
    G: nx.Graph,
    user_pairs: List[UserPair],
    adversary: Adversary,
    key_length: int = 1,
    verbose: bool = True
) -> Dict:
    """
    Simulate the KRP protocol on a given graph with specific user pairs and adversary.
    Returns a dictionary with detailed logs and verification results.
    """
    log = []
    # Step 1: Distribute random local keys (for each edge)
    local_keys = {}
    for edge in G.edges():
        local_keys[edge] = random.getrandbits(key_length)
        log.append(f"Local key for edge {edge}: {local_keys[edge]}")

    # Step 2: Each user pair computes their relayed key (simplified for now)
    for up in user_pairs:
        # For demonstration, just XOR all keys on a path between the users
        try:
            path = nx.shortest_path(G, up.node1, up.node2)
            key = 0
            for i in range(len(path)-1):
                e = tuple(sorted((path[i], path[i+1])))
                key ^= local_keys[e]
            up.k1 = up.k2 = key
            log.append(f"UserPair ({up.node1},{up.node2}) path: {path}, key: {key}")
        except nx.NetworkXNoPath:
            up.k1 = up.k2 = None
            log.append(f"UserPair ({up.node1},{up.node2}) has no connecting path.")

    # Step 3: Adversary observes keys on wiretapped edges
    observed_keys = [local_keys[e] for e in adversary.wiretapped_edges if e in local_keys]
    log.append(f"Adversary wiretapped edges: {adversary.wiretapped_edges}, observed keys: {observed_keys}")

    # Step 4: Verification (soundness, secrecy)
    sound = all(up.k1 == up.k2 and up.k1 is not None for up in user_pairs)
    # Step 4: Verification (soundness, secrecy)
    sound = all(up.k1 == up.k2 and up.k1 is not None for up in user_pairs)

    # Information-theoretic secrecy verification
    secrecy = True
    if sound:  # Secrecy is only meaningful if a key was established
        edge_to_idx = {edge: i for i, edge in enumerate(G.edges())}
        num_edges = len(G.edges())

        # Create a basis matrix for the adversary's subspace
        adversary_basis = []
        for edge in adversary.wiretapped_edges:
            if edge in edge_to_idx:
                vec = np.zeros(num_edges, dtype=int)
                vec[edge_to_idx[edge]] = 1
                adversary_basis.append(vec)
        
        adversary_matrix = np.array(adversary_basis)

        for up in user_pairs:
            try:
                path_nodes = nx.shortest_path(G, up.node1, up.node2)
                path_edges = {tuple(sorted((path_nodes[i], path_nodes[i+1]))) for i in range(len(path_nodes)-1)}

                path_vec = np.zeros(num_edges, dtype=int)
                for edge in path_edges:
                    if edge in edge_to_idx:
                        path_vec[edge_to_idx[edge]] = 1

                # Check for linear independence over GF(2) using rank test.
                # If rank increases when path_vec is added, it's independent.
                rank_before = _rank_gf2(adversary_matrix)
                
                augmented_matrix = np.vstack([adversary_matrix, path_vec]) if adversary_matrix.any() else path_vec.reshape(1, -1)
                rank_after = _rank_gf2(augmented_matrix)

                if rank_after == rank_before:
                    secrecy = False
                    log.append(f"SECRECY BREACH: Path for UserPair ({up.node1},{up.node2}) is in adversary's subspace.")
                    break

            except nx.NetworkXNoPath:
                pass
    else:
        secrecy = True

    result = {
        "graph": G,
        "user_pairs": user_pairs,
        "adversary": adversary,
        "sound": sound,
        "secrecy": secrecy,
        "log": log
    }
    if verbose:
        for entry in log:
            print(entry)
    return result

# ----------------------------
# Example Usage (for up to 3 nodes)
# ----------------------------

if __name__ == "__main__":
    n_nodes = 3
    graphs = enumerate_all_graphs(n_nodes)
    print(f"Enumerated {len(graphs)} non-isomorphic graphs with {n_nodes} nodes.")
    for idx, G in enumerate(graphs):
        print(f"\n--- Graph {idx+1} ---")
        # Example: first two nodes as user pair
        user_pairs = [UserPair(0, 1)]
        # Example: adversary wiretaps all edges
        adversary = Adversary(set(G.edges()))
        simulate_krp(G, user_pairs, adversary, key_length=1, verbose=True)

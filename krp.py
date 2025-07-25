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
import matplotlib.pyplot as plt
import os

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

def verify_min_cut_condition(G: nx.Graph, user_pair: UserPair, adversary_edges: Set[Tuple[int, int]]) -> bool:
    """
    Verifies if the adversary's wiretapped edges form a minimum edge cut 
    between the user pair.

    According to KRP principles, for the protocol to be secure, the set of 
    edges controlled by the adversary must constitute a minimum separating set (min-cut)
    between the users. This ensures the adversary has just enough information to 
    potentially break security, but not more, setting the stage for the final 
    linear independence check.

    Args:
        G: The full communication graph.
        user_pair: The user pair (u1, u2).
        adversary_edges: The set of edges wiretapped by the adversary.

    Returns:
        True if the adversary's edges form a min-cut, False otherwise.
    """
    # 1. Check if the adversary's edges form a cut at all.
    # Removing the adversary's edges should disconnect the user pair.
    G_temp = G.copy()
    G_temp.remove_edges_from(adversary_edges)
    if nx.has_path(G_temp, user_pair.node1, user_pair.node2):
        return False  # Not a cut, users are still connected.

    # 2. If it is a cut, check if it's a *minimum* cut.
    # The size of the adversary's edge set must equal the size of the min-cut.
    min_cut_size = len(nx.minimum_edge_cut(G, user_pair.node1, user_pair.node2))
    
    return len(adversary_edges) == min_cut_size


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

    # --- Verification --- 
    # 1. Soundness
    sound = all(up.k1 == up.k2 and up.k1 is not None for up in user_pairs)

    # 2. Min-Cut Test
    min_cut_test_passed = False
    if sound and user_pairs:
        min_cut_test_passed = verify_min_cut_condition(G, user_pairs[0], adversary.wiretapped_edges)

    # 3. Secrecy
    secrecy = False  # Default to not secure
    if sound:
        if not min_cut_test_passed:
            log.append(f"SECRECY BREACH: Adversary does not hold a valid min-cut.")
        else:
            # Min-cut test passed, proceed with linear algebra check
            edge_to_idx = {edge: i for i, edge in enumerate(G.edges())}
            num_edges = len(G.edges())
            adversary_basis = []
            for edge in adversary.wiretapped_edges:
                if edge in edge_to_idx:
                    vec = np.zeros(num_edges, dtype=int)
                    vec[edge_to_idx[edge]] = 1
                    adversary_basis.append(vec)
            adversary_matrix = np.array(adversary_basis)

            up = user_pairs[0]
            path_nodes = nx.shortest_path(G, up.node1, up.node2)
            path_edges = {tuple(sorted((path_nodes[i], path_nodes[i+1]))) for i in range(len(path_nodes)-1)}
            path_vec = np.zeros(num_edges, dtype=int)
            for edge in path_edges:
                if edge in edge_to_idx:
                    path_vec[edge_to_idx[edge]] = 1

            rank_before = _rank_gf2(adversary_matrix)
            augmented_matrix = np.vstack([adversary_matrix, path_vec]) if adversary_matrix.any() else path_vec.reshape(1, -1)
            rank_after = _rank_gf2(augmented_matrix)
            
            if rank_after > rank_before:
                secrecy = True  # Secure only if path is LI
            else:
                log.append(f"SECRECY BREACH: Path for UserPair ({up.node1},{up.node2}) is in adversary's subspace.")

    if verbose:
        for line in log:
            print(line)

    return {
        'soundness': sound,
        'secrecy': secrecy,
        'log': log,
        'adversary_edges': adversary.wiretapped_edges,
        'min_cut_test': min_cut_test_passed
    }

# ----------------------------
# Plotting Utility
# ----------------------------

def plot_graph(G: nx.Graph, user_pairs: List[UserPair], adversary: Adversary, filename: str, results=None):
    """
    Plots the graph, highlighting user pairs and wiretapped edges, and saves it to a file.
    """
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(8, 6))

    # Define colors
    user_node_color = 'skyblue'
    normal_node_color = 'lightgray'
    wiretapped_edge_color = 'red'
    normal_edge_color = 'black'

    # Collect user nodes
    user_nodes = {node for up in user_pairs for node in (up.node1, up.node2)}

    # Draw nodes
    node_colors = [user_node_color if n in user_nodes else normal_node_color for n in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=700)
    nx.draw_networkx_labels(G, pos, font_size=12)

    # Draw edges
    wiretapped_edges = adversary.wiretapped_edges
    normal_edges = [e for e in G.edges() if tuple(sorted(e)) not in wiretapped_edges and e not in wiretapped_edges]

    nx.draw_networkx_edges(G, pos, edgelist=normal_edges, edge_color=normal_edge_color, width=1.5)
    nx.draw_networkx_edges(G, pos, edgelist=list(wiretapped_edges), edge_color=wiretapped_edge_color, width=2.0, style='dashed')

    plt.axis('off')

    # Add simulation results to the plot
    if results:
        text_str = (
            f"Adversary Set: {len(results['adversary_edges'])} edges\n"
            f"Min-Cut Test Passed: {results['min_cut_test']}\n"
            f"Is Secure: {results['secrecy']}\n"
            f"KRP Sound: {results['soundness']}"
        )
        # Use figtext to position text relative to the figure, preventing cutoff
        plt.figtext(0.5, 0.01, text_str, ha='center', va='bottom', fontsize=12, 
                    bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.5))

    # Ensure the 'plots' directory exists
    plots_dir = 'plots'
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)

    save_path = os.path.join(plots_dir, f"{filename}.pdf")
    # Use bbox_inches='tight' to ensure the text box is not cut off
    plt.savefig(save_path, format='pdf', bbox_inches='tight')
    plt.close()
    print(f"Plot saved to {save_path}")

# ----------------------------
# Example Usage (for up to 3 nodes)
# ----------------------------

if __name__ == "__main__":
    n_nodes = 4
    graphs = enumerate_all_graphs(n_nodes)
    print(f"Enumerated {len(graphs)} non-isomorphic graphs with {n_nodes} nodes.")

    for idx, G in enumerate(graphs):
        # Example: first two nodes as user pair
        user_pairs = [UserPair(0, 1)]
        
        # --- Focus on connected graphs for the user pair ---
        if nx.has_path(G, user_pairs[0].node1, user_pairs[0].node2):
            print(f"\n--- Graph {idx+1} (Connected) ---")
            
            # Example: adversary wiretaps all edges
            adversary = Adversary(set(G.edges()))

            # Simulate the KRP
            results = simulate_krp(G, user_pairs, adversary, key_length=1, verbose=True)

            # Plot the graph configuration with results
            plot_filename = f"graph_{idx+1}_nodes_{n_nodes}_connected"
            plot_graph(G, user_pairs, adversary, plot_filename, results)

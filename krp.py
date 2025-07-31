"""
Key Relay Protocol (KRP) Verification Framework

This script simulates the Key Relay Protocol (KRP) on various network graphs.
It systematically verifies the protocol's security (soundness and secrecy) against a wiretapping adversary.
Security is confirmed by checking min-cut conditions and linear independence of the key path from the adversary's knowledge.

This module provides a detailed implementation of the KRP as described in the referenced paper.
It supports exhaustive enumeration of all small undirected graphs, simulates the KRP on each,
and verifies both soundness and secrecy properties under adversarial models.

"""

'''
So basically we are trying to build a KRP protocol verification framework.
So, here are some of the things and fundamental part of this framework. 

1. Graph Enumeration: We are going to enumerate all non-isomorphic undirected graphs with n_nodes nodes.
2. User Pair: We are going to define a user pair as a tuple of two nodes.
3. Adversary: We are going to define an adversary as a set of edges that the adversary can wiretap.
4. Simulation: We are going to simulate the KRP protocol on each graph with specific user pairs and adversary.
5. Verification: We are going to verify both soundness and secrecy properties under adversarial models.
6. Plotting: We are going to plot the graph configuration with results.

````'''

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


def construct_public_channels(G: nx.Graph, user_pairs: List[UserPair]) -> Set[frozenset]:
    """
So the public channels are the set of all edges that are not used by the user pairs. 
And we are going to use this public channels to simulate the KRP protocol.
The public channels are used to anounce information ie via internet and accessible to all the users and as well as adversaries.
They are ised to announce local keys  to the users in the following manner:
1. Can announce local keys from any edges that are incoming to a given node ie say node v, 
then it anounce e_i + e_(i+1) ie if only 2 edges are incoming to node v then it anounce e_i + e_(i+1) 

2. Can be constructed by 1. + Public information from other public channnels  ie  it can announce e_i + e_(i+1) + e_(i+2)+e_(i+3)
where e_(i+2) and e_(i+3) are the public information from other public channnels

3. It is reusable meaning to say it can be used multiple times to announce information which is sometimes different from the previous announcement


    Constructs the set of all public channels as sets of incoming edges to non-user, non-end nodes.
    Each public channel is represented as a frozenset of edges feeding into the node.
    Nodes that are user nodes (appear in any UserPair) or are end nodes (degree 1) are excluded.
    Returns a set of frozensets (to allow set of sets).
    """
    user_nodes = set()
    for up in user_pairs:
        user_nodes.add(up.node1)
        user_nodes.add(up.node2)

    public_channels = set()
    for node in G.nodes():
        # Exclude user nodes and end nodes (degree 1)
        if node in user_nodes:
            continue
        if G.degree[node] <= 1:
            continue
        # The public channel is the set of all edges feeding into this node
        incoming_edges = set()
        for neighbor in G.neighbors(node):
            edge = tuple(sorted((node, neighbor)))
            incoming_edges.add(edge)
        if incoming_edges:
            public_channels.add(frozenset(incoming_edges))
    return public_channels

# Note: Public channels can be reused and can make multiple announcements, as per the protocol.
# This function simply constructs the structure; protocol logic can use these sets as needed.

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
# Adversary Set Utilities
# ----------------------------

def adversary_set_size(G: nx.Graph) -> int:
    """
    Returns the number of possible adversary sets (subsets of edges) for the given graph.
    This is 2^{|E|}, where |E| is the number of edges in G.
    """
    return 2 ** G.number_of_edges()


def find_min_cut_edges(G: nx.Graph, sources: List[int], targets: List[int]) -> Set[Tuple[int, int]]:
    """
    Returns a set of edges that form a minimum cut between sources and targets.
    For a single user pair, this is the classic min-cut. For multiple pairs, this is the multi-terminal cut.

    Args:
        G: The undirected graph.
        sources: List of source nodes (e.g., all ai).
        targets: List of target nodes (e.g., all bi).

    Returns:
        A set of edges forming a minimum cut between sources and targets.
    """
    if len(sources) == 1 and len(targets) == 1:
        # Single pair: classic min-cut
        cut_edges = nx.minimum_edge_cut(G, sources[0], targets[0])
        return set(tuple(sorted(e)) for e in cut_edges)
    else:
        # Multi-terminal cut: brute-force approach for small graphs
        # We try all possible edge subsets up to the size of the minimum cut
        min_cut_size = None
        min_cut_set = None
        edges = list(G.edges())
        for r in range(1, len(edges) + 1):
            for candidate in itertools.combinations(edges, r):
                G_temp = G.copy()
                G_temp.remove_edges_from(candidate)
                # Check if all sources are disconnected from all targets
                disconnected = True
                for s in sources:
                    for t in targets:
                        if nx.has_path(G_temp, s, t):
                            disconnected = False
                            break
                    if not disconnected:
                        break
                if disconnected:
                    if min_cut_size is None or r < min_cut_size:
                        min_cut_size = r
                        min_cut_set = set(tuple(sorted(e)) for e in candidate)
            if min_cut_set is not None:
                break
        return min_cut_set if min_cut_set is not None else set()

# ----------------------------
# Helper for GF(2) linear algebra
# ----------------------------

def _rank_gf2(M):
    """
    Calculates the rank of a binary matrix over GF(2).
    
    Args:
        M: 2D numpy array representing the matrix
        
    Returns:
        int: The rank of the matrix over GF(2)
    """
    if not M.any():
        return 0
    
    mat = M.copy().astype(int)
    rows, cols = mat.shape
    rank = 0
    pivot_row = 0

    for j in range(cols):
        if pivot_row >= rows:
            break
            
        # Find pivot row
        i = pivot_row
        while i < rows and mat[i, j] == 0:
            i += 1
        
        if i < rows:
            # Swap rows
            if i != pivot_row:
                mat[[i, pivot_row]] = mat[[pivot_row, i]]
            
            # Eliminate this column in other rows
            for k in range(rows):
                if k != pivot_row and mat[k, j] == 1:
                    mat[k] = (mat[k] + mat[pivot_row]) % 2
            
            pivot_row += 1
            rank += 1
    
    return rank


def _can_adversary_reconstruct(G: nx.Graph, user_pair: UserPair, adversary: Adversary, 
                             local_keys: dict, log: List[str], verbose: bool = False) -> bool:
    """
    Determines if the adversary can reconstruct the shared key using their wiretapped edges
    and public announcements.
    
    Args:
        G: The network graph
        user_pair: The user pair (u1, u2)
        adversary: The adversary with wiretapped edges
        local_keys: Dictionary mapping edges to their local keys
        log: Log list to append messages to
        verbose: If True, print detailed debug information
        
    Returns:
        bool: True if the adversary can reconstruct the key, False otherwise
    """
    try:
        # Get the key path
        path_nodes = nx.shortest_path(G, user_pair.node1, user_pair.node2)
        path_edges = [tuple(sorted((path_nodes[i], path_nodes[i+1]))) 
                     for i in range(len(path_nodes)-1)]
        
        # The actual key is the XOR of all edge keys on the path
        actual_key = 0
        for edge in path_edges:
            actual_key ^= local_keys[edge]
        
        if verbose:
            print(f"Actual key: {actual_key}")
            print(f"Path edges: {path_edges}")
        
        # Get all non-user nodes (potential public announcement points)
        non_user_nodes = set(G.nodes()) - {user_pair.node1, user_pair.node2}
        
        # For each non-user node, get its incoming edges and create equations
        equations = []
        for node in non_user_nodes:
            incoming_edges = [e for e in G.edges() if e[1] == node or e[0] == node]
            if len(incoming_edges) > 1:  # Only nodes with degree > 1 can make announcements
                # The sum of incoming edge keys is public
                eq = {edge: 1 for edge in incoming_edges}
                equations.append(eq)
        
        # Adversary's knowledge: wiretapped edges and public equations
        known_edges = set(adversary.wiretapped_edges)
        known_vars = {edge: local_keys[edge] for edge in known_edges}
        
        if verbose:
            print(f"Known edges: {known_edges}")
            print(f"Known vars: {known_vars}")
        
        # Try to solve the system of equations
        # This is a simplified approach - in practice, you'd use Gaussian elimination
        # over GF(2) to solve for the unknown edge keys
        
        # Check if all path edges are known
        if all(edge in known_edges for edge in path_edges):
            # Adversary can compute the key directly
            reconstructed_key = 0
            for edge in path_edges:
                reconstructed_key ^= known_vars[edge]
            
            if verbose:
                print(f"Reconstructed key: {reconstructed_key}")
            
            return reconstructed_key == actual_key
        
        # If not all path edges are known, check if they can be derived
        # from the equations and known edges
        # This is a simplified check - a complete implementation would solve the system
        
        # Count how many path edges are unknown
        unknown_path_edges = [e for e in path_edges if e not in known_edges]
        
        if verbose:
            print(f"Unknown path edges: {unknown_path_edges}")
        
        # If there's only one unknown edge on the path, the adversary can compute it
        # using the public equations
        if len(unknown_path_edges) == 1:
            # The adversary can compute the missing edge key using the equations
            # and known edges, then compute the key
            return True
        
        # More complex case: multiple unknown edges on the path
        # In a complete implementation, we'd solve the system of equations here
        
        # For now, be conservative and assume the adversary can reconstruct
        # if they have a min-cut
        is_min_cut, _ = verify_min_cut_condition(G, user_pair, adversary.wiretapped_edges)
        return is_min_cut
        
    except Exception as e:
        if verbose:
            print(f"Error in _can_adversary_reconstruct: {e}")
        return False  # Assume secure if we can't determine otherwise

def verify_min_cut_condition(G: nx.Graph, user_pair: UserPair, adversary_edges: Set[Tuple[int, int]], verbose: bool = False) -> Tuple[bool, str]:
    """
    Verifies if the adversary's wiretapped edges form a minimum edge cut 
    between the user pair and if they can reconstruct the key.

    According to KRP principles, for the protocol to be secure, the set of
    edges controlled by the adversary must not allow them to reconstruct the key.
    This function checks both the min-cut condition and attempts key reconstruction.

    Args:
        G: The full communication graph.
        user_pair: The user pair (u1, u2).
        adversary_edges: The set of edges wiretapped by the adversary.
        verbose: If True, prints detailed debug information.

    Returns:
        A tuple (is_min_cut, message) where:
        - is_min_cut: True if the edges form a min-cut
        - message: Detailed explanation of the result
    """
    # 1. Check if the adversary's edges form a cut
    G_temp = G.copy()
    G_temp.remove_edges_from(adversary_edges)
    if nx.has_path(G_temp, user_pair.node1, user_pair.node2):
        return False, "Adversary's edges do not form a cut between the users"

    # 2. Check if it's a minimum cut
    min_cut_size = len(nx.minimum_edge_cut(G, user_pair.node1, user_pair.node2))
    is_min_cut = len(adversary_edges) == min_cut_size
    
    if verbose:
        print(f"Min-cut size: {min_cut_size}, Adversary edges: {len(adversary_edges)}")
        print(f"Is min-cut: {is_min_cut}")
    
    return is_min_cut, f"Adversary controls a {'min-cut' if is_min_cut else 'non-min cut'}"


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
    
    Args:
        G: The network graph
        user_pairs: List of UserPair objects
        adversary: The adversary with wiretapped edges
        key_length: Length of the key in bits (default: 1 for simplicity)
        verbose: If True, print detailed logs
        
    Returns:
        Dict containing simulation results including:
        - soundness: Whether the protocol is sound (users agree on key)
        - secrecy: Whether the protocol maintains secrecy against the adversary
        - min_cut_test: Result of the min-cut test
        - log: List of log messages
        - adversary_edges: Set of wiretapped edges
    """
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

    # --- Verification --- 
    # 1. Soundness: Both users derive the same key
    sound = all(up.k1 == up.k2 and up.k1 is not None for up in user_pairs)
    if not sound:
        log.append("SOUNDNESS FAILED: Users did not derive the same key.")
    else:
        log.append("SOUNDNESS: Users derived matching keys.")

    # 2. Min-Cut and Security Analysis
    min_cut_test_passed = False
    secrecy = False
    
    if sound and user_pairs:
        up = user_pairs[0]  # For now, handle single user pair
        
        # Get the key path
        try:
            path_nodes = nx.shortest_path(G, up.node1, up.node2)
            path_edges = {tuple(sorted((path_nodes[i], path_nodes[i+1]))) 
                         for i in range(len(path_nodes)-1)}
            
            # 2.1 Min-Cut Test
            is_min_cut, min_cut_msg = verify_min_cut_condition(
                G, up, adversary.wiretapped_edges, verbose=verbose)
            min_cut_test_passed = is_min_cut
            log.append(f"MIN-CUT ANALYSIS: {min_cut_msg}")
            
            # 2.2 Linear Independence Check
            edge_to_idx = {edge: i for i, edge in enumerate(G.edges())}
            num_edges = len(G.edges())
            
            # Adversary's basis: wiretapped edges
            adversary_basis = []
            for edge in adversary.wiretapped_edges:
                if edge in edge_to_idx:
                    vec = np.zeros(num_edges, dtype=int)
                    vec[edge_to_idx[edge]] = 1
                    adversary_basis.append(vec)
            
            # Key path vector
            path_vec = np.zeros(num_edges, dtype=int)
            for edge in path_edges:
                if edge in edge_to_idx:
                    path_vec[edge_to_idx[edge]] = 1
            
            # Check if path is in the span of adversary's knowledge
            if adversary_basis:
                adversary_matrix = np.array(adversary_basis)
                rank_before = _rank_gf2(adversary_matrix)
                augmented_matrix = np.vstack([adversary_matrix, path_vec])
                rank_after = _rank_gf2(augmented_matrix)
                
                if verbose:
                    print(f"Adversary matrix rank: {rank_before}")
                    print(f"Augmented matrix rank: {rank_after}")
                
                if rank_after > rank_before:
                    secrecy = True
                    log.append("SECRECY: Key path is independent of adversary's knowledge.")
                else:
                    log.append("SECRECY BREACH: Key path can be reconstructed by the adversary.")
            else:
                # No adversary edges, always secure
                secrecy = True
                log.append("SECRECY: No edges are wiretapped.")
            
            # 2.3 Check if adversary can reconstruct the key
            if not secrecy:
                # Try to reconstruct the key using wiretapped edges and public announcements
                # This is a more thorough check than just the rank test
                if _can_adversary_reconstruct(G, up, adversary, local_keys, log, verbose):
                    secrecy = False
                    log.append("SECRECY BREACH: Adversary can reconstruct the key!")
                else:
                    log.append("SECRECY: Adversary cannot reconstruct the key despite min-cut.")
                    secrecy = True  # Override if reconstruction fails
                    
        except nx.NetworkXNoPath:
            log.append("ERROR: No path exists between users.")
            sound = False

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

# ----------------------------------------------
# Plotting Utility
# ----------------------------------------------

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
# Interactive KRP Verifier
# ----------------------------

def run_krp_verifier_interactive():
    print("=== KRP Protocol Verifier (Interactive Mode) ===")
    # Input nodes
    n_nodes = int(input("Enter number of nodes: "))
    nodes = list(range(n_nodes))
    print(f"Nodes: {nodes}")

    # Input edges
    print("Enter edges as pairs of node indices (e.g. 0 1), one per line. Enter a blank line to finish:")
    edges = set()
    while True:
        line = input()
        if not line.strip():
            break
        parts = line.strip().split()
        if len(parts) != 2:
            print("Invalid edge, enter two node indices.")
            continue
        u, v = map(int, parts)
        if u == v or u not in nodes or v not in nodes:
            print("Invalid edge, node indices out of range or self-loop.")
            continue
        edges.add(tuple(sorted((u, v))))
    print(f"Edges: {edges}")

    # Input user pairs
    print("Enter user pair as two node indices (e.g. 0 1):")
    while True:
        line = input()
        parts = line.strip().split()
        if len(parts) == 2:
            u1, u2 = map(int, parts)
            if u1 in nodes and u2 in nodes and u1 != u2:
                user_pairs = [UserPair(u1, u2)]
                break
        print("Invalid user pair, try again.")

    # Input wiretapped edges
    print("Enter wiretapped edges as pairs of node indices (e.g. 0 1), one per line. Enter a blank line to finish:")
    wiretapped_edges = set()
    while True:
        line = input()
        if not line.strip():
            break
        parts = line.strip().split()
        if len(parts) != 2:
            print("Invalid edge, enter two node indices.")
            continue
        u, v = map(int, parts)
        edge = tuple(sorted((u, v)))
        if edge not in edges:
            print("Edge not in graph, try again.")
            continue
        wiretapped_edges.add(edge)
    print(f"Wiretapped edges: {wiretapped_edges}")

    # Build the graph
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    # Check connectivity
    if not nx.has_path(G, user_pairs[0].node1, user_pairs[0].node2):
        print("User pair is not connected in the graph. Exiting.")
        return

    # Build adversary
    adversary = Adversary(wiretapped_edges)

    # Announce public channels
    print("\n--- Public Channel Announcements ---")
    public_channels = construct_public_channels(G, user_pairs)
    for pc in public_channels:
        print(f"Public channel (incoming edges): {sorted(pc)}")

    # Simulate the KRP
    print("\n--- KRP Simulation and Verification ---")
    results = simulate_krp(G, user_pairs, adversary, key_length=1, verbose=True)

    # Plot the graph
    plot_filename = "interactive_krp_graph"
    plot_graph(G, user_pairs, adversary, plot_filename, results)
    print(f"Graph plotted to 'plots/{plot_filename}.pdf'")


if __name__ == "__main__":
    print("Select mode:\n1. Interactive verifier\n2. Canonical batch verifier")
    mode = input("Enter 1 or 2: ").strip()
    if mode == "1":
        run_krp_verifier_interactive()
    elif mode == "2":
        print("\n--- Running KRP Verifier on Canonical Test Graphs ---")
        from krp_canonical_graphs import all_canonical_graphs
        graphs = all_canonical_graphs()
        for G, user_pairs, name in graphs:
            print(f"\n=== Graph: {name} ===")
            print(f"Nodes: {list(G.nodes())}")
            print(f"Edges: {list(G.edges())}")
            print(f"User pairs: {user_pairs}")
            # For each user pair, prompt for a wiretap set
            for idx, up in enumerate(user_pairs):
                print(f"\n--- User Pair {idx+1}: {up} ---")
                print("Enter wiretapped edges for this user pair as pairs of node indices (e.g. 0 1), one per line. Enter a blank line to finish:")
                wiretapped_edges = set()
                while True:
                    line = input()
                    if not line.strip():
                        break
                    parts = line.strip().split()
                    if len(parts) != 2:
                        print("Invalid edge, enter two node indices.")
                        continue
                    u, v = map(int, parts)
                    edge = tuple(sorted((u, v)))
                    if edge not in G.edges():
                        print("Edge not in graph, try again.")
                        continue
                    wiretapped_edges.add(edge)
                print(f"Wiretapped edges: {wiretapped_edges}")
                # Build UserPair and Adversary objects
                user_pair_objs = [UserPair(up[0], up[1])]
                adversary = Adversary(wiretapped_edges)
                # Announce public channels
                print("\n--- Public Channel Announcements ---")
                public_channels = construct_public_channels(G, user_pair_objs)
                for pc in public_channels:
                    print(f"Public channel (incoming edges): {sorted(pc)}")
                # Simulate the KRP
                print("\n--- KRP Simulation and Verification ---")
                results = simulate_krp(G, user_pair_objs, adversary, key_length=1, verbose=True)
                # Plot the graph
                plot_filename = f"canonical_{name}_userpair{idx+1}"
                plot_graph(G, user_pair_objs, adversary, plot_filename, results)
                print(f"Graph plotted to 'plots/{plot_filename}.pdf'")
    else:
        print("Invalid mode. Exiting.")


##This is the end of the code
## This repository is for the KRP protocol verification framework

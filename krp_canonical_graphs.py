"""
Defines canonical test graphs for KRP verification, including 1, 2, and 3 user pair examples.
Each function returns a tuple: (graph, user_pairs), where
- graph is a networkx.Graph object
- user_pairs is a list of (node1, node2) tuples
"""
import networkx as nx
from typing import List, Tuple

def triangle_graph_1pair():
    # Triangle: 3 nodes, 3 edges, 1 user pair
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2), (2, 0)])
    user_pairs = [(0, 2)]
    return G, user_pairs

def line_graph_1pair():
    # Line: 3 nodes, 2 edges, 1 user pair
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2)])
    user_pairs = [(0, 2)]
    return G, user_pairs

def star_graph_2pairs():
    # Star: 4 nodes, center 0, 2 user pairs
    G = nx.Graph()
    G.add_edges_from([(0, 1), (0, 2), (0, 3)])
    user_pairs = [(1, 2), (2, 3)]
    return G, user_pairs

def square_graph_2pairs():
    # Square: 4 nodes, 4 edges, 2 user pairs
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0)])
    user_pairs = [(0, 2), (1, 3)]
    return G, user_pairs

def double_star_3pairs():
    # Double star: 5 nodes, center 0, 3 user pairs
    G = nx.Graph()
    G.add_edges_from([(0, 1), (0, 2), (0, 3), (0, 4)])
    user_pairs = [(1, 2), (2, 3), (3, 4)]
    return G, user_pairs

def pentagon_graph_3pairs():
    # Pentagon: 5 nodes, 5 edges, 3 user pairs
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)])
    user_pairs = [(0, 2), (1, 3), (2, 4)]
    return G, user_pairs

def all_canonical_graphs():
    """
    Returns a list of (graph, user_pairs, name) for all canonical test graphs.
    """
    return [
        (triangle_graph_1pair()[0], triangle_graph_1pair()[1], "triangle_1pair"),
        (line_graph_1pair()[0], line_graph_1pair()[1], "line_1pair"),
        (star_graph_2pairs()[0], star_graph_2pairs()[1], "star_2pairs"),
        (square_graph_2pairs()[0], square_graph_2pairs()[1], "square_2pairs"),
        (double_star_3pairs()[0], double_star_3pairs()[1], "double_star_3pairs"),
        (pentagon_graph_3pairs()[0], pentagon_graph_3pairs()[1], "pentagon_3pairs"),
    ]

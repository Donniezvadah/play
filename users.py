import networkx as nx
import matplotlib.pyplot as plt
import os
from itertools import combinations

OUTPUT_DIR = 'user_pair_graphs'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def plot_graph(G, user_pairs, title, filename):
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_color='skyblue', edge_color='gray', node_size=600, font_size=10)
    # Highlight user pairs
    for u, v in user_pairs:
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], width=3, edge_color='red')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename))
    plt.close()

def generate_graphs(n_pairs):
    # Label users as u1, u2, ..., u2n
    users = [f'U{i+1}' for i in range(2 * n_pairs)]
    user_pairs = [(users[2*i], users[2*i+1]) for i in range(n_pairs)]
    # 1. Complete graph
    G_complete = nx.Graph()
    G_complete.add_nodes_from(users)
    G_complete.add_edges_from(combinations(users, 2))
    plot_graph(G_complete, user_pairs, f'Complete Graph ({n_pairs} pairs)', f'complete_{n_pairs}_pairs.png')
    # 2. Ring
    G_ring = nx.cycle_graph(users)
    plot_graph(G_ring, user_pairs, f'Ring Graph ({n_pairs} pairs)', f'ring_{n_pairs}_pairs.png')
    # 3. Star (centered at U1)
    # NetworkX star_graph(n) creates a star with n+1 nodes labeled 0..n
    G_star = nx.star_graph(len(users)-1)
    mapping = {i: users[i] for i in range(len(users))}
    G_star = nx.relabel_nodes(G_star, mapping)
    plot_graph(G_star, user_pairs, f'Star Graph ({n_pairs} pairs)', f'star_{n_pairs}_pairs.png')
    # 4. Line
    G_line = nx.path_graph(users)
    plot_graph(G_line, user_pairs, f'Line Graph ({n_pairs} pairs)', f'line_{n_pairs}_pairs.png')
    # 5. Butterfly (for n_pairs==2 only, classic)
    if n_pairs == 2:
        G_butterfly = nx.DiGraph()
        G_butterfly.add_nodes_from(['A', 'B', 'a', 'b', 'M'])
        G_butterfly.add_edges_from([('A', 'M'), ('B', 'M'), ('M', 'a'), ('M', 'b')])
        plot_graph(G_butterfly, [('A', 'a'), ('B', 'b')], 'Butterfly Network', 'butterfly_2_pairs.png')

def main():
    for n in range(1, 11):
        generate_graphs(n)
    print(f"All graphs generated and saved in '{OUTPUT_DIR}' directory.")

if __name__ == '__main__':
    main()


# ======================
# Graphillion ALL CASES DEMO for (A,B) <-> (a,b)
# ======================
from graphillion import GraphSet
import matplotlib.pyplot as plt
import networkx as nx

# Universe: all possible edges between (A, B) and (a, b)
left = ['A', 'B']
right = ['a', 'b']
universe = [(u, v) for u in left for v in right]

print("\n--- All possible bipartite subgraphs (undirected) ---")
GraphSet.set_universe(universe)
all_subgraphs = GraphSet()
for g in all_subgraphs:
    print(sorted(g))
print(f"Total: {len(all_subgraphs)} subgraphs (should be 16)")

# Visualize all subgraphs
for i, g in enumerate(all_subgraphs):
    G = nx.Graph()
    G.add_nodes_from(left + right)
    G.add_edges_from(g)
    plt.figure(figsize=(3,2))
    pos = {"A":(0,1), "B":(0,-1), "a":(2,1), "b":(2,-1)}
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='black')
    plt.title(f'Subgraph {i+1}')
    plt.tight_layout()
    plt.savefig(f'user_pair_graphs/graphillion_subgraph_{i+1}.png')
    plt.close()

print("\n--- All perfect matchings ---")
# Perfect matchings: select 2 edges, no shared node
from itertools import permutations
matchings = []
for e1 in universe:
    for e2 in universe:
        if e1 < e2 and len(set(e1+e2)) == 4:
            matchings.append([e1, e2])
for i, m in enumerate(matchings):
    print(f"Matching {i+1}: {m}")
    # Optionally visualize
    G = nx.Graph()
    G.add_nodes_from(left + right)
    G.add_edges_from(m)
    plt.figure(figsize=(3,2))
    pos = {"A":(0,1), "B":(0,-1), "a":(2,1), "b":(2,-1)}
    nx.draw(G, pos, with_labels=True, node_color='lightgreen', edge_color='red', width=2)
    plt.title(f'Matching {i+1}')
    plt.tight_layout()
    plt.savefig(f'user_pair_graphs/graphillion_matching_{i+1}.png')
    plt.close()
print(f"Total: {len(matchings)} perfect matchings (should be 6)")

print("\n--- All possible directed bipartite subgraphs ---")
directed_universe = [(u, v) for u in left for v in right]
GraphSet.set_universe(directed_universe)
directed_subgraphs = GraphSet()
for i, g in enumerate(directed_subgraphs):
    print(sorted(g))
    # Optionally visualize
    G = nx.DiGraph()
    G.add_nodes_from(left + right)
    G.add_edges_from(g)
    plt.figure(figsize=(3,2))
    pos = {"A":(0,1), "B":(0,-1), "a":(2,1), "b":(2,-1)}
    nx.draw(G, pos, with_labels=True, node_color='wheat', edge_color='blue', arrows=True)
    plt.title(f'Directed Subgraph {i+1}')
    plt.tight_layout()
    plt.savefig(f'user_pair_graphs/graphillion_directed_subgraph_{i+1}.png')
    plt.close()
print(f"Total: {len(directed_subgraphs)} directed subgraphs (should be 16)")

print("\n--- All paths from A to a (using only bipartite edges) ---")
GraphSet.set_universe(universe)
paths = GraphSet.paths('A', 'a')
for i, p in enumerate(paths):
    print(f"Path {i+1}: {p}")
    G = nx.Graph()
    G.add_nodes_from(left + right)
    G.add_edges_from(p)
    plt.figure(figsize=(3,2))
    pos = {"A":(0,1), "B":(0,-1), "a":(2,1), "b":(2,-1)}
    nx.draw(G, pos, with_labels=True, node_color='orange', edge_color='black')
    plt.title(f'Path A→a #{i+1}')
    plt.tight_layout()
    plt.savefig(f'user_pair_graphs/graphillion_path_Aa_{i+1}.png')
    plt.close()
print(f"Total: {len(paths)} paths from A to a")

print("\n--- All paths from B to b (using only bipartite edges) ---")
paths = GraphSet.paths('B', 'b')
for i, p in enumerate(paths):
    print(f"Path {i+1}: {p}")
    G = nx.Graph()
    G.add_nodes_from(left + right)
    G.add_edges_from(p)
    plt.figure(figsize=(3,2))
    pos = {"A":(0,1), "B":(0,-1), "a":(2,1), "b":(2,-1)}
    nx.draw(G, pos, with_labels=True, node_color='violet', edge_color='black')
    plt.title(f'Path B→b #{i+1}')
    plt.tight_layout()
    plt.savefig(f'user_pair_graphs/graphillion_path_Bb_{i+1}.png')
    plt.close()
print(f"Total: {len(paths)} paths from B to b")

# You can add more cases as needed for larger universes or more complex demonstrations.

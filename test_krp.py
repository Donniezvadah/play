import unittest
import networkx as nx
from krp import UserPair, Adversary, enumerate_all_graphs, simulate_krp

class TestKRP(unittest.TestCase):
    def test_enumerate_all_graphs_small(self):
        # For n=2, should be 2 graphs: empty, one edge
        graphs = enumerate_all_graphs(2)
        self.assertEqual(len(graphs), 2)
        # For n=3, should be 4 graphs (empty, one edge, path, triangle)
        graphs = enumerate_all_graphs(3)
        self.assertEqual(len(graphs), 4)

    def test_simulate_krp_sound(self):
        # Simple connected graph
        G = nx.Graph()
        G.add_edges_from([(0,1),(1,2)])
        user_pairs = [UserPair(0,2)]
        adversary = Adversary(set())  # No wiretapping
        result = simulate_krp(G, user_pairs, adversary, key_length=2, verbose=False)
        self.assertTrue(result['sound'])
        self.assertIsNotNone(user_pairs[0].k1)
        self.assertEqual(user_pairs[0].k1, user_pairs[0].k2)

    def test_simulate_krp_no_path(self):
        # Disconnected graph
        G = nx.Graph()
        G.add_nodes_from([0,1,2])
        G.add_edge(0,1)
        user_pairs = [UserPair(0,2)]
        adversary = Adversary(set())
        result = simulate_krp(G, user_pairs, adversary, key_length=2, verbose=False)
        self.assertFalse(result['sound'])
        self.assertIsNone(user_pairs[0].k1)

    def test_adversary_observation(self):
        G = nx.Graph()
        G.add_edges_from([(0,1),(1,2)])
        user_pairs = [UserPair(0,2)]
        # Adversary wiretaps all edges
        adversary = Adversary(set(G.edges()))
        result = simulate_krp(G, user_pairs, adversary, key_length=2, verbose=False)
        self.assertIn('observed keys', str(result['log']))

    def test_secrecy_holds(self):
        # Path is not in adversary's subspace
        G = nx.path_graph(4)  # 0-1-2-3
        user_pairs = [UserPair(0, 3)]
        adversary = Adversary({(1, 2)})  # Wiretap middle edge
        result = simulate_krp(G, user_pairs, adversary, verbose=False)
        self.assertTrue(result['sound'])
        self.assertTrue(result['secrecy'])

    def test_secrecy_breached(self):
        # Path is a subset of adversary's wiretapped edges
        G = nx.path_graph(3)  # 0-1-2
        user_pairs = [UserPair(0, 2)]
        adversary = Adversary({(0, 1), (1, 2)})  # Wiretap the whole path
        result = simulate_krp(G, user_pairs, adversary, verbose=False)
        self.assertTrue(result['sound'])
        self.assertFalse(result['secrecy'])

if __name__ == "__main__":
    unittest.main()

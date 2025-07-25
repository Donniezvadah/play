import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class ButterflyNetwork:
    def __init__(self):
        # Define the network structure
        self.stages = 2
        self.switches = [
            [{"input": [None, None], "output": [None, None]}],  # Stage 1
            [{"input": [None, None], "output": [None, None]}]   # Stage 2
        ]
        # Create a graph for visualization
        self.G = nx.DiGraph()
        
    def add_edges(self, edges, color='black', style='solid'):
        """Add edges to the graph with specified style"""
        for u, v in edges:
            self.G.add_edge(u, v, color=color, style=style)
    
    def configure_straight(self):
        """Configure the network in straight-through mode"""
        # Clear previous graph
        self.G.clear()
        
        # Add nodes
        self.G.add_nodes_from(['A', 'B', 'a', 'b'])
        
        # Add edges for the straight configuration
        edges = [('A', 'a'), ('B', 'b')]
        self.add_edges(edges, 'green', 'solid')
        
        # Add all possible edges in gray
        all_edges = [('A', 'a'), ('A', 'b'), ('B', 'a'), ('B', 'b')]
        self.add_edges(all_edges, 'lightgray', 'dashed')
        
        return {"A": "a", "B": "b"}
    
    def configure_cross(self):
        """Configure the network in cross mode"""
        # Clear previous graph
        self.G.clear()
        
        # Add nodes
        self.G.add_nodes_from(['A', 'B', 'a', 'b'])
        
        # Add edges for the cross configuration
        edges = [('A', 'b'), ('B', 'a')]
        self.add_edges(edges, 'blue', 'solid')
        
        # Add all possible edges in gray
        all_edges = [('A', 'a'), ('A', 'b'), ('B', 'a'), ('B', 'b')]
        self.add_edges(all_edges, 'lightgray', 'dashed')
        
        return {"A": "b", "B": "a"}
    
    def show_all_possible_connections(self, save_path=None):
        """Show all possible connections between senders and receivers"""
        # Create a new graph
        G = nx.DiGraph()
        
        # Add nodes
        senders = ['A', 'B']
        receivers = ['a', 'b']
        G.add_nodes_from(senders, bipartite=0)
        G.add_nodes_from(receivers, bipartite=1)
        
        # Add all possible edges
        for s in senders:
            for r in receivers:
                G.add_edge(s, r)
        
        # Draw the graph
        plt.figure(figsize=(8, 4))
        pos = {}
        pos.update((n, (1, i)) for i, n in enumerate(senders))  # Senders on the left
        pos.update((n, (2, i)) for i, n in enumerate(receivers))  # Receivers on the right
        
        nx.draw_networkx_nodes(G, pos, nodelist=senders, node_color='lightblue', node_size=1500)
        nx.draw_networkx_nodes(G, pos, nodelist=receivers, node_color='lightgreen', node_size=1500)
        nx.draw_networkx_edges(G, pos, edge_color='gray', width=2, arrows=True, arrowsize=20)
        nx.draw_networkx_labels(G, pos, font_size=16, font_weight='bold')
        
        plt.title('All Possible Connections', fontsize=14)
        plt.axis('off')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved all possible connections to {save_path}")
        else:
            plt.show()
        plt.close()

    def draw_network(self, title, save_path=None):
        """Draw the current network configuration"""
        if not self.G.edges():
            print("No edges to display. Configure the network first.")
            return
            
        plt.figure(figsize=(8, 4))
        
        # Position nodes
        pos = {
            'A': (0, 1),
            'B': (0, 0),
            'a': (2, 1),
            'b': (2, 0)
        }
        
        # Draw nodes
        nx.draw_networkx_nodes(self.G, pos, nodelist=['A', 'B'], 
                              node_color='lightblue', node_size=1500)
        nx.draw_networkx_nodes(self.G, pos, nodelist=['a', 'b'], 
                              node_color='lightgreen', node_size=1500)
        
        # Draw all possible edges in gray
        all_edges = [('A', 'a'), ('A', 'b'), ('B', 'a'), ('B', 'b')]
        nx.draw_networkx_edges(self.G, pos, edgelist=all_edges, 
                              edge_color='lightgray', style='dashed', 
                              width=1, arrows=True, arrowsize=15)
        
        # Draw active edges
        active_edges = [(u, v) for u, v, d in self.G.edges(data=True) 
                       if d.get('style') == 'solid']
        edge_color = 'red' if 'A' in dict(active_edges).get('A', '') else 'blue'
        nx.draw_networkx_edges(self.G, pos, edgelist=active_edges, 
                              edge_color=edge_color, width=2, 
                              arrows=True, arrowsize=20)
        
        # Draw labels
        nx.draw_networkx_labels(self.G, pos, font_size=16, font_weight='bold')
        
        plt.title(title, fontsize=14)
        plt.axis('off')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved configuration to {save_path}")
        else:
            plt.show()
        plt.close()

def main():
    import os
    
    # Create output directory if it doesn't exist
    output_dir = 'butterfly_network_configs'
    os.makedirs(output_dir, exist_ok=True)
    
    network = ButterflyNetwork()
    
    # Save all possible connections
    all_connections_path = os.path.join(output_dir, 'all_possible_connections.png')
    network.show_all_possible_connections(save_path=all_connections_path)
    
    # Save straight configuration
    print("\nSaving Straight Configuration (A<->a, B<->b):")
    network.configure_straight()
    straight_path = os.path.join(output_dir, 'straight_configuration.png')
    network.draw_network("Butterfly Network - Straight Configuration", 
                        save_path=straight_path)
    
    # Save cross configuration
    print("\nSaving Cross Configuration (A<->b, B<->a):")
    network.configure_cross()
    cross_path = os.path.join(output_dir, 'cross_configuration.png')
    network.draw_network("Butterfly Network - Cross Configuration",
                        save_path=cross_path)
    
    # Save individual connection configurations
    print("\nSaving all individual connection configurations:")
    configs = [
        ("A_to_a", [('A', 'a')]),
        ("A_to_b", [('A', 'b')]),
        ("B_to_a", [('B', 'a')]),
        ("B_to_b", [('B', 'b')])
    ]
    
    for name, edges in configs:
        network.G.clear()
        network.G.add_nodes_from(['A', 'B', 'a', 'b'])
        network.add_edges(edges, 'green', 'solid')
        config_path = os.path.join(output_dir, f'{name}.png')
        network.draw_network(f"Configuration: {name}", save_path=config_path)
    
    print("\nAll configurations have been saved to the 'butterfly_network_configs' directory.")

if __name__ == "__main__":
    main()

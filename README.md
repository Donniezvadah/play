# 🔑 Key Relay Protocol (KRP) Verification Framework

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python framework for simulating and verifying the **Key Relay Protocol (KRP)**, a cryptographic protocol designed to extend secure communication networks like Quantum Key Distribution (QKD) systems.

## 🌟 Features

- **Graph-based Simulation**: Model communication networks as undirected graphs
- **Security Verification**: Validate both soundness and secrecy properties
- **Adversary Modeling**: Test against various wiretapping scenarios
- **Interactive Mode**: Step-through simulation with detailed logging
- **Visualization**: Generate PDF visualizations of network topologies and security analyses

## 📚 Table of Contents

1. [Mathematical Foundations](#-mathematical-foundations)
   - [Network Model](#network-model)
   - [The Protocol](#the-protocol)
   - [Adversarial Model](#adversarial-model)
   - [Security Conditions](#security-conditions)
2. [Framework Architecture](#-framework-architecture)
   - [Core Components](#core-components)
   - [Data Structures](#data-structures)
3. [Getting Started](#-getting-started)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
4. [Usage](#-usage)
   - [Interactive Mode](#interactive-mode)
   - [Programmatic Usage](#programmatic-usage)
5. [Examples](#-examples)
6. [License](#-license)

---

## 🛠️ Usage

This section provides detailed instructions on how to use the KRP Verification Framework, including both interactive and programmatic approaches.

### Interactive Mode

The interactive mode provides a user-friendly command-line interface for running KRP simulations without writing any code.

#### Starting Interactive Mode

```bash
python krp.py
```

#### Interactive Mode Workflow

1. **Network Setup**:
   - Enter the number of nodes in your network
   - Define the edges between nodes as pairs of node indices (e.g., `0 1` for an edge between node 0 and node 1)
   - Enter a blank line when done adding edges

2. **User Pair Configuration**:
   - Specify the user pair by entering two node indices (e.g., `0 2` for users at nodes 0 and 2)

3. **Adversary Configuration**:
   - Define which edges the adversary can wiretap by entering edge pairs
   - Enter a blank line when done adding wiretapped edges

4. **Simulation Execution**:
   - The system will run the KRP simulation
   - Results will be displayed, including:
     - Soundness verification
     - Secrecy analysis
     - Visualization of the network

5. **Output**:
   - A PDF visualization will be saved in the `plots/` directory
   - Detailed logs will be displayed in the console

### Programmatic Usage

For more advanced usage, you can import the KRP framework into your Python code:

#### Basic Example

```python
import networkx as nx
from krp import UserPair, Adversary, simulate_krp

# Create a network graph
G = nx.Graph()
G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0)])  # 4-node ring

# Define user pair (nodes 0 and 2)
user_pairs = [UserPair(0, 2)]

# Define adversary (wiretapping one edge)
adversary = Adversary({(0, 1)})

# Run the simulation
results = simulate_krp(
    G, 
    user_pairs, 
    adversary,
    key_length=128,  # Key length in bits
    verbose=True     # Enable detailed logging
)

# View results
print(f"Soundness: {results['soundness']}")
print(f"Secrecy: {results['secrecy']}")
print(f"Min-cut test passed: {results['min_cut_test']}")

# Access the full simulation log
for log_entry in results['log']:
    print(log_entry)
```

#### Advanced Configuration

```python
import networkx as nx
from krp import UserPair, Adversary, simulate_krp, plot_graph
import matplotlib.pyplot as plt

# Create a more complex network
G = nx.Graph()
G.add_edges_from([
    (0, 1), (1, 2), (2, 3), (3, 0),  # Outer ring
    (1, 3), (0, 2),                   # Diagonals
    (4, 0), (4, 1), (4, 2), (4, 3)    # Central hub
])

# Define multiple user pairs
user_pairs = [
    UserPair(0, 2),  # Direct connection available
    UserPair(1, 3),  # Multiple paths available
    UserPair(0, 4)   # Through central hub
]

# Define adversary with multiple wiretapped edges
adversary = Adversary({
    (0, 1),  # Edge in the ring
    (4, 2),  # Edge to central hub
    (2, 3)   # Another edge in the ring
})

# Run simulation with custom parameters
results = simulate_krp(
    G,
    user_pairs,
    adversary,
    key_length=256,      # 256-bit keys
    max_paths=3,         # Maximum number of paths to consider
    allow_multipath=True # Allow multiple paths for key establishment
)

# Generate and display the network plot
plot_graph(G, user_pairs, adversary, "advanced_example", results)
plt.show()

# Analyze results for each user pair
for i, up in enumerate(user_pairs):
    print(f"\n--- User Pair {i+1}: ({up.node1}, {up.node2}) ---")
    print(f"Path used: {results['paths'][i]}")
    print(f"Key established: {results['keys'][i]}")
    print(f"Security status: {'Secure' if results['secrecy'][i] else 'Insecure'}")
```

### Key Functions and Classes

#### `UserPair(node1, node2)`
Represents a pair of users who want to establish a shared key.

**Parameters**:
- `node1`: First node ID (integer)
- `node2`: Second node ID (integer)

#### `Adversary(wiretapped_edges)`
Represents an adversary that can wiretap specific edges in the network.

**Parameters**:
- `wiretapped_edges`: Set of tuples representing edges the adversary can observe

#### `simulate_krp(graph, user_pairs, adversary, **kwargs)`
Main function to simulate the KRP protocol.

**Parameters**:
- `graph`: NetworkX Graph object representing the network
- `user_pairs`: List of UserPair objects
- `adversary`: Adversary object
- `key_length`: Length of the generated keys in bits (default: 1)
- `verbose`: Whether to print detailed logs (default: False)
- `max_paths`: Maximum number of paths to consider (default: 1)
- `allow_multipath`: Whether to allow multiple paths for key establishment (default: False)

**Returns**:
A dictionary containing:
- `soundness`: Boolean indicating if the protocol is sound
- `secrecy`: Boolean indicating if the protocol maintains secrecy
- `min_cut_test`: Boolean indicating if the min-cut condition is satisfied
- `log`: List of log messages
- `paths`: List of paths used for each user pair
- `keys`: List of established keys for each user pair

### Visualization

The framework includes built-in visualization capabilities:

```python
from krp import plot_graph
import matplotlib.pyplot as plt

# After running a simulation...
plot_graph(
    G,                          # NetworkX graph
    user_pairs,                 # List of UserPair objects
    adversary,                  # Adversary object
    "network_visualization",    # Output filename (without extension)
    results,                    # Simulation results
    show_plot=True,             # Whether to display the plot
    save_pdf=True,              # Whether to save as PDF
    dpi=300                     # Image resolution
)
plt.show()
```

### Batch Processing

To run multiple simulations with different parameters:

```python
from itertools import product
import networkx as nx
from krp import UserPair, Adversary, simulate_krp

# Define different network sizes and adversary strengths
network_sizes = [4, 5, 6]
adversary_ratios = [0.2, 0.4, 0.6]

results = []

for n, ratio in product(network_sizes, adversary_ratios):
    # Create a complete graph
    G = nx.complete_graph(n)
    
    # Create user pair (first and last node)
    user_pairs = [UserPair(0, n-1)]
    
    # Calculate number of edges to wiretap
    num_edges = len(G.edges())
    num_wiretapped = max(1, int(num_edges * ratio))
    
    # Select edges to wiretap
    wiretapped_edges = set(list(G.edges())[:num_wiretapped])
    adversary = Adversary(wiretapped_edges)
    
    # Run simulation
    result = simulate_krp(G, user_pairs, adversary)
    
    # Store results
    results.append({
        'network_size': n,
        'adversary_ratio': ratio,
        'num_edges': num_edges,
        'num_wiretapped': num_wiretapped,
        'sound': result['soundness'],
        'secure': result['secrecy']
    })

# Analyze results...
```

### Performance Considerations

1. **Graph Size**:
   - The framework is optimized for small to medium-sized graphs (up to ~100 nodes)
   - For larger graphs, consider using sparse matrix representations

2. **Key Length**:
   - Longer keys provide better security but increase computation time
   - Default key length is 1 bit for demonstration purposes

3. **Parallel Processing**:
   - For batch simulations, you can use Python's `multiprocessing` module:
     ```python
     from multiprocessing import Pool
     
     def run_simulation(params):
         # Unpack parameters
         n, ratio = params
         # ... simulation code ...
         return result
     
     # Create parameter combinations
     parameters = [(n, r) for n in network_sizes for r in adversary_ratios]
     
     # Run in parallel
     with Pool() as pool:
         results = pool.map(run_simulation, parameters)
     ```

### Next Steps

- Explore the [Examples](#-examples) section for more advanced use cases
- Check the [API Documentation](docs/api.md) for detailed function references
- Contribute to the project by submitting issues or pull requests

---

## 📊 Examples

This section provides practical examples demonstrating how to use the KRP Verification Framework for different network topologies and security analyses.

### Example 1: Ring Network Analysis

Analyze a simple ring network with 4 nodes and evaluate its security against different adversary configurations.

```python
import networkx as nx
import matplotlib.pyplot as plt
from krp import UserPair, Adversary, simulate_krp, plot_graph

# Create a 4-node ring network
G = nx.cycle_graph(4)

# Define user pair (diametrically opposite nodes)
user_pairs = [UserPair(0, 2)]

# Test different adversary configurations
adversary_configs = [
    ("No Adversary", set()),
    ("One Edge Compromised", {(0, 1)}),
    ("Two Edges Compromised", {(0, 1), (1, 2)}),
    ("Three Edges Compromised", {(0, 1), (1, 2), (2, 3)})
]

# Run simulations
for name, wiretapped_edges in adversary_configs:
    print(f"\n--- {name} ---")
    adversary = Adversary(wiretapped_edges)
    
    # Run simulation
    results = simulate_krp(G, user_pairs, adversary, verbose=True)
    
    # Plot the network
    plot_graph(
        G, 
        user_pairs, 
        adversary, 
        f"ring_4node_{name.lower().replace(' ', '_')}",
        results,
        show_plot=False,
        save_pdf=True
    )
    
    print(f"Soundness: {results['soundness']}")
    print(f"Secrecy: {results['secrecy']}")
    print(f"Min-cut test: {results['min_cut_test']}")
```

### Example 2: Star Network with Multiple User Pairs

Evaluate a star network with a central hub and multiple user pairs, analyzing the impact of hub compromise.

```python
import networkx as nx
from krp import UserPair, Adversary, simulate_krp

# Create a star network with 5 nodes (1 hub + 4 leaves)
G = nx.star_graph(4)

# Define multiple user pairs
user_pairs = [
    UserPair(1, 3),  # Leaf to leaf
    UserPair(0, 2),  # Another leaf to leaf
    UserPair(0, 4)   # Leaf to another leaf
]

# Test with and without hub compromise
scenarios = [
    ("Hub Not Compromised", {1, 2, 3, 4}),  # Only leaves are users
    ("Hub Compromised", {0, 1, 2, 3, 4})    # Hub is also a user
]

for scenario_name, user_nodes in scenarios:
    print(f"\n--- {scenario_name} ---")
    
    # Define which nodes are users (all except the hub)
    user_pairs = [UserPair(u, v) for u in user_nodes 
                 for v in user_nodes if u < v]
    
    # Adversary wiretaps edges to hub
    adversary = Adversary({(0, i) for i in range(1, 5)})
    
    # Run simulation
    results = simulate_krp(G, user_pairs, adversary, verbose=False)
    
    # Analyze results
    secure_pairs = sum(1 for s in results['secrecy'] if s)
    total_pairs = len(results['secrecy'])
    
    print(f"Secure pairs: {secure_pairs}/{total_pairs} "
          f"({secure_pairs/total_pairs:.1%})")
```

### Example 3: Grid Network with Random Adversary

Analyze a 3x3 grid network with random adversary placement to evaluate security properties statistically.

```python
import random
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from krp import UserPair, Adversary, simulate_krp

# Create a 3x3 grid
G = nx.grid_2d_graph(3, 3)
# Convert node labels from (x,y) to integers
G = nx.convert_node_labels_to_integers(G)

# Number of simulations
num_simulations = 100

# Storage for results
results = []

for _ in range(num_simulations):
    # Randomly select user pair
    nodes = list(G.nodes())
    u, v = random.sample(nodes, 2)
    user_pairs = [UserPair(u, v)]
    
    # Randomly select edges to compromise (1-3 edges)
    all_edges = list(G.edges())
    num_compromised = random.randint(1, 3)
    compromised_edges = random.sample(all_edges, num_compromised)
    
    adversary = Adversary(compromised_edges)
    
    # Run simulation
    result = simulate_krp(G, user_pairs, adversary, verbose=False)
    
    # Store results
    results.append({
        'user_pair': (u, v),
        'num_compromised': num_compromised,
        'compromised_edges': compromised_edges,
        'secure': result['secrecy'][0],
        'path': result['paths'][0]
    })

# Analyze results
secure_count = sum(1 for r in results if r['secure'])
print(f"Secure communications: {secure_count}/{num_simulations} "
      f"({secure_count/num_simulations:.1%})")

# Plot security vs number of compromised edges
compromise_counts = {}
for r in results:
    count = r['num_compromised']
    if count not in compromise_counts:
        compromise_counts[count] = {'total': 0, 'secure': 0}
    compromise_counts[count]['total'] += 1
    if r['secure']:
        compromise_counts[count]['secure'] += 1

# Print security statistics
print("\nSecurity by number of compromised edges:")
for count in sorted(compromise_counts.keys()):
    stats = compromise_counts[count]
    print(f"{count} edges: {stats['secure']}/{stats['total']} "
          f"({stats['secure']/stats['total']:.1%}) secure")
```

### Example 4: Comparing Network Topologies

Compare the security of different network topologies (ring, star, grid, complete) under the same adversary model.

```python
import networkx as nx
import matplotlib.pyplot as plt
from krp import UserPair, Adversary, simulate_krp

# Network configurations
networks = {
    "4-node Ring": nx.cycle_graph(4),
    "4-node Star": nx.star_graph(3),
    "2x2 Grid": nx.grid_2d_graph(2, 2),
    "4-node Complete": nx.complete_graph(4)
}

# Convert node labels to integers for consistency
for name in networks:
    if name != "4-node Star":  # star_graph already has integer labels
        networks[name] = nx.convert_node_labels_to_integers(networks[name])

# Define user pairs (diametrically opposite nodes where applicable)
user_pairs_config = {
    "4-node Ring": [UserPair(0, 2)],
    "4-node Star": [UserPair(1, 3)],
    "2x2 Grid": [UserPair(0, 3)],
    "4-node Complete": [UserPair(0, 2)]
}

# Define adversary (compromising 1 or 2 edges)
adversary_configs = [
    ("1 Edge Compromised", 1),
    ("2 Edges Compromised", 2)
]

# Run simulations
results = {}

for name, G in networks.items():
    results[name] = {}
    
    for adv_name, num_edges in adversary_configs:
        # Select edges to compromise
        edges = list(G.edges())
        compromised_edges = edges[:num_edges]
        adversary = Adversary(compromised_edges)
        
        # Run simulation
        result = simulate_krp(
            G, 
            user_pairs_config[name], 
            adversary,
            verbose=False
        )
        
        results[name][adv_name] = {
            'secure': result['secrecy'][0],
            'path': result['paths'][0],
            'compromised_edges': compromised_edges
        }

# Display results
print("Security Analysis of Different Network Topologies\n" + "="*50)
print(f"{'Network':<20} {'Adversary':<20} {'Status':<15} Path")
print("-" * 60)

for name in networks:
    print(f"\n{name}:")
    for adv_name in adversary_configs:
        adv_name = adv_name[0]
        result = results[name][adv_name]
        status = "SECURE" if result['secure'] else "COMPROMISED"
        print(f"  {adv_name:<20} {status:<15} {result['path']}")

# Visualize the networks
plt.figure(figsize=(15, 10))
for i, (name, G) in enumerate(networks.items(), 1):
    plt.subplot(2, 2, i)
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500)
    plt.title(name)

plt.tight_layout()
plt.savefig('network_topologies_comparison.png', dpi=300)
plt.show()
```

### Example 5: Visualizing Security Analysis

Create a comprehensive visualization of the security analysis for a given network.

```python
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import numpy as np
from krp import UserPair, Adversary, simulate_krp

def visualize_security_analysis(G, user_pairs, adversary, filename):
    # Run simulation
    results = simulate_krp(G, user_pairs, adversary, verbose=False)
    
    # Create figure
    plt.figure(figsize=(12, 8))
    
    # Position nodes using spring layout
    pos = nx.spring_layout(G, seed=42)
    
    # Draw the network
    node_colors = ['lightgreen' if node in [up.node1 for up in user_pairs] + 
                               [up.node2 for up in user_pairs] 
                  else 'lightblue' for node in G.nodes()]
    
    # Draw nodes and edges
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color=node_colors)
    
    # Draw regular edges
    regular_edges = [e for e in G.edges() 
                    if e not in adversary.wiretapped_edges and 
                       (e[1], e[0]) not in adversary.wiretapped_edges]
    nx.draw_networkx_edges(G, pos, edgelist=regular_edges, width=2)
    
    # Draw compromised edges in red
    nx.draw_networkx_edges(G, pos, edgelist=adversary.wiretapped_edges, 
                          edge_color='red', width=2, style='dashed')
    
    # Draw node labels
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')
    
    # Draw edge labels (local keys)
    edge_labels = {}
    for i, (u, v) in enumerate(G.edges()):
        edge_labels[(u, v)] = f"k{i+1}"
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
    
    # Highlight the used path
    for path in results['paths']:
        path_edges = list(zip(path[:-1], path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, 
                              edge_color='green', width=3, alpha=0.5)
    
    # Add title with security information
    plt.title(
        f"Security Analysis\n"
        f"Soundness: {results['soundness']} | "
        f"Secrecy: {results['secrecy']} | "
        f"Min-Cut Test: {results['min_cut_test']}",
        fontsize=14
    )
    
    # Add legend
    plt.legend(
        handles=[
            plt.Line2D([0], [0], color='black', lw=2, label='Secure Edge'),
            plt.Line2D([0], [0], color='red', lw=2, linestyle='--', 
                      label='Compromised Edge'),
            plt.Line2D([0], [0], color='green', lw=3, alpha=0.5, 
                      label='Key Path')
        ],
        loc='upper right'
    )
    
    # Save and show
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(f"{filename}.png", dpi=300, bbox_inches='tight')
    plt.show()

# Example usage
G = nx.cycle_graph(5)
user_pairs = [UserPair(0, 2)]
adversary = Adversary({(0, 1), (1, 2)})

visualize_security_analysis(G, user_pairs, adversary, "security_analysis_example")
```

### Example 6: Batch Processing for Research

Run multiple simulations with different parameters for research purposes and analyze the results.

```python
import pandas as pd
import networkx as nx
import numpy as np
from tqdm import tqdm
from krp import UserPair, Adversary, simulate_krp

def run_experiment(network_generator, num_nodes, num_trials=100):
    """Run multiple trials with random user pairs and adversary configurations."""
    results = []
    
    for _ in tqdm(range(num_trials), desc=f"Nodes: {num_nodes}"):
        # Generate network
        G = network_generator(num_nodes)
        nodes = list(G.nodes())
        
        # Random user pair
        u, v = np.random.choice(nodes, 2, replace=False)
        user_pairs = [UserPair(u, v)]
        
        # Random adversary (compromising 10-30% of edges)
        edges = list(G.edges())
        num_compromised = max(1, int(len(edges) * np.random.uniform(0.1, 0.3)))
        compromised_edges = [edges[i] for i in np.random.choice(
            len(edges), num_compromised, replace=False)]
        adversary = Adversary(compromised_edges)
        
        # Run simulation
        result = simulate_krp(G, user_pairs, adversary, verbose=False)
        
        # Store results
        results.append({
            'num_nodes': num_nodes,
            'num_edges': len(edges),
            'num_compromised': num_compromised,
            'path_length': len(result['paths'][0])-1 if result['paths'] else 0,
            'secure': result['secrecy'][0] if result['secrecy'] else False,
            'min_cut': result['min_cut_test']
        })
    
    return pd.DataFrame(results)

# Define network generators
def generate_ring(n):
    return nx.cycle_graph(n)

def generate_star(n):
    return nx.star_graph(n-1)

def generate_grid(n):
    # Find factors closest to square
    factors = []
    for i in range(1, int(np.sqrt(n)) + 1):
        if n % i == 0:
            factors.append((i, n // i))
    rows, cols = max(factors, key=lambda x: min(x))
    return nx.grid_2d_graph(rows, cols)

# Run experiments
network_types = {
    'ring': generate_ring,
    'star': generate_star,
    'grid': generate_grid
}

all_results = []

for name, generator in network_types.items():
    print(f"\n=== {name.upper()} NETWORK ===")
    for n in [5, 10, 15, 20]:  # Different network sizes
        df = run_experiment(generator, n, num_trials=50)
        df['network_type'] = name
        all_results.append(df)

# Combine all results
results_df = pd.concat(all_results, ignore_index=True)

# Analyze results
print("\n=== SECURITY ANALYSIS ===")
security_by_type = results_df.groupby(['network_type', 'num_nodes'])['secure'].mean().unstack()
print("\nSecurity Rate by Network Type and Size:")
print(security_by_type)

# Plot results
import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
sns.set_theme(style="whitegrid")

# Plot security rate vs network size
plt.subplot(1, 2, 1)
sns.lineplot(data=results_df, x='num_nodes', y='secure', 
             hue='network_type', marker='o')
plt.title('Security Rate vs Network Size')
plt.xlabel('Number of Nodes')
plt.ylabel('Security Rate')
plt.ylim(0, 1.1)

# Plot security vs number of compromised edges
plt.subplot(1, 2, 2)
sns.lineplot(data=results_df, x='num_compromised', y='secure',
             hue='network_type', marker='o', ci=None)
plt.title('Security vs Number of Compromised Edges')
plt.xlabel('Number of Compromised Edges')
plt.ylabel('Security Rate')
plt.ylim(0, 1.1)

plt.tight_layout()
plt.savefig('security_analysis_results.png', dpi=300)
plt.show()
```

## 🚀 Getting Started

This section will guide you through setting up the KRP Verification Framework on your system.

### Prerequisites

Before installing the KRP Verification Framework, ensure you have the following installed on your system:

- **Python 3.7 or higher**
  - Check your Python version:
    ```bash
    python --version
    # or
    python3 --version
    ```
  - Download Python: [https://www.python.org/downloads/](https://www.python.org/downloads/)

- **pip** (Python package manager)
  - Usually comes with Python installation
  - Verify installation:
    ```bash
    pip --version
    ```

- **Git** (for cloning the repository)
  - Download Git: [https://git-scm.com/downloads](https://git-scm.com/downloads)

### Installation

Follow these steps to install the KRP Verification Framework:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/krp-verification-framework.git
   cd krp-verification-framework
   ```

2. **Create a virtual environment (recommended)**:
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   The main dependencies are:
   - networkx: For graph operations
   - numpy: For numerical computations
   - matplotlib: For visualization
   - pytest: For running tests

4. **Verify the installation**:
   ```bash
   python -m pytest tests/
   ```
   All tests should pass to confirm a successful installation.

### Quick Start

1. **Run the interactive mode**:
   ```bash
   python krp.py
   ```
   Follow the on-screen prompts to define your network, user pairs, and adversary configuration.

2. **Or use the framework programmatically**:
   ```python
   import networkx as nx
   from krp import UserPair, Adversary, simulate_krp
   
   # Create a simple 4-node network
   G = nx.cycle_graph(4)
   
   # Define user pair (nodes 0 and 2)
   user_pairs = [UserPair(0, 2)]
   
   # Define adversary (wiretapping one edge)
   adversary = Adversary({(0, 1)})
   
   # Run the simulation
   results = simulate_krp(G, user_pairs, adversary, verbose=True)
   
   # View results
   print(f"Soundness: {results['soundness']}")
   print(f"Secrecy: {results['secrecy']}")
   ```

### Troubleshooting

If you encounter any issues during installation:

1. **Permission Errors**:
   - On Linux/macOS, try using `sudo` or install with the `--user` flag:
     ```bash
     pip install --user -r requirements.txt
     ```

2. **Missing Dependencies**:
   - Ensure all system dependencies are installed:
     - On Ubuntu/Debian:
       ```bash
       sudo apt-get install python3-dev python3-pip python3-venv
       ```
     - On macOS (with Homebrew):
       ```bash
       brew install python
       ```

3. **Virtual Environment Issues**:
   - If the virtual environment doesn't activate, try:
     ```bash
     # On Windows
     .\venv\Scripts\activate.ps1  # PowerShell
     .\venv\Scripts\activate.bat  # Command Prompt
     
     # On macOS/Linux
     source venv/bin/activate
     ```

### Next Steps

- Explore the [Usage](#-usage) section for detailed examples
- Check out the [Examples](#-examples) for ready-to-run code snippets
- Read the [API Documentation](docs/api.md) for detailed function references

---

## 🧮 Mathematical Foundations

The security of the KRP is rigorously analyzed using concepts from graph theory and linear algebra over the finite field of two elements, GF(2). This section provides a formal treatment of the theoretical underpinnings.

### Network Model

The communication network is formally represented as an undirected graph:

$$ G = (V, E) $$

Where:
- $V$: A finite set of nodes (vertices), representing users or network relays
- $E \subseteq \{\{u, v\} \mid u, v \in V, u \neq v\}$: A set of undirected edges, representing secure communication links

#### Graph Properties
- **Simple Graph**: No self-loops or multiple edges between the same pair of nodes
- **Undirected**: Edges have no direction, representing bidirectional communication
- **Connected**: There exists a path between any two nodes (for meaningful key exchange)
- **Weighted**: Optional edge weights can represent channel capacities or reliability metrics

#### Node Types
- **User Nodes**: Endpoints that wish to establish a shared secret
- **Relay Nodes**: Intermediate nodes that assist in key distribution
- **Adversary Nodes**: Compromised nodes under the adversary's control

### The Protocol

The KRP enables a user pair $(u_1, u_2)$ to establish a shared secret key by leveraging the network's relay nodes through the following steps:

#### 1. Network Initialization
- **Graph Construction**: The network topology is established as an undirected graph $G = (V, E)$
- **Node Identification**: Each node is assigned a unique identifier (typically an integer)
- **Edge Establishment**: Secure communication links are established between connected nodes

#### 2. Local Key Generation
For each edge $e \in E$ in the network:
- A random local key $k_e \in \{0, 1\}$ is generated
- The key is securely shared between the two nodes connected by $e$
- All operations are performed in GF(2), where addition corresponds to the XOR operation

#### 3. Path Selection
- A path $P$ is selected between the user pair $(u_1, u_2)$
- The path is a sequence of edges: $P = \{e_1, e_2, ..., e_m\}$
- Multiple path selection strategies are supported:
  - Shortest path (default)
  - Random path
  - Maximum disjoint paths (for multi-path variants)

#### 4. Shared Key Computation
The final shared key $K$ is computed by XORing the local keys along the selected path:

$$K = \bigoplus_{e \in P} k_e = k_{e_1} \oplus k_{e_2} \oplus ... \oplus k_{e_m}$$

#### 5. Key Confirmation (Optional)
- Users can perform a key confirmation step to verify they've derived the same key
- This is implemented using a hash-based message authentication code (HMAC)

#### 6. Key Update
- The protocol supports periodic key updates for forward secrecy
- Local keys can be refreshed using a one-way function

#### Example: 4-Node Network
```
       k1
   0 ------ 1
   |       / \
k2 |    k3   k4
   |  /       \
   2 --------- 3
       k5
```
- **Users**: 0 and 3
- **Path**: 0 → 1 → 3
- **Key Computation**: $K = k_1 \oplus k_4$
- **Alternative Path**: 0 → 2 → 1 → 3
- **Same Key**: $K = k_2 \oplus k_3 \oplus k_4$ (due to properties of XOR)

### Adversarial Model

The framework models a powerful but realistic adversary that can wiretap a subset of the network's communication links. This models real-world scenarios where an attacker may have compromised certain communication channels.

#### Adversary Capabilities

- **Wiretapping**: The adversary can observe all communication (local keys) on a chosen set of edges $E_A \subseteq E$
- **Passive**: The adversary is assumed to be passive (eavesdropping only) and cannot modify or inject messages
- **Computationally Unbounded**: The adversary has unlimited computational resources
- **Knowledge**: For each wiretapped edge $e \in E_A$, the adversary learns the local key $k_e$
- **Goal**: To determine the shared secret key $K$ established between a non-compromised user pair

#### Adversary Types

1. **Edge Adversary**
   - Can wiretap up to $t$ edges of their choice
   - Models physical compromise of specific communication links
   - Most common model in the KRP framework

2. **Node Adversary**
   - Can compromise all edges incident to up to $t$ nodes
   - Models complete compromise of specific network nodes
   - Can be simulated using appropriate edge selections

#### Example: Adversary in a 4-Node Network
```
       k1 (wiretapped)
   0 ====== 1
   |       / \
k2 |    k3   k4 (wiretapped)
   |  /       \
   2 --------- 3
       k5
```
- **Adversary's Knowledge**: $k_1$, $k_4$
- **User Pair**: (0, 3)
- **Path Used**: 0 → 1 → 3
- **Key**: $K = k_1 \oplus k_4$
- **Adversary's Success**: Can compute $K$ directly from known keys
- **Security Breach**: Adversary can derive the shared key

#### Security Parameters

- **Adversary Threshold**: The maximum number of edges the adversary can wiretap before security is compromised
- **Key Space**: The size of the key space (2 for binary keys)
- **Success Probability**: The probability an adversary can guess the key (ideally $1/2$ for perfect secrecy)

### Security Conditions

The KRP's security is evaluated based on two fundamental properties: soundness and secrecy. These properties ensure the protocol's correctness and security against eavesdropping adversaries.

#### 1. Soundness

**Definition**: A KRP is *sound* if legitimate users successfully establish identical shared keys when a path exists between them.

**Formal Definition**:
For a user pair $(u_1, u_2)$ in graph $G$:
- If $u_1$ and $u_2$ are in the same connected component, they must agree on the same key $K$.
- If they are in different components, key establishment must fail explicitly.

**Verification**:
1. Check if a path exists between $u_1$ and $u_2$ using BFS/DFS.
2. If a path exists, verify both users compute the same key $K$.
3. If no path exists, ensure key establishment fails gracefully.

**Example**:
```
   0 -- 1 -- 2    3 -- 4
```
- Users (0,2): Sound (path exists: 0-1-2)
- Users (0,4): Unsound (no path exists)

#### 2. Secrecy

**Definition**: A KRP provides *perfect secrecy* if the adversary gains no information about the established key $K$ from observing the wiretapped edges.

**Information-Theoretic Definition**:
For a key $K$ and adversary's knowledge $\mathbf{k}_{E_A}$:

Perfect secrecy is achieved when:
$$ I(K; \mathbf{k}_{E_A}) = 0 $$

Equivalently, in terms of entropy:
$$ H(K | \mathbf{k}_{E_A}) = H(K) $$

**Linear Algebra Interpretation**:
The secrecy condition can be translated to linear algebra over GF(2):

1. **Vector Space Representation**:
   - Each edge $e_i \in E$ corresponds to a basis vector $\vec{e_i}$
   - The path $P$ is represented as a vector $\vec{p} = \sum_{e_i \in P} \vec{e_i}$
   - The adversary's knowledge spans a subspace $W = \text{span}(\{\vec{e} | e \in E_A\})$

2. **Secrecy Condition**:
   $$ \vec{p} \notin W $$
   
   This means the path vector cannot be expressed as a linear combination of the adversary's observed edges.

**Example**:
Consider a 3-node path: 0 -- 1 -- 2
- Users: (0,2)
- Path: 0-1-2
- Path vector: $\vec{p} = (1, 1)$ (for edges (0,1) and (1,2))
- If adversary taps edge (0,1): $W = \text{span}\{(1,0)\}$
  - $\vec{p} = (1,1) \notin W$ → Secure
- If adversary taps both edges: $W = \text{span}\{(1,0), (0,1)\}$
  - $\vec{p} = (1,1) = 1\cdot(1,0) + 1\cdot(0,1) \in W$ → Insecure

#### 3. The Min-Cut Condition

**Definition**: A necessary condition for secrecy is that the adversary's wiretapped edges must form a *minimum edge cut* between the user pair.

**Formal Definition**:
For a user pair $(u_1, u_2)$ and adversary edges $E_A$:
1. $E_A$ must be a cut between $u_1$ and $u_2$
2. $|E_A|$ must equal the size of the minimum cut between $u_1$ and $u_2$

**Verification**:
1. Check if $E_A$ is a cut (removing $E_A$ disconnects $u_1$ and $u_2$)
2. Verify no smaller cut exists between $u_1$ and $u_2$

**Example**:
```
   0 -- 1 -- 2 -- 3
    \     \  /
     \     X
      \  /  \
       4 ----5
```
- Min-cut between 0 and 3 is 2 (edges (1,2) and (2,3))
- Adversary with $E_A = \{(1,2), (2,3)\}$ satisfies min-cut condition
- Adversary with $E_A = \{(0,1), (1,4)\}$ does not satisfy (not a min-cut)

#### 4. Security Verification Algorithm

The complete security verification in `krp.py` follows these steps:

1. **Soundness Check**:
   - Verify a path exists between the user pair
   - Ensure both users compute the same key

2. **Min-Cut Verification**:
   - Check if adversary's edges form a cut
   - Verify it's a minimum cut

3. **Linear Independence Check**:
   - Construct the adversary's subspace $W$
   - Check if path vector $\vec{p}$ is linearly independent of $W$
   - This is done using Gaussian elimination over GF(2)

4. **Security Decision**:
   - If soundness fails → Protocol is broken
   - If min-cut condition fails → Protocol is insecure
   - If path vector is in adversary's subspace → Protocol is insecure
   - Otherwise → Protocol is secure

This comprehensive verification ensures the KRP meets both correctness and security requirements under the given adversarial model.

Only if this condition is met does the simulation proceed to the final secrecy verification using linear algebra. This two-step process ensures a more rigorous and accurate security analysis.

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
python3 krp.py #This will run on  linux 

python ./krp.py #This will run on windows
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





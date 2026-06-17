#!/usr/bin/env python3
"""Load JSON-LD files into RDF graph and visualize"""

import json
import sys
from pathlib import Path
from collections import defaultdict

try:
    from rdflib import Graph
    import networkx as nx
    import matplotlib.pyplot as plt
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "rdflib", "networkx", "matplotlib"])
    from rdflib import Graph
    import networkx as nx
    import matplotlib.pyplot as plt

BASE_DIR = Path("/Users/daniel.ellis/WIPwork/Essential-Model-Documentation")

def find_jsonld_files(start_path=BASE_DIR):
    jsonld_files = list(start_path.rglob("*.jsonld"))
    return sorted(jsonld_files)

def load_jsonld(file_path):
    g = Graph()
    try:
        g.parse(str(file_path), format="json-ld")
        return g
    except Exception as e:
        print(f"Error: {e}")
        return Graph()

def main():
    print("\n" + "=" * 70)
    print("JSON-LD to RDF Graph Visualizer")
    print("=" * 70)
    
    print("\n[1/4] Finding JSON-LD files...")
    jsonld_files = find_jsonld_files()
    
    if not jsonld_files:
        print("❌ No JSON-LD files found!")
        return
    
    print(f"Found {len(jsonld_files)} JSON-LD files:")
    for f in jsonld_files:
        print(f"  - {f.relative_to(BASE_DIR)}")
    
    print("\n[2/4] Loading JSON-LD into RDF graph...")
    g = Graph()
    
    for jsonld_file in jsonld_files:
        try:
            sub_graph = load_jsonld(jsonld_file)
            for s, p, o in sub_graph:
                g.add((s, p, o))
            print(f"  ✓ Loaded {jsonld_file.name} ({len(sub_graph)} triples)")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\n  Total triples: {len(g)}")
    
    print("\n[3/4] Creating network graph...")
    nx_graph = nx.DiGraph()
    
    for s, p, o in g:
        s_str = str(s)
        o_str = str(o)
        p_str = str(p).split("#")[-1].split("/")[-1]
        
        nx_graph.add_node(s_str)
        nx_graph.add_node(o_str)
        nx_graph.add_edge(s_str, o_str, label=p_str)
    
    print(f"  Nodes: {nx_graph.number_of_nodes()}")
    print(f"  Edges: {nx_graph.number_of_edges()}")
    
    print("\n[4/4] Creating visualization...")
    
    # Static high-quality PNG
    fig, ax = plt.subplots(figsize=(20, 16))
    pos = nx.spring_layout(nx_graph, k=3, iterations=100, seed=42)
    
    # Draw edges
    nx.draw_networkx_edges(nx_graph, pos, 
                          edge_color="gray", 
                          arrows=True, 
                          arrowsize=12, 
                          alpha=0.4,
                          arrowstyle="-|>",
                          connectionstyle="arc3,rad=0.1",
                          width=1.5,
                          ax=ax)
    
    # Draw nodes
    nx.draw_networkx_nodes(nx_graph, pos, 
                          node_color="lightblue", 
                          node_size=300, 
                          alpha=0.95,
                          edgecolors="darkblue",
                          linewidths=2,
                          ax=ax)
    
    # Draw labels
    labels = {n: n.split("#")[-1].split("/")[-1][:20] for n in nx_graph.nodes()}
    nx.draw_networkx_labels(nx_graph, pos, labels, font_size=6, font_weight="bold", ax=ax)
    
    ax.set_title("RDF Graph from JSON-LD Files", fontsize=18, fontweight="bold", pad=20)
    ax.axis("off")
    plt.tight_layout()
    
    output_png = BASE_DIR / "rdf_graph.png"
    plt.savefig(str(output_png), dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"  ✓ Saved visualization: {output_png}")
    
    # Create interactive HTML manually
    html_content = generate_interactive_html(nx_graph, BASE_DIR)
    output_html = BASE_DIR / "rdf_visualization.html"
    output_html.write_text(html_content)
    print(f"  ✓ Saved interactive HTML: {output_html}")
    
    # Statistics
    print("\n" + "=" * 70)
    print("STATISTICS")
    print("=" * 70)
    print(f"Total triples: {len(g)}")
    print(f"Unique subjects: {len(set(s for s, _, _ in g))}")
    print(f"Unique predicates: {len(set(p for _, p, _ in g))}")
    print(f"Unique objects: {len(set(o for _, _, o in g))}")
    
    pred_counts = defaultdict(int)
    for _, p, _ in g:
        pred_str = str(p).split("#")[-1].split("/")[-1]
        pred_counts[pred_str] += 1
    
    print("\nTop predicates:")
    for pred, count in sorted(pred_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  {pred}: {count}")
    
    print("\n" + "=" * 70)
    print("✅ COMPLETE")
    print("=" * 70)
    print(f"\nOpen in browser: {output_html}")

def generate_interactive_html(nx_graph, base_dir):
    """Generate simple interactive HTML using vis.js"""
    nodes_json = json.dumps([{"id": str(i), "label": node.split("#")[-1].split("/")[-1][:20], "title": node}
                             for i, node in enumerate(nx_graph.nodes())], indent=2)
    
    node_map = {node: str(i) for i, node in enumerate(nx_graph.nodes())}
    edges_json = json.dumps([{"from": node_map[s], "to": node_map[o], "label": data.get("label", "")}
                             for s, o, data in nx_graph.edges(data=True)], indent=2)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>RDF Graph Visualization</title>
    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.css" rel="stylesheet" type="text/css" />
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; }}
        #network {{ width: 100%; height: 100vh; border: 1px solid lightgray; }}
        #info {{ position: absolute; top: 10px; left: 10px; background: white; padding: 10px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <div id="info">
        <h3>RDF Graph Visualization</h3>
        <p>Nodes: {nx_graph.number_of_nodes()}</p>
        <p>Edges: {nx_graph.number_of_edges()}</p>
        <p>Drag to move | Scroll to zoom</p>
    </div>
    <div id="network"></div>
    <script type="text/javascript">
        var nodes = new vis.DataSet({nodes_json});
        var edges = new vis.DataSet({edges_json});
        var container = document.getElementById('network');
        var data = {{ nodes: nodes, edges: edges }};
        var options = {{
            physics: {{ enabled: true, forceAtlas2Based: {{ gravitationalConstant: -50, centralGravity: 0.01, springLength: 300 }}, maxVelocity: 50 }},
            nodes: {{ font: {{ size: 12 }} }},
            edges: {{ arrows: 'to', font: {{ size: 10 }} }}
        }};
        var network = new vis.Network(container, data, options);
    </script>
</body>
</html>"""
    return html

if __name__ == "__main__":
    main()

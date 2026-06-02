#!/usr/bin/env python3
"""RDF Graph Builder from esgvoc _graph.json Files"""

import json
import sys
from pathlib import Path
from collections import defaultdict

try:
    from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS
    from rdflib.namespace import SKOS
except ImportError:
    print("Installing rdflib...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rdflib"])
    from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS
    from rdflib.namespace import SKOS

BASE_DIR = Path("/Users/daniel.ellis/WIPwork/Essential-Model-Documentation")
ESGVOC = Namespace("http://example.org/esgvoc/")

def to_uri(uri_str):
    """Convert string to URIRef."""
    if uri_str.startswith("http://") or uri_str.startswith("https://"):
        return URIRef(uri_str)
    return ESGVOC[uri_str]

def extract_uris(obj):
    """Recursively extract all URIs from an object."""
    uris = set()
    def recurse(item):
        if isinstance(item, dict):
            if "@id" in item:
                uris.add(item["@id"])
            if "@type" in item:
                t = item["@type"]
                if isinstance(t, str):
                    uris.add(t)
                elif isinstance(t, list):
                    uris.update(t)
            for v in item.values():
                recurse(v)
        elif isinstance(item, list):
            for i in item:
                recurse(i)
    recurse(obj)
    return uris

def load_graph_json(file_path):
    """Load a _graph.json file."""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

def main():
    """Main execution."""
    print("\n" + "=" * 70)
    print("RDF GRAPH BUILDER FROM ESGVOC")
    print("=" * 70)
    
    print("\n[1/6] Finding _graph.json files...")
    graph_files = sorted(BASE_DIR.rglob("_graph.json"))
    print(f"Found {len(graph_files)} files:")
    for f in graph_files:
        print(f"  - {f.relative_to(BASE_DIR)}")
    
    print("\n[2/6] Loading _graph.json files...")
    graph_data = {}
    for gf in graph_files:
        folder_name = gf.parent.name
        data = load_graph_json(gf)
        graph_data[folder_name] = data
        print(f"  ✓ Loaded {folder_name}")
    
    print("\n[3/6] Extracting URIs...")
    all_uris = set()
    for folder_name, data in graph_data.items():
        uris = extract_uris(data)
        all_uris.update(uris)
        print(f"  {folder_name}: {len(uris)} URIs")
    print(f"  Total unique URIs: {len(all_uris)}")
    
    print("\n[4/6] Building RDF graph...")
    g = Graph()
    g.bind("esgvoc", ESGVOC)
    g.bind("skos", SKOS)
    
    triples = 0
    for folder_name, data in graph_data.items():
        folder_uri = ESGVOC[folder_name]
        g.add((folder_uri, RDF.type, SKOS.Collection))
        g.add((folder_uri, RDFS.label, Literal(folder_name)))
        triples += 2
        
        if "contents" in data and isinstance(data["contents"], list):
            for item in data["contents"]:
                if isinstance(item, dict) and "@id" in item:
                    item_uri = to_uri(item["@id"])
                    g.add((folder_uri, SKOS.member, item_uri))
                    triples += 1
                    
                    if "@type" in item:
                        types = item["@type"] if isinstance(item["@type"], list) else [item["@type"]]
                        for t in types:
                            g.add((item_uri, RDF.type, to_uri(t)))
                            triples += 1
    
    print(f"  Added {triples} triples")
    print(f"  Graph contains {len(g)} triples")
    
    print("\n[5/6] Graph statistics...")
    subjects = len(set(s for s, _, _ in g))
    predicates = len(set(p for _, p, _ in g))
    objects = len(set(o for _, _, o in g))
    
    print(f"  Total triples: {len(g)}")
    print(f"  Unique subjects: {subjects}")
    print(f"  Unique predicates: {predicates}")
    print(f"  Unique objects: {objects}")
    
    pred_counts = defaultdict(int)
    for _, p, _ in g:
        pred_counts[str(p)] += 1
    
    print("\n  Triples by predicate:")
    for pred, count in sorted(pred_counts.items(), key=lambda x: -x[1]):
        print(f"    {pred}: {count}")
    
    print("\n[6/6] Exporting graph...")
    output_dir = BASE_DIR / "rdf_output"
    output_dir.mkdir(exist_ok=True)
    
    formats = [("turtle", "ttl"), ("xml", "rdf"), ("json-ld", "jsonld"), ("nt", "nt")]
    for fmt, ext in formats:
        output_file = output_dir / f"combined_graph.{ext}"
        g.serialize(destination=str(output_file), format=fmt)
        print(f"  ✓ Exported to {output_file}")
    
    print("\n" + "=" * 70)
    print("✅ COMPLETE")
    print("=" * 70)
    print(f"\nOutput directory: {output_dir}")
    print(f"Files:")
    for f in output_dir.glob("combined_graph.*"):
        size = f.stat().st_size / 1024
        print(f"  - {f.name} ({size:.1f} KB)")

if __name__ == "__main__":
    main()

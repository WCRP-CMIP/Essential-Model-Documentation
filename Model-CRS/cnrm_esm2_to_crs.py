"""Convert JSON-LD model structure to CRS"""
import json

def json_to_crs(model_data):
    """
    Convert JSON-LD model data to CRS string
    
    Args:
        model_data: dict with 'embedded_components', 'coupling_groups'
    
    Returns:
        str: CRS string
    """
    # Map full names to codes
    code_map = {
        'atmosphere': 'A',
        'ocean': 'O',
        'land-surface': 'L',
        'atmospheric-chemistry': 'Ac',
        'aerosol': 'Ae',
        'land-ice': 'Li',
        'ocean-biogeochemistry': 'Ob',
        'sea-ice': 'Si'
    }
    
    # Extract embeddings
    embeddings = []
    if 'embedded_components' in model_data:
        for pair in model_data['embedded_components']:
            child = code_map.get(pair[0])
            parent = code_map.get(pair[1])
            if child and parent:
                embeddings.append((child, parent))
    
    # Extract couplings
    couplings = set()
    if 'coupling_groups' in model_data:
        for group in model_data['coupling_groups']:
            codes = [code_map.get(c) for c in group if code_map.get(c)]
            # All pairs in the group are coupled
            for i, c1 in enumerate(codes):
                for c2 in codes[i+1:]:
                    couplings.add(tuple(sorted([c1, c2])))
    
    return embeddings, couplings


def generate_crs(embeddings, couplings):
    """Generate canonical CRS from embeddings and couplings"""
    couplings = {tuple(sorted(pair)) for pair in couplings}
    parent_map = {c: p for c, p in embeddings}
    realms = sorted(set([c for c,p in embeddings] + [p for c,p in embeddings] + [x for pair in couplings for x in pair]))
    
    def chain(r):
        for c, p in embeddings:
            if p == r:
                return f"{r}[{chain(c)}]"
        return r
    
    roots = [r for r in realms if r not in parent_map]
    realm_couple = {r: set() for r in realms}
    for r1, r2 in couplings:
        if realms.index(r1) < realms.index(r2):
            realm_couple[r1].add(r2)
        else:
            realm_couple[r2].add(r1)
    
    parts = []
    for r in roots:
        s = chain(r)
        couples = sorted(realm_couple[r])
        if couples:
            s += f"({','.join(couples)})"
        parts.append(s)
    
    return ''.join(parts)


if __name__ == "__main__":
    # CNRM-ESM2-1e example
    model_data = {
        "embedding_components": [
            ["atmosphere", "aerosol"],
            ["atmosphere", "atmospheric-chemistry"],
            ["ocean", "sea-ice"],
            ["ocean", "ocean-biogeochemistry"]
        ],
        "coupling_groups": [
            ["atmosphere", "land-surface", "ocean"]
        ],
        "dynamic_components": [
            "aerosol", "atmosphere", "atmospheric-chemistry",
            "land-surface", "ocean", "ocean-biogeochemistry", "sea-ice"
        ]
    }
    
    emb, coup = json_to_crs(model_data)
    crs = generate_crs(emb, coup)
    print(f"Model: CNRM-ESM2-1e")
    print(f"CRS: {crs}")
    print(f"Embeddings: {emb}")
    print(f"Couplings: {coup}")

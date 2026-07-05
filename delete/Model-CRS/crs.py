"""CRS Parser - Canonical Realm String"""

def parse(s):
    """Parse CRS string: A[Ac[Ae]](O,L) -> (embeddings, couplings)"""
    emb = []
    coup = set()
    i = 0
    
    def read_code():
        nonlocal i
        if i >= len(s) or not s[i].isupper():
            return None
        code = s[i]
        i += 1
        if i < len(s) and s[i].islower():
            code += s[i]
            i += 1
        return code
    
    def parse_embed(parent):
        nonlocal i
        if i < len(s) and s[i] == '[':
            i += 1
            child = read_code()
            if child:
                emb.append((child, parent))
                parse_embed(child)
            if i < len(s) and s[i] == ']':
                i += 1
    
    def parse_couple(realm):
        nonlocal i
        if i < len(s) and s[i] == '(':
            i += 1
            while i < len(s) and s[i] != ')':
                if s[i] == ',':
                    i += 1
                else:
                    c = read_code()
                    if c:
                        coup.add(tuple(sorted([realm, c])))
                    else:
                        i += 1
            if i < len(s):
                i += 1
    
    while i < len(s):
        code = read_code()
        if code:
            parse_embed(code)
            parse_couple(code)
        else:
            i += 1
    
    return emb, coup


def generate(emb, coup):
    """Generate canonical CRS from embeddings and couplings"""
    coup = {tuple(sorted(pair)) for pair in coup}
    parent_map = {c: p for c, p in emb}
    realms = sorted(set([c for c,p in emb] + [p for c,p in emb] + [x for pair in coup for x in pair]))
    
    def chain(r):
        for c, p in emb:
            if p == r:
                return f"{r}[{chain(c)}]"
        return r
    
    roots = [r for r in realms if r not in parent_map]
    realm_couple = {r: set() for r in realms}
    for r1, r2 in coup:
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

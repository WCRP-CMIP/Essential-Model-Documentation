/**CRS Parser - Canonical Realm String*/

function parse(s) {
  const emb = [], coup = new Set();
  let i = 0;
  
  function readCode() {
    if (i >= s.length || s[i] !== s[i].toUpperCase()) return null;
    let code = s[i++];
    if (i < s.length && s[i] === s[i].toLowerCase()) code += s[i++];
    return code;
  }
  
  function parseEmbed(p) {
    if (i < s.length && s[i] === '[') {
      i++;
      const c = readCode();
      if (c) {
        emb.push([c, p]);
        parseEmbed(c);
      }
      if (i < s.length && s[i] === ']') i++;
    }
  }
  
  function parseCouple(r) {
    if (i < s.length && s[i] === '(') {
      i++;
      while (i < s.length && s[i] !== ')') {
        if (s[i] === ',') i++;
        else {
          const c = readCode();
          if (c) coup.add(JSON.stringify(sorted([r, c])));
        }
      }
      if (i < s.length) i++;
    }
  }
  
  while (i < s.length) {
    const c = readCode();
    if (c) {
      parseEmbed(c);
      parseCouple(c);
    } else i++;
  }
  
  return {emb, coup: Array.from(coup).map(JSON.parse)};
}

function generate(emb, coup) {
  const coupSet = new Set(coup.map(p => JSON.stringify([...p].sort())));
  const pMap = new Map(emb);
  const realms = [...new Set([...emb.flat(), ...coup.flat()])].sort();
  
  function chain(r) {
    for (const [c, p] of emb) {
      if (p === r) return `${r}[${chain(c)}]`;
    }
    return r;
  }
  
  const roots = realms.filter(r => !pMap.has(r));
  const rCoup = Object.fromEntries(realms.map(r => [r, []]));
  
  coupSet.forEach(pair => {
    const [r1, r2] = JSON.parse(pair);
    if (realms.indexOf(r1) < realms.indexOf(r2)) rCoup[r1].push(r2);
    else rCoup[r2].push(r1);
  });
  
  return roots.map(r => {
    let s = chain(r);
    if (rCoup[r].length) s += `(${rCoup[r].join(',')})`;
    return s;
  }).join('');
}

function sorted(arr) { return arr.sort(); }

// Export for Node.js
if (typeof module !== 'undefined') {
  module.exports = { parse, generate };
}

#!/usr/bin/env python3
"""
Generate D3 chord diagram visualization showing models ↔ realms.

Creates an interactive HTML page with:
- Chord diagram: models connected to their realms (via component_configs)
- Color coding by realm/scientific domain
- Hover tooltips with component details
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from helpers.data_loader import init_loader, fetch_data
from helpers.realm_colors import REALM_COLORS, DEFAULT_COLOR, get_realm_color


OUTPUT_DIR = SCRIPT_DIR.parent / "Visualizations"


REALM_SHORT_NAMES = {
    "atmosphere": "Atmos",
    "ocean": "Ocean",
    "land-surface": "Land",
    "sea-ice": "SeaIce",
    "land-ice": "LandIce",
    "aerosol": "Aerosol",
    "atmospheric-chemistry": "AtmosChem",
    "ocean-biogeochemistry": "OcnBgchem",
}


def get_realm_from_config_id(config_id):
    """Extract realm from component_config ID like 'atmosphere_arpege-climat-version-6-3_c100_v100'."""
    if not config_id:
        return None
    parts = config_id.split("_")
    if parts:
        # First part is the realm, but might be hyphenated like "land-surface"
        # Check if first two parts form a known realm
        if len(parts) >= 2:
            two_part = f"{parts[0]}-{parts[1]}"
            if two_part in REALM_COLORS:
                return two_part
        return parts[0]
    return None


def build_chord_data():
    """Build data structure for chord diagram."""
    # Fetch all models
    models = fetch_data("model", depth=1)
    
    # Build nodes and matrix
    model_names = []
    realm_names = list(REALM_COLORS.keys())
    
    # Collect all models and their realm connections
    model_realm_matrix = defaultdict(lambda: defaultdict(int))
    model_components = defaultdict(list)  # For tooltips
    
    for model in models:
        if not isinstance(model, dict):
            continue
        
        model_id = model.get("@id") or model.get("validation_key")
        model_name = model.get("name") or model.get("ui_label") or model_id
        
        if not model_id:
            continue
        
        if model_name not in model_names:
            model_names.append(model_name)
        
        # Get realms from component_configs
        configs = model.get("component_configs", [])
        if isinstance(configs, list):
            for config_id in configs:
                if isinstance(config_id, str):
                    realm = get_realm_from_config_id(config_id)
                    if realm and realm in realm_names:
                        model_realm_matrix[model_name][realm] += 1
                        model_components[model_name].append({
                            "config": config_id,
                            "realm": realm
                        })
        
        # Also use dynamic_components as backup
        dynamic = model.get("dynamic_components", [])
        if isinstance(dynamic, list):
            for comp in dynamic:
                if isinstance(comp, str) and comp in realm_names:
                    if model_realm_matrix[model_name][comp] == 0:
                        model_realm_matrix[model_name][comp] = 1
    
    # Filter to models that have connections
    model_names = [m for m in model_names if sum(model_realm_matrix[m].values()) > 0]
    
    # Filter realms that have connections
    realm_names = [r for r in realm_names if any(model_realm_matrix[m][r] > 0 for m in model_names)]
    
    # Build combined node list: models first, then realms
    nodes = []
    for name in model_names:
        nodes.append({
            "id": name,
            "name": name,
            "type": "model",
            "color": "#1e40af"
        })
    
    for realm in realm_names:
        nodes.append({
            "id": realm,
            "name": REALM_SHORT_NAMES.get(realm, realm.title()),
            "fullName": realm.replace("-", " ").title(),
            "type": "realm",
            "color": get_realm_color(realm)
        })
    
    # Build matrix (n x n where n = models + realms)
    n = len(nodes)
    matrix = [[0] * n for _ in range(n)]
    
    model_offset = 0
    realm_offset = len(model_names)
    
    for i, model_name in enumerate(model_names):
        for j, realm in enumerate(realm_names):
            count = model_realm_matrix[model_name][realm]
            if count > 0:
                matrix[model_offset + i][realm_offset + j] = count
                matrix[realm_offset + j][model_offset + i] = count
    
    return {
        "nodes": nodes,
        "matrix": matrix,
        "modelCount": len(model_names),
        "realmCount": len(realm_names),
        "modelComponents": dict(model_components),
        "colors": REALM_COLORS
    }


def generate_html(data):
    """Generate the HTML page with D3 chord diagram."""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Model-Realm Relationships | EMD Visualization</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            min-height: 100vh;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 2rem;
        }}
        
        h1 {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        
        .subtitle {{
            color: #94a3b8;
            font-size: 1rem;
        }}
        
        .visualization {{
            display: flex;
            gap: 2rem;
            align-items: flex-start;
        }}
        
        .chart-container {{
            flex: 1;
            background: #1e293b;
            border-radius: 12px;
            padding: 1.5rem;
            min-height: 750px;
        }}
        
        .sidebar {{
            width: 280px;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }}
        
        .legend {{
            background: #1e293b;
            border-radius: 12px;
            padding: 1.5rem;
        }}
        
        .legend h3 {{
            font-size: 0.875rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #94a3b8;
            margin-bottom: 1rem;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.5rem;
            font-size: 0.875rem;
            cursor: pointer;
            padding: 0.25rem;
            border-radius: 4px;
            transition: background 0.2s;
        }}
        
        .legend-item:hover {{
            background: #334155;
        }}
        
        .legend-item.dimmed {{
            opacity: 0.3;
        }}
        
        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 4px;
            flex-shrink: 0;
        }}
        
        #chord-chart {{
            width: 100%;
            height: 700px;
        }}
        
        .chord {{
            fill-opacity: 0.7;
            transition: fill-opacity 0.2s;
        }}
        
        .chord.dimmed {{
            fill-opacity: 0.1;
        }}
        
        .chord:hover {{
            fill-opacity: 1;
        }}
        
        .arc path {{
            stroke: #0f172a;
            stroke-width: 2px;
            transition: opacity 0.2s;
        }}
        
        .arc.dimmed path {{
            opacity: 0.2;
        }}
        
        .arc-label {{
            font-size: 11px;
            fill: #e2e8f0;
            transition: opacity 0.2s;
        }}
        
        .arc.dimmed .arc-label {{
            opacity: 0.2;
        }}
        
        .tooltip {{
            position: absolute;
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 0.75rem 1rem;
            font-size: 0.875rem;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s;
            z-index: 1000;
            max-width: 350px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        
        .tooltip.visible {{
            opacity: 1;
        }}
        
        .tooltip-title {{
            font-weight: 600;
            margin-bottom: 0.5rem;
            font-size: 1rem;
        }}
        
        .tooltip-detail {{
            color: #94a3b8;
            margin-bottom: 0.25rem;
        }}
        
        .tooltip-components {{
            margin-top: 0.5rem;
            padding-top: 0.5rem;
            border-top: 1px solid #334155;
        }}
        
        .tooltip-component {{
            font-size: 0.75rem;
            color: #64748b;
            margin-bottom: 0.125rem;
            font-family: monospace;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        
        .stat-card {{
            background: #1e293b;
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 2rem;
            font-weight: 700;
            color: #3b82f6;
        }}
        
        .stat-label {{
            font-size: 0.75rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .details-panel {{
            background: #1e293b;
            border-radius: 12px;
            padding: 1.5rem;
            max-height: 300px;
            overflow-y: auto;
        }}
        
        .details-panel h3 {{
            font-size: 0.875rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #94a3b8;
            margin-bottom: 1rem;
        }}
        
        .details-content {{
            font-size: 0.875rem;
            color: #cbd5e1;
        }}
        
        .component-list {{
            list-style: none;
        }}
        
        .component-list li {{
            padding: 0.25rem 0;
            font-family: monospace;
            font-size: 0.75rem;
            color: #64748b;
        }}
        
        footer {{
            text-align: center;
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid #334155;
            color: #64748b;
            font-size: 0.875rem;
        }}
        
        footer a {{
            color: #3b82f6;
            text-decoration: none;
        }}
        
        footer a:hover {{
            text-decoration: underline;
        }}
        
        @media (max-width: 1024px) {{
            .visualization {{
                flex-direction: column;
            }}
            .sidebar {{
                width: 100%;
                flex-direction: row;
                flex-wrap: wrap;
            }}
            .legend, .details-panel {{
                flex: 1;
                min-width: 200px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌍 Model-Realm Relationships</h1>
            <p class="subtitle">Interactive chord diagram showing how climate models connect to scientific realms through their components</p>
        </header>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value" id="model-count">{data['modelCount']}</div>
                <div class="stat-label">Models</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="realm-count">{data['realmCount']}</div>
                <div class="stat-label">Realms</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="connection-count">0</div>
                <div class="stat-label">Connections</div>
            </div>
        </div>
        
        <div class="visualization">
            <div class="chart-container">
                <div id="chord-chart"></div>
            </div>
            <div class="sidebar">
                <div class="legend">
                    <h3>Scientific Realms</h3>
                    <div id="realm-legend"></div>
                </div>
                <div class="legend">
                    <h3>Models</h3>
                    <div id="model-legend"></div>
                </div>
                <div class="details-panel">
                    <h3>Selected Details</h3>
                    <div class="details-content" id="details-content">
                        <p style="color: #64748b;">Hover over a model or realm to see details</p>
                    </div>
                </div>
            </div>
        </div>
        
        <footer>
            <p>Data from <a href="https://emd.mipcvs.dev/">EMD Registry</a> · 
            Part of <a href="https://wcrp-cmip.org/">WCRP CMIP</a> · 
            Generated {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}</p>
        </footer>
    </div>
    
    <div class="tooltip" id="tooltip"></div>
    
    <script>
    const data = {json.dumps(data)};
    
    // Count total connections
    let totalConnections = 0;
    data.matrix.forEach(row => row.forEach(val => totalConnections += val));
    document.getElementById('connection-count').textContent = Math.floor(totalConnections / 2);
    
    // Build legends
    const realmLegend = document.getElementById('realm-legend');
    const modelLegend = document.getElementById('model-legend');
    
    data.nodes.forEach((node, i) => {{
        const item = document.createElement('div');
        item.className = 'legend-item';
        item.dataset.index = i;
        item.innerHTML = `
            <div class="legend-color" style="background: ${{node.color}};"></div>
            <span>${{node.name}}</span>
        `;
        item.addEventListener('mouseenter', () => highlightNode(i));
        item.addEventListener('mouseleave', clearHighlight);
        
        if (node.type === 'realm') {{
            realmLegend.appendChild(item);
        }} else {{
            modelLegend.appendChild(item);
        }}
    }});
    
    // D3 Chord Diagram
    const container = document.getElementById('chord-chart');
    const width = container.clientWidth;
    const height = 700;
    const innerRadius = Math.min(width, height) * 0.38;
    const outerRadius = innerRadius + 25;
    
    const svg = d3.select('#chord-chart')
        .append('svg')
        .attr('viewBox', [-width/2, -height/2, width, height])
        .attr('width', '100%')
        .attr('height', height);
    
    const tooltip = d3.select('#tooltip');
    const detailsContent = document.getElementById('details-content');
    
    const chord = d3.chord()
        .padAngle(0.04)
        .sortSubgroups(d3.descending)
        .sortChords(d3.descending);
    
    const chords = chord(data.matrix);
    
    const arc = d3.arc()
        .innerRadius(innerRadius)
        .outerRadius(outerRadius);
    
    const ribbon = d3.ribbon()
        .radius(innerRadius - 1);
    
    // Draw ribbons (chords) first so they're behind arcs
    const ribbons = svg.append('g')
        .attr('class', 'ribbons')
        .selectAll('path')
        .data(chords)
        .join('path')
        .attr('class', 'chord')
        .attr('d', ribbon)
        .attr('fill', d => {{
            // Color by the realm (which is in the higher index range)
            const realmIdx = Math.max(d.source.index, d.target.index);
            return data.nodes[realmIdx].color;
        }})
        .attr('data-source', d => d.source.index)
        .attr('data-target', d => d.target.index);
    
    // Draw arcs (nodes)
    const groups = svg.append('g')
        .selectAll('g')
        .data(chords.groups)
        .join('g')
        .attr('class', 'arc')
        .attr('data-index', d => d.index);
    
    groups.append('path')
        .attr('d', arc)
        .attr('fill', d => data.nodes[d.index].color)
        .on('mouseenter', (event, d) => {{
            highlightNode(d.index);
            showTooltip(event, d);
        }})
        .on('mousemove', (event) => {{
            tooltip
                .style('left', (event.pageX + 15) + 'px')
                .style('top', (event.pageY - 10) + 'px');
        }})
        .on('mouseleave', () => {{
            clearHighlight();
            tooltip.classed('visible', false);
        }});
    
    // Draw labels
    groups.append('text')
        .each(d => {{ d.angle = (d.startAngle + d.endAngle) / 2; }})
        .attr('dy', '0.35em')
        .attr('class', 'arc-label')
        .attr('transform', d => `
            rotate(${{(d.angle * 180 / Math.PI - 90)}})
            translate(${{outerRadius + 8}})
            ${{d.angle > Math.PI ? 'rotate(180)' : ''}}
        `)
        .attr('text-anchor', d => d.angle > Math.PI ? 'end' : 'start')
        .text(d => data.nodes[d.index].name);
    
    function highlightNode(index) {{
        // Dim all arcs and ribbons
        svg.selectAll('.arc').classed('dimmed', true);
        svg.selectAll('.chord').classed('dimmed', true);
        document.querySelectorAll('.legend-item').forEach(el => el.classList.add('dimmed'));
        
        // Highlight selected arc
        svg.select(`.arc[data-index="${{index}}"]`).classed('dimmed', false);
        document.querySelector(`.legend-item[data-index="${{index}}"]`)?.classList.remove('dimmed');
        
        // Highlight connected ribbons and their endpoints
        svg.selectAll('.chord').each(function(d) {{
            if (d.source.index === index || d.target.index === index) {{
                d3.select(this).classed('dimmed', false);
                const otherIdx = d.source.index === index ? d.target.index : d.source.index;
                svg.select(`.arc[data-index="${{otherIdx}}"]`).classed('dimmed', false);
                document.querySelector(`.legend-item[data-index="${{otherIdx}}"]`)?.classList.remove('dimmed');
            }}
        }});
        
        // Update details panel
        const node = data.nodes[index];
        if (node.type === 'model') {{
            const components = data.modelComponents[node.id] || [];
            detailsContent.innerHTML = `
                <p><strong>${{node.name}}</strong></p>
                <p style="color: #94a3b8; margin: 0.5rem 0;">Components:</p>
                <ul class="component-list">
                    ${{components.map(c => `<li>${{c.config}}</li>`).join('')}}
                </ul>
            `;
        }} else {{
            // Find all models connected to this realm
            const connectedModels = [];
            data.matrix.forEach((row, i) => {{
                if (i < data.modelCount && row[index] > 0) {{
                    connectedModels.push(data.nodes[i].name);
                }}
            }});
            detailsContent.innerHTML = `
                <p><strong>${{node.fullName || node.name}}</strong></p>
                <p style="color: #94a3b8; margin: 0.5rem 0;">Models with this realm:</p>
                <ul class="component-list">
                    ${{connectedModels.map(m => `<li>${{m}}</li>`).join('')}}
                </ul>
            `;
        }}
    }}
    
    function clearHighlight() {{
        svg.selectAll('.arc').classed('dimmed', false);
        svg.selectAll('.chord').classed('dimmed', false);
        document.querySelectorAll('.legend-item').forEach(el => el.classList.remove('dimmed'));
    }}
    
    function showTooltip(event, d) {{
        const node = data.nodes[d.index];
        let html = `<div class="tooltip-title">${{node.fullName || node.name}}</div>`;
        html += `<div class="tooltip-detail">Type: ${{node.type === 'model' ? 'Climate Model' : 'Scientific Realm'}}</div>`;
        
        if (node.type === 'model') {{
            const components = data.modelComponents[node.id] || [];
            const realms = [...new Set(components.map(c => c.realm))];
            html += `<div class="tooltip-detail">Realms: ${{realms.length}}</div>`;
            html += `<div class="tooltip-detail">Components: ${{components.length}}</div>`;
        }} else {{
            // Count connected models
            let modelCount = 0;
            data.matrix.forEach((row, i) => {{
                if (i < data.modelCount && row[d.index] > 0) modelCount++;
            }});
            html += `<div class="tooltip-detail">Models: ${{modelCount}}</div>`;
        }}
        
        tooltip.html(html)
            .classed('visible', true)
            .style('left', (event.pageX + 15) + 'px')
            .style('top', (event.pageY - 10) + 'px');
    }}
    </script>
</body>
</html>
'''


def main():
    print("Model-Realm Chord Diagram Generator")
    print("=" * 40)
    
    # Initialize data loader
    init_loader()
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Build chord data
    print("Building chord diagram data...")
    data = build_chord_data()
    
    print(f"  Models: {data['modelCount']}")
    print(f"  Realms: {data['realmCount']}")
    print(f"  Nodes: {len(data['nodes'])}")
    
    if data['modelCount'] == 0:
        print("  No models found - skipping visualization")
        return 0
    
    # Generate HTML
    print("Generating visualization...")
    html = generate_html(data)
    
    output_path = OUTPUT_DIR / "model-realm-chord.html"
    output_path.write_text(html, encoding="utf-8")
    
    print(f"✅ Generated: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
else:
    main()

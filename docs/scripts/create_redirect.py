#!/usr/bin/env python3
"""
Generate root redirect page to docs/.

Creates an index.html at the repository root that redirects to docs/
Reads project name and theme colour from .copier-answers-documentation.yml
so every project gets a correctly branded redirect page.
"""

from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

SCRIPT_DIR = Path(__file__).parent.resolve()
DOCS_DIR   = SCRIPT_DIR.parent
REPO_ROOT  = DOCS_DIR.parent

#  Colour map mirrors copier/documentation/docs/assets/logo.svg.jinja 
COLOR_MAP = {
    'red':         '#f44336', 'pink':        '#e91e63', 'purple':      '#9c27b0',
    'deep-purple': '#673ab7', 'indigo':      '#3f51b5', 'blue':        '#2196f3',
    'light-blue':  '#03a9f4', 'cyan':        '#00bcd4', 'teal':        '#009688',
    'green':       '#4caf50', 'light-green': '#8bc34a', 'lime':        '#cddc39',
    'yellow':      '#ffeb3b', 'amber':       '#ffc107', 'orange':      '#ff9800',
    'deep-orange': '#ff5722', 'brown':       '#795548', 'grey':        '#9e9e9e',
    'blue-grey':   '#607d8b', 'black':       '#000000',
}


def _read_copier_answers() -> dict:
    """Parse .copier-answers-documentation.yml if available."""
    answers_path = REPO_ROOT / ".copier-answers-documentation.yml"
    if not answers_path.exists():
        return {}

    if HAS_YAML:
        try:
            with open(answers_path) as f:
                return yaml.safe_load(f) or {}
        except Exception:
            pass

    # Minimal fallback parser (key: value lines, ignoring comments/blanks)
    data = {}
    for line in answers_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if ':' in line:
            k, _, v = line.partition(':')
            data[k.strip()] = v.strip()
    return data


def _build_html(project_name: str, primary: str, primary_light: str,
                redirect_url: str) -> str:
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="3; url={redirect_url}">
    <link rel="canonical" href="{redirect_url}">
    <title>Redirecting  {project_name}</title>
    <style>
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8fafc;
            color: #1e293b;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }}

        .card {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 3rem 3.5rem;
            text-align: center;
            max-width: 420px;
            width: 90%;
            box-shadow: 0 4px 24px color-mix(in srgb, {primary} 10%, transparent);
        }}

        /*  Logo spinner  */
        .logo-wrap {{
            width: 80px;
            height: 80px;
            margin: 0 auto 2rem;
            animation: spin 1.4s linear infinite;
            transform-origin: center center;
        }}

        @keyframes spin {{
            from {{ transform: rotate(0deg); }}
            to   {{ transform: rotate(360deg); }}
        }}

        /*  Text  */
        h1 {{
            font-size: 1.2rem;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 0.5rem;
            letter-spacing: -0.01em;
        }}

        .destination {{
            font-size: 0.95rem;
            color: #475569;
            margin-bottom: 1.75rem;
        }}

        .destination code {{
            font-family: 'JetBrains Mono', 'Fira Mono', monospace;
            font-size: 0.88rem;
            background: #f1f5f9;
            border: 1px solid #e2e8f0;
            border-radius: 5px;
            padding: 1px 6px;
            color: {primary};
        }}

        /*  Fallback link  */
        .fallback {{
            font-size: 0.88rem;
            color: #94a3b8;
        }}

        .fallback a {{
            color: {primary};
            text-decoration: none;
            font-weight: 500;
            border-bottom: 1px solid {primary_light};
            transition: border-color 0.15s;
        }}

        .fallback a:hover {{
            border-color: {primary};
        }}
    </style>
</head>
<body>
    <div class="card">

        <!-- Project logo as spinner -->
        <div class="logo-wrap">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="80" height="80" aria-hidden="true">
                <rect width="256" height="256" fill="none"/>
                <line x1="208" y1="128" x2="128" y2="208" fill="none"
                      stroke="{primary}" stroke-linecap="round" stroke-linejoin="round" stroke-width="32"/>
                <line x1="192" y1="40" x2="40" y2="192" fill="none"
                      stroke="{primary}" stroke-linecap="round" stroke-linejoin="round" stroke-width="32"/>
            </svg>
        </div>

        <h1>Redirecting to {project_name}</h1>
        <p class="destination">Taking you to <code>{redirect_url}</code></p>

        <p class="fallback">
            Not redirected?
            <a href="{redirect_url}">{project_name} &rarr;</a>
        </p>

    </div>
</body>
</html>
'''


def main():
    """Generate redirect page at repository root."""
    answers = _read_copier_answers()

    project_name = answers.get('project_name', 'Documentation')
    header_color = answers.get('header_color', 'blue')
    redirect_url = 'docs/'

    primary       = COLOR_MAP.get(header_color, '#2196f3')
    # Approximate a light tint for the underline (blend toward white ~65%)
    primary_light = primary + 'a8'   # use alpha shorthand; falls back fine in all browsers

    html = _build_html(project_name, primary, primary_light, redirect_url)

    redirect_path = REPO_ROOT / "index.html"
    redirect_path.write_text(html, encoding='utf-8')
    print(f" Created redirect page: {redirect_path}")
    print(f"   Project : {project_name}")
    print(f"   Colour  : {header_color} ({primary})")
    print(f"   Target  : {redirect_url}")


if __name__ == "__main__":
    main()
else:
    # Auto-run when imported by run_scripts.py
    main()

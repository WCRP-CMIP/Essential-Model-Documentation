<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GELATO | Sea Ice Model Component</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Akshar:wght@400;500;600&family=Roboto:wght@300;400;500;700&family=Roboto+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --md-text-font: "Roboto", sans-serif;
            --md-code-font: "Roboto Mono", monospace;
            --md-title-font: "Akshar", sans-serif;
            --md-default-fg-color: rgba(0, 0, 0, 0.87);
            --md-default-fg-color--light: rgba(0, 0, 0, 0.54);
            --md-default-fg-color--lighter: rgba(0, 0, 0, 0.32);
            --md-default-fg-color--lightest: rgba(0, 0, 0, 0.07);
            --md-default-bg-color: #fff;
            --md-default-bg-color--light: #f5f5f5;
            --md-primary-fg-color: #2196f3;
            --md-accent-fg-color: #ff9800;
            --component-accent: #00bcd4;
        }
        @media (prefers-color-scheme: dark) {
            :root {
                --md-default-fg-color: rgba(255, 255, 255, 0.87);
                --md-default-fg-color--light: rgba(255, 255, 255, 0.54);
                --md-default-fg-color--lighter: rgba(255, 255, 255, 0.32);
                --md-default-fg-color--lightest: rgba(255, 255, 255, 0.07);
                --md-default-bg-color: #1e1e1e;
                --md-default-bg-color--light: #2d2d2d;
            }
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: var(--md-text-font); background: var(--md-default-bg-color); color: var(--md-default-fg-color); line-height: 1.6; font-size: 0.8rem; min-height: 100vh; }
        .container { max-width: 61rem; margin: 0 auto; padding: 2rem 1.5rem 4rem; }
        .header { margin-bottom: 3rem; }
        .breadcrumb { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1.5rem; font-size: 0.75rem; color: var(--md-default-fg-color--light); }
        .breadcrumb a { color: var(--md-default-fg-color--light); text-decoration: none; }
        .breadcrumb a:hover { color: var(--md-primary-fg-color); }
        .component-badge { display: inline-flex; align-items: center; gap: 0.5rem; background: rgba(0, 188, 212, 0.1); border: 1px solid rgba(0, 188, 212, 0.25); padding: 0.35rem 0.9rem; border-radius: 100px; font-size: 0.65rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: var(--component-accent); margin-bottom: 1rem; }
        .component-badge::before { content: ''; width: 8px; height: 8px; background: var(--component-accent); border-radius: 50%; animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(0.8); } }
        .component-title { font-family: var(--md-title-font); font-size: 2.5rem; font-weight: 600; line-height: 1.1; margin-bottom: 0.5rem; }
        .component-subtitle { font-size: 1rem; color: var(--md-default-fg-color--light); margin-bottom: 1.5rem; font-style: italic; }
        .header-meta { display: flex; flex-wrap: wrap; gap: 2rem; padding-top: 1.25rem; border-top: 1px solid var(--md-default-fg-color--lightest); }
        .meta-item { display: flex; flex-direction: column; gap: 0.2rem; }
        .meta-label { font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--md-default-fg-color--light); font-weight: 500; }
        .meta-value { font-family: var(--md-code-font); font-size: 0.8rem; }
        .meta-value a { color: var(--md-primary-fg-color); text-decoration: none; }
        .meta-value a:hover { text-decoration: underline; }
        .meta-value.private { color: var(--md-accent-fg-color); }
        .meta-value.private::before { content: '🔒 '; }
        .section { background: var(--md-default-bg-color); border: 1px solid var(--md-default-fg-color--lightest); border-radius: 8px; margin-bottom: 1rem; overflow: hidden; }
        .section-header { display: flex; align-items: center; justify-content: space-between; padding: 1rem 1.25rem; cursor: pointer; user-select: none; }
        .section-header:hover { background: var(--md-default-bg-color--light); }
        .section-title-wrapper { display: flex; align-items: center; gap: 0.75rem; }
        .section-icon { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; background: var(--md-default-bg-color--light); border-radius: 8px; color: var(--component-accent); }
        .section-icon svg { width: 18px; height: 18px; }
        .section-title { font-family: var(--md-title-font); font-size: 1.1rem; font-weight: 600; }
        .section-toggle { width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; background: var(--md-default-bg-color--light); border-radius: 6px; }
        .section-toggle svg { width: 14px; height: 14px; color: var(--md-default-fg-color--light); transition: transform 0.3s; }
        .section.expanded .section-toggle svg { transform: rotate(180deg); }
        .section-content { max-height: 0; overflow: hidden; transition: max-height 0.4s; }
        .section.expanded .section-content { max-height: 2000px; }
        .section-body { padding: 0 1.25rem 1.25rem; }
        .section-divider { height: 1px; background: var(--md-default-fg-color--lightest); margin-bottom: 1.25rem; }
        .description-text { font-size: 0.85rem; color: var(--md-default-fg-color--light); line-height: 1.8; }
        .description-text strong { color: var(--md-default-fg-color); font-weight: 500; }
        .domain-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }
        .domain-card { background: var(--md-default-bg-color--light); border: 1px solid var(--md-default-fg-color--lightest); border-radius: 8px; padding: 1.25rem; border-left: 3px solid var(--component-accent); transition: all 0.25s; }
        .domain-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .domain-card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem; }
        .domain-card-title { font-family: var(--md-title-font); font-weight: 600; font-size: 1.1rem; }
        .domain-card-type { font-size: 0.55rem; padding: 0.2rem 0.5rem; border-radius: 100px; font-weight: 600; text-transform: uppercase; background: rgba(0, 188, 212, 0.15); color: var(--component-accent); }
        .domain-card-id { font-family: var(--md-code-font); font-size: 0.7rem; color: var(--md-primary-fg-color); margin-bottom: 0.5rem; }
        .domain-card-description { font-size: 0.8rem; color: var(--md-default-fg-color--light); line-height: 1.5; margin-bottom: 0.75rem; }
        .domain-card-meta { display: flex; flex-wrap: wrap; gap: 0.4rem; }
        .domain-meta-tag { font-family: var(--md-code-font); font-size: 0.65rem; padding: 0.2rem 0.5rem; background: var(--md-default-bg-color); border: 1px solid var(--md-default-fg-color--lightest); border-radius: 4px; color: var(--md-default-fg-color--light); }
        .grid-info-text { font-size: 0.85rem; color: var(--md-default-fg-color--light); line-height: 1.8; margin-bottom: 1.25rem; }
        .grid-info-text a { color: var(--md-primary-fg-color); text-decoration: none; }
        .grid-info-text a:hover { text-decoration: underline; }
        .grid-info-text strong { color: var(--md-default-fg-color); font-weight: 500; }
        .grid-specs { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }
        .grid-spec-card { background: var(--md-default-bg-color--light); border: 1px solid var(--md-default-fg-color--lightest); border-radius: 8px; padding: 1.25rem; border-left: 3px solid var(--component-accent); transition: all 0.25s; }
        .grid-spec-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .grid-spec-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem; }
        .grid-spec-label { font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--md-default-fg-color--light); }
        .grid-spec-value { font-family: var(--md-code-font); font-size: 1.4rem; font-weight: 500; color: var(--component-accent); }
        .grid-spec-desc { font-size: 0.8rem; color: var(--md-default-fg-color--light); line-height: 1.6; margin-bottom: 0.75rem; }
        .grid-spec-details { display: flex; flex-wrap: wrap; gap: 0.4rem; }
        .grid-detail-tag { font-family: var(--md-code-font); font-size: 0.65rem; padding: 0.2rem 0.5rem; background: var(--md-default-bg-color); border: 1px solid var(--md-default-fg-color--lightest); border-radius: 4px; color: var(--md-default-fg-color--light); }
        .tech-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; }
        .tech-item { padding: 1rem; background: var(--md-default-bg-color--light); border-radius: 8px; border: 1px solid var(--md-default-fg-color--lightest); }
        .tech-label { font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--md-default-fg-color--light); margin-bottom: 0.35rem; }
        .tech-value { font-family: var(--md-code-font); font-size: 0.8rem; word-break: break-all; }
        .tech-value a { color: var(--md-primary-fg-color); text-decoration: none; }
        .type-badges { display: flex; flex-wrap: wrap; gap: 0.4rem; }
        .type-badge { font-family: var(--md-code-font); font-size: 0.7rem; padding: 0.3rem 0.6rem; background: var(--md-default-bg-color--light); border: 1px solid var(--md-default-fg-color--lightest); border-radius: 4px; color: var(--md-default-fg-color--light); }
        .type-badge:hover { border-color: var(--component-accent); color: var(--component-accent); }
        .coupling-status { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; background: var(--md-default-bg-color--light); border: 1px solid var(--md-default-fg-color--lighter); border-radius: 8px; font-size: 0.8rem; color: var(--md-default-fg-color--light); }
        .reference-item { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; background: var(--md-default-bg-color--light); border-radius: 8px; border: 1px solid var(--md-default-fg-color--lightest); text-decoration: none; transition: all 0.2s; }
        .reference-item:hover { border-color: var(--md-primary-fg-color); transform: translateX(4px); }
        .reference-icon { width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; background: var(--md-default-bg-color); border-radius: 6px; color: var(--md-primary-fg-color); }
        .reference-icon svg { width: 16px; height: 16px; }
        .reference-text { font-family: var(--md-code-font); font-size: 0.8rem; }
        .reference-arrow { margin-left: auto; color: var(--md-default-fg-color--light); }
        .reference-item:hover .reference-arrow { color: var(--md-primary-fg-color); }
        .footer { margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid var(--md-default-fg-color--lightest); text-align: center; }
        .footer-text { font-size: 0.75rem; color: var(--md-default-fg-color--light); }
        .footer-link { color: var(--md-primary-fg-color); text-decoration: none; }
        @media (max-width: 768px) { .container { padding: 1.5rem 1rem 3rem; } .component-title { font-size: 2rem; } .domain-grid, .grid-specs { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <nav class="breadcrumb">
                <a href="../">← Back to Documentation</a>
                <span>|</span>
                <a href="https://emd.mipcvs.dev/" target="_blank">EMD Registry</a>
                <span>→</span>
                <a href="https://emd.mipcvs.dev/model_component/" target="_blank">Model Components</a>
                <span>→</span>
                <span>GELATO</span>
            </nav>
            <div class="component-badge">Model Component</div>
            <h1 class="component-title">GELATO</h1>
            <p class="component-subtitle">Global Experimental Leads and sea ice for ATmosphere and Ocean</p>
            <div class="header-meta">
                <div class="meta-item">
                    <span class="meta-label">Family</span>
                    <span class="meta-value">gelato</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Scientific Domain</span>
                    <span class="meta-value">Sea Ice</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Code Base</span>
                    <span class="meta-value private">Private</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Context</span>
                    <span class="meta-value"><a href="https://emd.mipcvs.dev/model_component/gelato.json" target="_blank">JSON-LD →</a></span>
                </div>
            </div>
        </header>

        <main>
            <!-- Description -->
            <section class="section expanded">
                <div class="section-header" onclick="toggleSection(this)">
                    <div class="section-title-wrapper">
                        <div class="section-icon"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg></div>
                        <h2 class="section-title">Description</h2>
                    </div>
                    <div class="section-toggle"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" /></svg></div>
                </div>
                <div class="section-content">
                    <div class="section-body">
                        <div class="section-divider"></div>
                        <p class="description-text"><strong>GELATO</strong> (Global Experimental Leads and sea ice for ATmosphere and Ocean) is a dynamic-thermodynamic sea ice model developed at CNRM (Centre National de Recherches Météorologiques). It is embedded within the <strong>Ocean</strong> domain and provides comprehensive sea ice dynamics and thermodynamics for coupled climate simulations.</p>
                        <p class="description-text" style="margin-top: 1rem;">Key features include <strong>elastic-viscous-plastic (EVP) rheology</strong> for ice dynamics, a <strong>multi-category ice thickness distribution</strong> with 5 thickness categories, redistribution of ice through rafting and ridging processes, and detailed treatment of leads, snow cover, and snow-ice formation. The model accounts for heat conduction and storage within the ice slab and includes parameterizations for melt ponds and their effect on surface albedo.</p>
                    </div>
                </div>
            </section>

            <!-- Scientific Domains -->
            <section class="section expanded">
                <div class="section-header" onclick="toggleSection(this)">
                    <div class="section-title-wrapper">
                        <div class="section-icon"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg></div>
                        <h2 class="section-title">Scientific Domains</h2>
                    </div>
                    <div class="section-toggle"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" /></svg></div>
                </div>
                <div class="section-content">
                    <div class="section-body">
                        <div class="section-divider"></div>
                        <div class="domain-grid">
                            <div class="domain-card">
                                <div class="domain-card-header">
                                    <span class="domain-card-title">Sea Ice</span>
                                    <span class="domain-card-type">Component</span>
                                </div>
                                <div class="domain-card-id">@id: sea-ice</div>
                                <p class="domain-card-description">Primary scientific domain representing sea ice processes, formation, extent, and dynamics.</p>
                                <div class="domain-card-meta">
                                    <span class="domain-meta-tag">seaice</span>
                                    <span class="domain-meta-tag">seaIce</span>
                                    <span class="domain-meta-tag">sea_ice</span>
                                </div>
                            </div>
                            <div class="domain-card">
                                <div class="domain-card-header">
                                    <span class="domain-card-title">Ocean</span>
                                    <span class="domain-card-type">Embedded In</span>
                                </div>
                                <div class="domain-card-id">@id: ocean</div>
                                <p class="domain-card-description">Parent domain — GELATO operates embedded within the ocean model component.</p>
                                <div class="domain-card-meta">
                                    <span class="domain-meta-tag">ocean</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Computational Grids -->
            <section class="section expanded">
                <div class="section-header" onclick="toggleSection(this)">
                    <div class="section-title-wrapper">
                        <div class="section-icon"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg></div>
                        <h2 class="section-title">Computational Grids</h2>
                    </div>
                    <div class="section-toggle"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" /></svg></div>
                </div>
                <div class="section-content">
                    <div class="section-body">
                        <div class="section-divider"></div>
                        <p class="grid-info-text">
                            GELATO shares its computational grid with the host ocean model (typically <a href="https://www.nemo-ocean.eu/" target="_blank">NEMO</a>). The model uses the <strong>ORCA tripolar grid</strong> system, which avoids singularity issues at the North Pole by using a semi-analytical method with two poles placed over land masses (Canada and Siberia). This allows for efficient computation in polar regions where sea ice dynamics are critical.
                        </p>
                        <div class="grid-specs">
                            <div class="grid-spec-card">
                                <div class="grid-spec-header">
                                    <div class="grid-spec-label">Horizontal Grid</div>
                                    <div class="grid-spec-value">c101</div>
                                </div>
                                <p class="grid-spec-desc">
                                    Defines the horizontal spatial discretization used for sea ice calculations. This grid shares coordinates with the parent ocean model, enabling direct coupling without interpolation overhead. Based on the ORCA tripolar mesh with optimized resolution in polar and equatorial regions.
                                </p>
                                <div class="grid-spec-details">
                                    <span class="grid-detail-tag">tripolar</span>
                                    <span class="grid-detail-tag">staggered Arakawa-C</span>
                                    <span class="grid-detail-tag">curvilinear</span>
                                </div>
                            </div>
                            <div class="grid-spec-card">
                                <div class="grid-spec-header">
                                    <div class="grid-spec-label">Vertical Grid</div>
                                    <div class="grid-spec-value">v104</div>
                                </div>
                                <p class="grid-spec-desc">
                                    Specifies the vertical layer structure for sea ice thermodynamics. GELATO uses a multi-category ice thickness distribution with multiple vertical layers within each ice slab to resolve heat conduction, brine dynamics, and snow accumulation.
                                </p>
                                <div class="grid-spec-details">
                                    <span class="grid-detail-tag">multi-layer</span>
                                    <span class="grid-detail-tag">5 ice categories</span>
                                    <span class="grid-detail-tag">snow layer</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Coupling -->
            <section class="section">
                <div class="section-header" onclick="toggleSection(this)">
                    <div class="section-title-wrapper">
                        <div class="section-icon"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" /></svg></div>
                        <h2 class="section-title">Coupling</h2>
                    </div>
                    <div class="section-toggle"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" /></svg></div>
                </div>
                <div class="section-content">
                    <div class="section-body">
                        <div class="section-divider"></div>
                        <div class="coupling-status">
                            <span>○</span>
                            <span>No external coupling — component operates embedded within Ocean</span>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Technical Details -->
            <section class="section">
                <div class="section-header" onclick="toggleSection(this)">
                    <div class="section-title-wrapper">
                        <div class="section-icon"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" /></svg></div>
                        <h2 class="section-title">Technical Details</h2>
                    </div>
                    <div class="section-toggle"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" /></svg></div>
                </div>
                <div class="section-content">
                    <div class="section-body">
                        <div class="section-divider"></div>
                        <div class="tech-grid">
                            <div class="tech-item">
                                <div class="tech-label">Resource Identifier (@id)</div>
                                <div class="tech-value">gelato</div>
                            </div>
                            <div class="tech-item">
                                <div class="tech-label">Validation Key</div>
                                <div class="tech-value">gelato</div>
                            </div>
                            <div class="tech-item">
                                <div class="tech-label">JSON-LD Context</div>
                                <div class="tech-value"><a href="https://emd.mipcvs.dev/model_component/gelato.json" target="_blank">emd.mipcvs.dev/model_component/gelato.json</a></div>
                            </div>
                            <div class="tech-item">
                                <div class="tech-label">Resource Types (@type)</div>
                                <div class="type-badges">
                                    <span class="type-badge">emd</span>
                                    <span class="type-badge">wcrp:model_component</span>
                                    <span class="type-badge">esgvoc:ModelComponent</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- References -->
            <section class="section">
                <div class="section-header" onclick="toggleSection(this)">
                    <div class="section-title-wrapper">
                        <div class="section-icon"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg></div>
                        <h2 class="section-title">References</h2>
                    </div>
                    <div class="section-toggle"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" /></svg></div>
                </div>
                <div class="section-content">
                    <div class="section-body">
                        <div class="section-divider"></div>
                        <a href="#" class="reference-item">
                            <div class="reference-icon"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg></div>
                            <span class="reference-text">REF002</span>
                            <span class="reference-arrow">→</span>
                        </a>
                    </div>
                </div>
            </section>
        </main>

        <footer class="footer">
            <p class="footer-text">Data sourced from <a href="https://emd.mipcvs.dev/" class="footer-link" target="_blank">EMD Registry</a> · Part of the <a href="https://wcrp-cmip.org/" class="footer-link" target="_blank">WCRP CMIP</a> initiative</p>
        </footer>
    </div>
    <script>function toggleSection(header) { header.parentElement.classList.toggle('expanded'); }</script>
</body>
</html>

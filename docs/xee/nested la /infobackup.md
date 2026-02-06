<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CNRM-ESM2-1e | Earth System Model</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0a0f14;
            --bg-secondary: #111920;
            --bg-tertiary: #182028;
            --bg-card: #141c24;
            --accent-primary: #3ecf8e;
            --accent-secondary: #1a9f68;
            --accent-warm: #f0b429;
            --accent-blue: #4da6ff;
            --accent-purple: #a78bfa;
            --text-primary: #e8edf3;
            --text-secondary: #8899a8;
            --text-muted: #5a6a7a;
            --border-color: rgba(62, 207, 142, 0.15);
            --border-subtle: rgba(255, 255, 255, 0.06);
            --gradient-mesh: radial-gradient(ellipse at 20% 0%, rgba(62, 207, 142, 0.08) 0%, transparent 50%),
                             radial-gradient(ellipse at 80% 100%, rgba(77, 166, 255, 0.06) 0%, transparent 50%);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'DM Sans', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.7;
            min-height: 100vh;
        }

        .noise-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            opacity: 0.03;
            z-index: 1000;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
        }

        .gradient-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: var(--gradient-mesh);
            pointer-events: none;
            z-index: 0;
        }

        .container {
            max-width: 1100px;
            margin: 0 auto;
            padding: 3rem 2rem 5rem;
            position: relative;
            z-index: 1;
        }

        /* Header */
        .header {
            margin-bottom: 4rem;
            animation: fadeSlideUp 0.8s ease-out;
        }

        @keyframes fadeSlideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .breadcrumb {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 2rem;
            font-size: 0.85rem;
            color: var(--text-muted);
        }

        .breadcrumb a {
            color: var(--text-secondary);
            text-decoration: none;
            transition: color 0.2s;
        }

        .breadcrumb a:hover {
            color: var(--accent-primary);
        }

        .breadcrumb span {
            color: var(--text-muted);
        }

        .model-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: linear-gradient(135deg, rgba(62, 207, 142, 0.15), rgba(62, 207, 142, 0.05));
            border: 1px solid var(--border-color);
            padding: 0.4rem 1rem;
            border-radius: 100px;
            font-size: 0.75rem;
            font-weight: 500;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            color: var(--accent-primary);
            margin-bottom: 1.5rem;
        }

        .model-badge::before {
            content: '';
            width: 8px;
            height: 8px;
            background: var(--accent-primary);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(0.8); }
        }

        .model-title {
            font-family: 'Instrument Serif', serif;
            font-size: clamp(3rem, 8vw, 4.5rem);
            font-weight: 400;
            letter-spacing: -0.02em;
            line-height: 1.1;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, var(--text-primary) 0%, var(--text-secondary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .model-subtitle {
            font-family: 'Instrument Serif', serif;
            font-style: italic;
            font-size: 1.35rem;
            color: var(--text-secondary);
            margin-bottom: 2rem;
        }

        .header-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 2rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--border-subtle);
        }

        .meta-item {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }

        .meta-label {
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: var(--text-muted);
        }

        .meta-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
            color: var(--text-primary);
        }

        .meta-value a {
            color: var(--accent-blue);
            text-decoration: none;
            transition: color 0.2s;
        }

        .meta-value a:hover {
            color: var(--accent-primary);
            text-decoration: underline;
        }

        /* Main content */
        .content-grid {
            display: grid;
            gap: 2rem;
        }

        /* Section styling */
        .section {
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 16px;
            overflow: hidden;
            animation: fadeSlideUp 0.8s ease-out both;
        }

        .section:nth-child(1) { animation-delay: 0.1s; }
        .section:nth-child(2) { animation-delay: 0.2s; }
        .section:nth-child(3) { animation-delay: 0.3s; }
        .section:nth-child(4) { animation-delay: 0.4s; }
        .section:nth-child(5) { animation-delay: 0.5s; }

        .section-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1.25rem 1.5rem;
            cursor: pointer;
            transition: background 0.2s;
            user-select: none;
        }

        .section-header:hover {
            background: rgba(255, 255, 255, 0.02);
        }

        .section-title-wrapper {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .section-icon {
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--bg-tertiary);
            border-radius: 10px;
            color: var(--accent-primary);
        }

        .section-icon svg {
            width: 20px;
            height: 20px;
        }

        .section-title {
            font-family: 'Instrument Serif', serif;
            font-size: 1.35rem;
            font-weight: 400;
            color: var(--text-primary);
        }

        .section-toggle {
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--bg-tertiary);
            border-radius: 8px;
            transition: transform 0.3s ease, background 0.2s;
        }

        .section-toggle svg {
            width: 16px;
            height: 16px;
            color: var(--text-secondary);
            transition: transform 0.3s ease;
        }

        .section.expanded .section-toggle svg {
            transform: rotate(180deg);
        }

        .section-content {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.4s ease;
        }

        .section.expanded .section-content {
            max-height: 2000px;
        }

        .section-body {
            padding: 0 1.5rem 1.5rem;
        }

        .section-divider {
            height: 1px;
            background: var(--border-subtle);
            margin-bottom: 1.5rem;
        }

        /* Description section */
        .description-text {
            font-size: 1.05rem;
            color: var(--text-secondary);
            line-height: 1.85;
        }

        .description-text strong {
            color: var(--text-primary);
            font-weight: 500;
        }

        /* Components grid */
        .components-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 1rem;
        }

        .component-card {
            background: var(--bg-secondary);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            padding: 1.25rem;
            transition: all 0.3s ease;
            cursor: default;
        }

        .component-card:hover {
            border-color: var(--border-color);
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
        }

        .component-card.active {
            border-color: var(--accent-primary);
            background: linear-gradient(135deg, rgba(62, 207, 142, 0.08), transparent);
        }

        .component-card.inactive {
            opacity: 0.5;
        }

        .component-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            margin-bottom: 0.75rem;
        }

        .component-name {
            font-weight: 500;
            font-size: 0.95rem;
            color: var(--text-primary);
        }

        .component-status {
            font-size: 0.65rem;
            padding: 0.2rem 0.5rem;
            border-radius: 100px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .component-status.dynamic {
            background: rgba(62, 207, 142, 0.15);
            color: var(--accent-primary);
        }

        .component-status.omitted {
            background: rgba(240, 180, 41, 0.15);
            color: var(--accent-warm);
        }

        .component-alias {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-bottom: 0.5rem;
        }

        .component-description {
            font-size: 0.85rem;
            color: var(--text-secondary);
            line-height: 1.5;
        }

        /* Calendar section */
        .calendar-display {
            display: flex;
            align-items: stretch;
            gap: 2rem;
            flex-wrap: wrap;
        }

        .calendar-main {
            flex: 1;
            min-width: 280px;
        }

        .calendar-name {
            font-family: 'Instrument Serif', serif;
            font-size: 1.75rem;
            color: var(--text-primary);
            margin-bottom: 0.25rem;
        }

        .calendar-alias {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            color: var(--accent-blue);
            margin-bottom: 1rem;
        }

        .calendar-description {
            font-size: 0.95rem;
            color: var(--text-secondary);
            line-height: 1.75;
        }

        .calendar-meta {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            padding: 1.25rem;
            background: var(--bg-secondary);
            border-radius: 12px;
            border: 1px solid var(--border-subtle);
            min-width: 200px;
        }

        .calendar-meta-item {
            display: flex;
            flex-direction: column;
            gap: 0.2rem;
        }

        .calendar-meta-label {
            font-size: 0.65rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: var(--text-muted);
        }

        .calendar-meta-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            color: var(--text-primary);
        }

        /* Technical section */
        .tech-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
        }

        .tech-item {
            padding: 1.25rem;
            background: var(--bg-secondary);
            border-radius: 12px;
            border: 1px solid var(--border-subtle);
        }

        .tech-label {
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: var(--text-muted);
            margin-bottom: 0.5rem;
        }

        .tech-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
            color: var(--text-primary);
            word-break: break-all;
        }

        .tech-value a {
            color: var(--accent-blue);
            text-decoration: none;
            transition: color 0.2s;
        }

        .tech-value a:hover {
            color: var(--accent-primary);
        }

        /* Type badges */
        .type-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        .type-badge {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            padding: 0.35rem 0.75rem;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-subtle);
            border-radius: 6px;
            color: var(--text-secondary);
            transition: all 0.2s;
        }

        .type-badge:hover {
            border-color: var(--accent-purple);
            color: var(--accent-purple);
        }

        /* References */
        .references-list {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .reference-item {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem 1.25rem;
            background: var(--bg-secondary);
            border-radius: 10px;
            border: 1px solid var(--border-subtle);
            transition: all 0.2s;
            text-decoration: none;
        }

        .reference-item:hover {
            border-color: var(--accent-blue);
            transform: translateX(4px);
        }

        .reference-icon {
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--bg-tertiary);
            border-radius: 8px;
            color: var(--accent-blue);
            flex-shrink: 0;
        }

        .reference-icon svg {
            width: 18px;
            height: 18px;
        }

        .reference-text {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
            color: var(--text-primary);
        }

        .reference-arrow {
            margin-left: auto;
            color: var(--text-muted);
            transition: transform 0.2s, color 0.2s;
        }

        .reference-item:hover .reference-arrow {
            transform: translateX(4px);
            color: var(--accent-blue);
        }

        /* Footer */
        .footer {
            margin-top: 4rem;
            padding-top: 2rem;
            border-top: 1px solid var(--border-subtle);
            text-align: center;
            animation: fadeSlideUp 0.8s ease-out 0.6s both;
        }

        .footer-text {
            font-size: 0.85rem;
            color: var(--text-muted);
        }

        .footer-link {
            color: var(--accent-primary);
            text-decoration: none;
            transition: color 0.2s;
        }

        .footer-link:hover {
            color: var(--accent-blue);
        }

        /* Responsive */
        @media (max-width: 768px) {
            .container {
                padding: 2rem 1rem 3rem;
            }

            .header-meta {
                gap: 1.5rem;
            }

            .calendar-display {
                flex-direction: column;
            }

            .section-header {
                padding: 1rem 1.25rem;
            }

            .section-body {
                padding: 0 1.25rem 1.25rem;
            }
        }
    </style>
</head>
<body>
    <div class="noise-overlay"></div>
    <div class="gradient-bg"></div>

    <div class="container">
        <!-- Header -->
        <header class="header">
            <nav class="breadcrumb">
                <a href="https://emd.mipcvs.dev/">EMD Registry</a>
                <span>→</span>
                <a href="https://emd.mipcvs.dev/model/">Models</a>
                <span>→</span>
                <span>CNRM-ESM2-1e</span>
            </nav>

            <div class="model-badge">
                <span>Earth System Model</span>
            </div>

            <h1 class="model-title">CNRM-ESM2-1e</h1>
            <p class="model-subtitle">CNRM Earth System Model Version 2 — Emission-driven Configuration</p>

            <div class="header-meta">
                <div class="meta-item">
                    <span class="meta-label">Release Year</span>
                    <span class="meta-value">2018</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Model Family</span>
                    <span class="meta-value">cnrm-cm</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Validation Key</span>
                    <span class="meta-value">cnrm-esm2-1e</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Context</span>
                    <span class="meta-value">
                        <a href="https://emd.mipcvs.dev/model/cnrm-esm2-1e.json" target="_blank">JSON-LD →</a>
                    </span>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="content-grid">
            <!-- Description Section -->
            <section class="section expanded">
                <div class="section-header" onclick="toggleSection(this)">
                    <div class="section-title-wrapper">
                        <div class="section-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                        </div>
                        <h2 class="section-title">Description</h2>
                    </div>
                    <div class="section-toggle">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
                        </svg>
                    </div>
                </div>
                <div class="section-content">
                    <div class="section-body">
                        <div class="section-divider"></div>
                        <p class="description-text">
                            <strong>CNRM-ESM2-1e</strong> is the CNRM Earth System model version 2 designed for <strong>CMIP6</strong> on the basis of the physical core CNRM-CM6-1 (Voldoire et al. 2019). In concentration mode, it is the same model as CNRM-ESM2-1 (Séférian et al. 2019), it only differs from CNRM-ESM2-1 in <strong>emission-driven mode</strong> (see Bossert et al. 2026). The main adaptations consist in a better conservation of the carbon in all the components leading to a more consistent/realistic carbon flux evolution in historical simulations.
                        </p>
                    </div>
                </div>
            </section>

            <!-- Dynamic Components Section -->
            <section class="section expanded">
                <div class="section-header" onclick="toggleSection(this)">
                    <div class="section-title-wrapper">
                        <div class="section-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                            </svg>
                        </div>
                        <h2 class="section-title">Model Components</h2>
                    </div>
                    <div class="section-toggle">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
                        </svg>
                    </div>
                </div>
                <div class="section-content">
                    <div class="section-body">
                        <div class="section-divider"></div>
                        <div class="components-grid">
                            <!-- Aerosol -->
                            <div class="component-card active">
                                <div class="component-header">
                                    <span class="component-name">Aerosol</span>
                                    <span class="component-status dynamic">Dynamic</span>
                                </div>
                                <div class="component-alias">alias: aerosol</div>
                                <p class="component-description">Aerosol processes and atmospheric particulate matter dynamics</p>
                            </div>

                            <!-- Atmosphere -->
                            <div class="component-card active">
                                <div class="component-header">
                                    <span class="component-name">Atmosphere</span>
                                    <span class="component-status dynamic">Dynamic</span>
                                </div>
                                <div class="component-alias">alias: atmos</div>
                                <p class="component-description">Atmospheric circulation and thermodynamics</p>
                            </div>

                            <!-- Atmospheric Chemistry -->
                            <div class="component-card active">
                                <div class="component-header">
                                    <span class="component-name">Atmospheric Chemistry</span>
                                    <span class="component-status dynamic">Dynamic</span>
                                </div>
                                <div class="component-alias">key: atmospheric_chemistry</div>
                                <p class="component-description">Chemical processes and reactions in the atmosphere</p>
                            </div>

                            <!-- Land Surface -->
                            <div class="component-card active">
                                <div class="component-header">
                                    <span class="component-name">Land Surface</span>
                                    <span class="component-status dynamic">Dynamic</span>
                                </div>
                                <div class="component-alias">key: land_surface</div>
                                <p class="component-description">Terrestrial surface processes and land-atmosphere interactions</p>
                            </div>

                            <!-- Ocean -->
                            <div class="component-card active">
                                <div class="component-header">
                                    <span class="component-name">Ocean</span>
                                    <span class="component-status dynamic">Dynamic</span>
                                </div>
                                <div class="component-alias">alias: ocean</div>
                                <p class="component-description">Ocean circulation and physical oceanography</p>
                            </div>

                            <!-- Ocean Biogeochemistry -->
                            <div class="component-card active">
                                <div class="component-header">
                                    <span class="component-name">Ocean Biogeochemistry</span>
                                    <span class="component-status dynamic">Dynamic</span>
                                </div>
                                <div class="component-alias">key: ocean_biogeochemistry</div>
                                <p class="component-description">Marine biogeochemical cycles and carbon dynamics</p>
                            </div>

                            <!-- Sea Ice -->
                            <div class="component-card active">
                                <div class="component-header">
                                    <span class="component-name">Sea Ice</span>
                                    <span class="component-status dynamic">Dynamic</span>
                                </div>
                                <div class="component-alias">key: sea_ice</div>
                                <p class="component-description">Sea ice formation, extent, and dynamics</p>
                            </div>

                            <!-- Land Ice (Omitted) -->
                            <div class="component-card inactive">
                                <div class="component-header">
                                    <span class="component-name">Land Ice</span>
                                    <span class="component-status omitted">Omitted</span>
                                </div>
                                <div class="component-alias">key: land_ice</div>
                                <p class="component-description">Ice sheets and glaciers (not included in this configuration)</p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Calendar Section -->
            <section class="section">
                <div class="section-header" onclick="toggleSection(this)">
                    <div class="section-title-wrapper">
                        <div class="section-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                        </div>
                        <h2 class="section-title">Calendar System</h2>
                    </div>
                    <div class="section-toggle">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
                        </svg>
                    </div>
                </div>
                <div class="section-content">
                    <div class="section-body">
                        <div class="section-divider"></div>
                        <div class="calendar-display">
                            <div class="calendar-main">
                                <h3 class="calendar-name">Standard (Gregorian)</h3>
                                <div class="calendar-alias">gregorian</div>
                                <p class="calendar-description">
                                    Mixed Gregorian/Julian calendar as defined by UDUNITS. This is the default calendar assumed if no calendar attribute is specified. A deprecated alternative name for this calendar is 'gregorian'.
                                </p>
                            </div>
                            <div class="calendar-meta">
                                <div class="calendar-meta-item">
                                    <span class="calendar-meta-label">Identifier</span>
                                    <span class="calendar-meta-value">standard</span>
                                </div>
                                <div class="calendar-meta-item">
                                    <span class="calendar-meta-label">Validation Key</span>
                                    <span class="calendar-meta-value">standard</span>
                                </div>
                                <div class="calendar-meta-item">
                                    <span class="calendar-meta-label">Types</span>
                                    <span class="calendar-meta-value">wcrp:calendar, universal</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Technical Details Section -->
            <section class="section">
                <div class="section-header" onclick="toggleSection(this)">
                    <div class="section-title-wrapper">
                        <div class="section-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                            </svg>
                        </div>
                        <h2 class="section-title">Technical Details</h2>
                    </div>
                    <div class="section-toggle">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
                        </svg>
                    </div>
                </div>
                <div class="section-content">
                    <div class="section-body">
                        <div class="section-divider"></div>
                        <div class="tech-grid">
                            <div class="tech-item">
                                <div class="tech-label">Resource Identifier (@id)</div>
                                <div class="tech-value">cnrm-esm2-1e</div>
                            </div>
                            <div class="tech-item">
                                <div class="tech-label">JSON-LD Context</div>
                                <div class="tech-value">
                                    <a href="https://emd.mipcvs.dev/model/cnrm-esm2-1e.json" target="_blank">emd.mipcvs.dev/model/cnrm-esm2-1e.json</a>
                                </div>
                            </div>
                            <div class="tech-item">
                                <div class="tech-label">Resource Types (@type)</div>
                                <div class="type-badges">
                                    <span class="type-badge">emd</span>
                                    <span class="type-badge">wcrp:model</span>
                                    <span class="type-badge">esgvoc:Model</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- References Section -->
            <section class="section">
                <div class="section-header" onclick="toggleSection(this)">
                    <div class="section-title-wrapper">
                        <div class="section-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                            </svg>
                        </div>
                        <h2 class="section-title">References</h2>
                    </div>
                    <div class="section-toggle">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
                        </svg>
                    </div>
                </div>
                <div class="section-content">
                    <div class="section-body">
                        <div class="section-divider"></div>
                        <div class="references-list">
                            <a href="#" class="reference-item">
                                <div class="reference-icon">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                        <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                    </svg>
                                </div>
                                <span class="reference-text">REF001</span>
                                <span class="reference-arrow">→</span>
                            </a>
                            <a href="#" class="reference-item">
                                <div class="reference-icon">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                        <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                    </svg>
                                </div>
                                <span class="reference-text">REF002</span>
                                <span class="reference-arrow">→</span>
                            </a>
                        </div>
                    </div>
                </div>
            </section>
        </main>

        <!-- Footer -->
        <footer class="footer">
            <p class="footer-text">
                Data sourced from <a href="https://emd.mipcvs.dev/" class="footer-link" target="_blank">EMD Registry</a> · 
                Part of the <a href="https://wcrp-cmip.org/" class="footer-link" target="_blank">WCRP CMIP</a> initiative
            </p>
        </footer>
    </div>

    <script>
        function toggleSection(header) {
            const section = header.parentElement;
            section.classList.toggle('expanded');
        }

        // Expand first two sections by default (already done via HTML class)
        // Add smooth scroll behavior
        document.documentElement.style.scrollBehavior = 'smooth';
    </script>
</body>
</html>


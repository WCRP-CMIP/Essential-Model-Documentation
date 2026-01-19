<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CNRM-ESM2-1e | Earth System Model</title>
    <!-- MkDocs Material fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Akshar:wght@400;500;600&family=Roboto:wght@300;400;500;700&family=Roboto+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            /* MkDocs Material compatible variables */
            --md-text-font: "Roboto", sans-serif;
            --md-code-font: "Roboto Mono", monospace;
            --md-title-font: "Akshar", sans-serif;
            
            /* Light theme (default) */
            --md-default-fg-color: rgba(0, 0, 0, 0.87);
            --md-default-fg-color--light: rgba(0, 0, 0, 0.54);
            --md-default-fg-color--lighter: rgba(0, 0, 0, 0.32);
            --md-default-fg-color--lightest: rgba(0, 0, 0, 0.07);
            --md-default-bg-color: #fff;
            --md-default-bg-color--light: #f5f5f5;
            --md-primary-fg-color: #2196f3;
            --md-primary-fg-color--light: #64b5f6;
            --md-primary-fg-color--dark: #1976d2;
            --md-accent-fg-color: #ff9800;
            --md-code-bg-color: #f5f5f5;
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --md-default-fg-color: rgba(255, 255, 255, 0.87);
                --md-default-fg-color--light: rgba(255, 255, 255, 0.54);
                --md-default-fg-color--lighter: rgba(255, 255, 255, 0.32);
                --md-default-fg-color--lightest: rgba(255, 255, 255, 0.07);
                --md-default-bg-color: #1e1e1e;
                --md-default-bg-color--light: #2d2d2d;
                --md-code-bg-color: #2d2d2d;
            }
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: var(--md-text-font);
            background: var(--md-default-bg-color);
            color: var(--md-default-fg-color);
            line-height: 1.6;
            font-size: 0.8rem;
            min-height: 100vh;
        }

        .container {
            max-width: 61rem;
            margin: 0 auto;
            padding: 2rem 1.5rem 4rem;
        }

        /* Header */
        .header {
            margin-bottom: 3rem;
        }

        .breadcrumb {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 1.5rem;
            font-size: 0.75rem;
            color: var(--md-default-fg-color--light);
        }

        .breadcrumb a {
            color: var(--md-default-fg-color--light);
            text-decoration: none;
            transition: color 0.2s;
        }

        .breadcrumb a:hover {
            color: var(--md-primary-fg-color);
        }

        .model-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(33, 150, 243, 0.1);
            border: 1px solid rgba(33, 150, 243, 0.2);
            padding: 0.35rem 0.9rem;
            border-radius: 100px;
            font-size: 0.65rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--md-primary-fg-color);
            margin-bottom: 1rem;
        }

        .model-badge::before {
            content: '';
            width: 8px;
            height: 8px;
            background: var(--md-primary-fg-color);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(0.8); }
        }

        .model-title {
            font-family: var(--md-title-font);
            font-size: 2.5rem;
            font-weight: 600;
            line-height: 1.1;
            margin-bottom: 0.5rem;
            color: var(--md-default-fg-color);
        }

        .model-subtitle {
            font-size: 1rem;
            color: var(--md-default-fg-color--light);
            margin-bottom: 1.5rem;
            font-style: italic;
        }

        .header-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 2rem;
            padding-top: 1.25rem;
            border-top: 1px solid var(--md-default-fg-color--lightest);
        }

        .meta-item {
            display: flex;
            flex-direction: column;
            gap: 0.2rem;
        }

        .meta-label {
            font-size: 0.6rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: var(--md-default-fg-color--light);
            font-weight: 500;
        }

        .meta-value {
            font-family: var(--md-code-font);
            font-size: 0.8rem;
            color: var(--md-default-fg-color);
        }

        .meta-value a {
            color: var(--md-primary-fg-color);
            text-decoration: none;
            transition: color 0.2s;
        }

        .meta-value a:hover {
            text-decoration: underline;
        }

        /* Section styling */
        .section {
            background: var(--md-default-bg-color);
            border: 1px solid var(--md-default-fg-color--lightest);
            border-radius: 8px;
            margin-bottom: 1rem;
            overflow: hidden;
        }

        .section-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem 1.25rem;
            cursor: pointer;
            transition: background 0.2s;
            user-select: none;
        }

        .section-header:hover {
            background: var(--md-default-bg-color--light);
        }

        .section-title-wrapper {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .section-icon {
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--md-default-bg-color--light);
            border-radius: 8px;
            color: var(--md-primary-fg-color);
        }

        .section-icon svg {
            width: 18px;
            height: 18px;
        }

        .section-title {
            font-family: var(--md-title-font);
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--md-default-fg-color);
        }

        .section-toggle {
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--md-default-bg-color--light);
            border-radius: 6px;
        }

        .section-toggle svg {
            width: 14px;
            height: 14px;
            color: var(--md-default-fg-color--light);
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
            padding: 0 1.25rem 1.25rem;
        }

        .section-divider {
            height: 1px;
            background: var(--md-default-fg-color--lightest);
            margin-bottom: 1.25rem;
        }

        /* Description */
        .description-text {
            font-size: 0.85rem;
            color: var(--md-default-fg-color--light);
            line-height: 1.8;
        }

        .description-text strong {
            color: var(--md-default-fg-color);
            font-weight: 500;
        }

        /* Components grid */
        .components-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 0.75rem;
        }

        .component-card {
            background: var(--md-default-bg-color--light);
            border: 1px solid var(--md-default-fg-color--lightest);
            border-radius: 8px;
            padding: 1rem;
            transition: all 0.25s ease;
        }

        .component-card:hover {
            border-color: var(--md-primary-fg-color);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .component-card.active {
            border-left: 3px solid var(--md-primary-fg-color);
        }

        .component-card.inactive {
            opacity: 0.6;
            border-left: 3px solid var(--md-accent-fg-color);
        }

        .component-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            margin-bottom: 0.5rem;
        }

        .component-name {
            font-family: var(--md-title-font);
            font-weight: 600;
            font-size: 0.85rem;
            color: var(--md-default-fg-color);
        }

        .component-status {
            font-size: 0.55rem;
            padding: 0.15rem 0.45rem;
            border-radius: 100px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }

        .component-status.dynamic {
            background: rgba(76, 175, 80, 0.15);
            color: #4caf50;
        }

        .component-status.omitted {
            background: rgba(255, 152, 0, 0.15);
            color: #ff9800;
        }

        .component-alias {
            font-family: var(--md-code-font);
            font-size: 0.65rem;
            color: var(--md-default-fg-color--light);
            margin-bottom: 0.35rem;
        }

        .component-description {
            font-size: 0.75rem;
            color: var(--md-default-fg-color--light);
            line-height: 1.5;
        }

        /* Calendar */
        .calendar-display {
            display: flex;
            align-items: stretch;
            gap: 1.5rem;
            flex-wrap: wrap;
        }

        .calendar-main {
            flex: 1;
            min-width: 260px;
        }

        .calendar-name {
            font-family: var(--md-title-font);
            font-size: 1.3rem;
            font-weight: 600;
            color: var(--md-default-fg-color);
            margin-bottom: 0.2rem;
        }

        .calendar-alias {
            font-family: var(--md-code-font);
            font-size: 0.8rem;
            color: var(--md-primary-fg-color);
            margin-bottom: 0.75rem;
        }

        .calendar-description {
            font-size: 0.85rem;
            color: var(--md-default-fg-color--light);
            line-height: 1.7;
        }

        .calendar-meta {
            display: flex;
            flex-direction: column;
            gap: 0.6rem;
            padding: 1rem;
            background: var(--md-default-bg-color--light);
            border-radius: 8px;
            border: 1px solid var(--md-default-fg-color--lightest);
            min-width: 180px;
        }

        .calendar-meta-item {
            display: flex;
            flex-direction: column;
            gap: 0.15rem;
        }

        .calendar-meta-label {
            font-size: 0.55rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: var(--md-default-fg-color--light);
        }

        .calendar-meta-value {
            font-family: var(--md-code-font);
            font-size: 0.75rem;
            color: var(--md-default-fg-color);
        }

        /* Technical */
        .tech-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 1rem;
        }

        .tech-item {
            padding: 1rem;
            background: var(--md-default-bg-color--light);
            border-radius: 8px;
            border: 1px solid var(--md-default-fg-color--lightest);
        }

        .tech-label {
            font-size: 0.6rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: var(--md-default-fg-color--light);
            margin-bottom: 0.35rem;
        }

        .tech-value {
            font-family: var(--md-code-font);
            font-size: 0.8rem;
            color: var(--md-default-fg-color);
            word-break: break-all;
        }

        .tech-value a {
            color: var(--md-primary-fg-color);
            text-decoration: none;
        }

        .tech-value a:hover {
            text-decoration: underline;
        }

        .type-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
        }

        .type-badge {
            font-family: var(--md-code-font);
            font-size: 0.7rem;
            padding: 0.3rem 0.6rem;
            background: var(--md-default-bg-color--light);
            border: 1px solid var(--md-default-fg-color--lightest);
            border-radius: 4px;
            color: var(--md-default-fg-color--light);
            transition: all 0.2s;
        }

        .type-badge:hover {
            border-color: var(--md-primary-fg-color);
            color: var(--md-primary-fg-color);
        }

        /* References */
        .references-list {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .reference-item {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.75rem 1rem;
            background: var(--md-default-bg-color--light);
            border-radius: 8px;
            border: 1px solid var(--md-default-fg-color--lightest);
            transition: all 0.2s;
            text-decoration: none;
        }

        .reference-item:hover {
            border-color: var(--md-primary-fg-color);
            transform: translateX(4px);
        }

        .reference-icon {
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--md-default-bg-color);
            border-radius: 6px;
            color: var(--md-primary-fg-color);
            flex-shrink: 0;
        }

        .reference-icon svg {
            width: 16px;
            height: 16px;
        }

        .reference-text {
            font-family: var(--md-code-font);
            font-size: 0.8rem;
            color: var(--md-default-fg-color);
        }

        .reference-arrow {
            margin-left: auto;
            color: var(--md-default-fg-color--light);
            transition: transform 0.2s, color 0.2s;
        }

        .reference-item:hover .reference-arrow {
            transform: translateX(4px);
            color: var(--md-primary-fg-color);
        }

        /* Footer */
        .footer {
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--md-default-fg-color--lightest);
            text-align: center;
        }

        .footer-text {
            font-size: 0.75rem;
            color: var(--md-default-fg-color--light);
        }

        .footer-link {
            color: var(--md-primary-fg-color);
            text-decoration: none;
        }

        .footer-link:hover {
            text-decoration: underline;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .container {
                padding: 1.5rem 1rem 3rem;
            }

            .model-title {
                font-size: 2rem;
            }

            .header-meta {
                gap: 1.25rem;
            }

            .calendar-display {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="header">
            <nav class="breadcrumb">
                <a href="../">← Back to Documentation</a>
                <span>|</span>
                <a href="https://emd.mipcvs.dev/" target="_blank">EMD Registry</a>
                <span>→</span>
                <span>CNRM-ESM2-1e</span>
            </nav>

            <div class="model-badge">Earth System Model</div>

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
        <main>
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
                            <div class="component-card active">
                                <div class="component-header">
                                    <span class="component-name">Aerosol</span>
                                    <span class="component-status dynamic">Dynamic</span>
                                </div>
                                <div class="component-alias">alias: aerosol</div>
                                <p class="component-description">Aerosol processes and atmospheric particulate matter dynamics</p>
                            </div>

                            <div class="component-card active">
                                <div class="component-header">
                                    <span class="component-name">Atmosphere</span>
                                    <span class="component-status dynamic">Dynamic</span>
                                </div>
                                <div class="component-alias">alias: atmos</div>
                                <p class="component-description">Atmospheric circulation and thermodynamics</p>
                            </div>

                            <div class="component-card active">
                                <div class="component-header">
                                    <span class="component-name">Atmospheric Chemistry</span>
                                    <span class="component-status dynamic">Dynamic</span>
                                </div>
                                <div class="component-alias">key: atmospheric_chemistry</div>
                                <p class="component-description">Chemical processes and reactions in the atmosphere</p>
                            </div>

                            <div class="component-card active">
                                <div class="component-header">
                                    <span class="component-name">Land Surface</span>
                                    <span class="component-status dynamic">Dynamic</span>
                                </div>
                                <div class="component-alias">key: land_surface</div>
                                <p class="component-description">Terrestrial surface processes and land-atmosphere interactions</p>
                            </div>

                            <div class="component-card active">
                                <div class="component-header">
                                    <span class="component-name">Ocean</span>
                                    <span class="component-status dynamic">Dynamic</span>
                                </div>
                                <div class="component-alias">alias: ocean</div>
                                <p class="component-description">Ocean circulation and physical oceanography</p>
                            </div>

                            <div class="component-card active">
                                <div class="component-header">
                                    <span class="component-name">Ocean Biogeochemistry</span>
                                    <span class="component-status dynamic">Dynamic</span>
                                </div>
                                <div class="component-alias">key: ocean_biogeochemistry</div>
                                <p class="component-description">Marine biogeochemical cycles and carbon dynamics</p>
                            </div>

                            <div class="component-card active">
                                <div class="component-header">
                                    <span class="component-name">Sea Ice</span>
                                    <span class="component-status dynamic">Dynamic</span>
                                </div>
                                <div class="component-alias">key: sea_ice</div>
                                <p class="component-description">Sea ice formation, extent, and dynamics</p>
                            </div>

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
    </script>
</body>
</html>

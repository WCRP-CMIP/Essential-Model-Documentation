---
title: "CNRM-ESM2-1e"
description: "CNRM Earth System Model Version 2 — Emission-driven Configuration"
---

<style>
/* Model Info Page Custom Styles */
.model-hero {
    background: linear-gradient(135deg, rgba(33, 150, 243, 0.08) 0%, rgba(33, 150, 243, 0.02) 100%);
    border: 1px solid rgba(33, 150, 243, 0.15);
    border-radius: 12px;
    padding: 2rem;
    margin-bottom: 2rem;
}

.model-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(33, 150, 243, 0.12);
    border: 1px solid rgba(33, 150, 243, 0.25);
    padding: 0.35rem 0.9rem;
    border-radius: 100px;
    font-size: 0.7rem;
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
    font-family: "Akshar", sans-serif;
    font-size: 2.5rem;
    font-weight: 600;
    line-height: 1.1;
    margin: 0 0 0.5rem 0;
    color: var(--md-default-fg-color);
}

.model-subtitle {
    font-size: 1.1rem;
    color: var(--md-default-fg-color--light);
    margin: 0;
    font-style: italic;
}

.meta-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 1.5rem;
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--md-default-fg-color--lightest);
}

.meta-item {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
}

.meta-label {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--md-default-fg-color--light);
    font-weight: 500;
}

.meta-value {
    font-family: "Roboto Mono", monospace;
    font-size: 0.85rem;
    color: var(--md-default-fg-color);
}

.meta-value a {
    color: var(--md-primary-fg-color);
    text-decoration: none;
}

.meta-value a:hover {
    text-decoration: underline;
}

/* Components Grid */
.components-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 1rem;
    margin: 1.5rem 0;
}

.component-card {
    background: var(--md-code-bg-color);
    border: 1px solid var(--md-default-fg-color--lightest);
    border-radius: 10px;
    padding: 1.1rem;
    transition: all 0.25s ease;
}

.component-card:hover {
    border-color: var(--md-primary-fg-color);
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
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
    font-weight: 600;
    font-size: 0.9rem;
    color: var(--md-default-fg-color);
    font-family: "Akshar", sans-serif;
}

.component-status {
    font-size: 0.6rem;
    padding: 0.15rem 0.5rem;
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
    font-family: "Roboto Mono", monospace;
    font-size: 0.7rem;
    color: var(--md-default-fg-color--light);
    margin-bottom: 0.4rem;
}

.component-description {
    font-size: 0.8rem;
    color: var(--md-default-fg-color--light);
    line-height: 1.5;
    margin: 0;
}

/* Calendar Display */
.calendar-display {
    display: flex;
    gap: 2rem;
    flex-wrap: wrap;
    align-items: stretch;
}

.calendar-main {
    flex: 1;
    min-width: 280px;
}

.calendar-name {
    font-family: "Akshar", sans-serif;
    font-size: 1.4rem;
    font-weight: 600;
    margin: 0 0 0.25rem 0;
}

.calendar-alias {
    font-family: "Roboto Mono", monospace;
    font-size: 0.85rem;
    color: var(--md-primary-fg-color);
    margin-bottom: 0.75rem;
}

.calendar-description {
    font-size: 0.9rem;
    color: var(--md-default-fg-color--light);
    line-height: 1.7;
}

.calendar-meta {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    padding: 1.1rem;
    background: var(--md-code-bg-color);
    border-radius: 10px;
    border: 1px solid var(--md-default-fg-color--lightest);
    min-width: 180px;
}

.calendar-meta-item {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
}

.calendar-meta-label {
    font-size: 0.6rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--md-default-fg-color--light);
}

.calendar-meta-value {
    font-family: "Roboto Mono", monospace;
    font-size: 0.8rem;
    color: var(--md-default-fg-color);
}

/* Technical Details */
.tech-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem;
    margin: 1rem 0;
}

.tech-item {
    padding: 1rem;
    background: var(--md-code-bg-color);
    border-radius: 8px;
    border: 1px solid var(--md-default-fg-color--lightest);
}

.tech-label {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--md-default-fg-color--light);
    margin-bottom: 0.4rem;
}

.tech-value {
    font-family: "Roboto Mono", monospace;
    font-size: 0.85rem;
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

/* Type Badges */
.type-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
}

.type-badge {
    font-family: "Roboto Mono", monospace;
    font-size: 0.7rem;
    padding: 0.3rem 0.6rem;
    background: var(--md-default-fg-color--lightest);
    border: 1px solid var(--md-default-fg-color--lighter);
    border-radius: 4px;
    color: var(--md-default-fg-color--light);
    transition: all 0.2s;
}

.type-badge:hover {
    border-color: var(--md-primary-fg-color);
    color: var(--md-primary-fg-color);
}

/* JSON-LD Section */
.jsonld-section {
    margin-top: 1.5rem;
}

.jsonld-section summary {
    cursor: pointer;
    font-weight: 500;
    padding: 0.5rem 0;
    color: var(--md-default-fg-color--light);
}

.jsonld-section summary:hover {
    color: var(--md-primary-fg-color);
}
</style>

<div class="model-hero">
    <div class="model-badge">Earth System Model</div>
    <h1 class="model-title">CNRM-ESM2-1e</h1>
    <p class="model-subtitle">CNRM Earth System Model Version 2 — Emission-driven Configuration</p>
    <div class="meta-grid">
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
            <span class="meta-value"><a href="https://emd.mipcvs.dev/model/cnrm-esm2-1e.json" target="_blank">JSON-LD ↗</a></span>
        </div>
    </div>
</div>

## Description

**CNRM-ESM2-1e** is the CNRM Earth System model version 2 designed for **CMIP6** on the basis of the physical core [CNRM-CM6-1](https://doi.org/10.1029/2019MS001683) (Voldoire et al. 2019). In concentration mode, it is the same model as [CNRM-ESM2-1](https://doi.org/10.1029/2019MS001791) (Séférian et al. 2019), it only differs from CNRM-ESM2-1 in **emission-driven mode** (see Bossert et al. 2026). 

The main adaptations consist in a better conservation of the carbon in all the components leading to a more consistent/realistic carbon flux evolution in historical simulations.

---

## Model Components

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

---

## Calendar System

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

---

## Technical Details

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
</div>

<div class="tech-item" style="margin-top: 1rem;">
    <div class="tech-label">Resource Types (@type)</div>
    <div class="type-badges" style="margin-top: 0.5rem;">
        <span class="type-badge">emd</span>
        <span class="type-badge">wcrp:model</span>
        <span class="type-badge">esgvoc:Model</span>
    </div>
</div>

---

## References

| ID | Description |
|---|---|
| REF001 | Primary model reference |
| REF002 | Additional documentation |

---

## Related Links

- [EMD Registry](https://emd.mipcvs.dev/) — Model metadata registry
- [WCRP CMIP](https://wcrp-cmip.org/) — Climate Model Intercomparison Project
- [JSON-LD Specification](https://json-ld.org/) — Linked data format

---

<details class="jsonld-section">
<summary>View Raw JSON-LD</summary>

```json
{
  "@context": "https://emd.mipcvs.dev/model/cnrm-esm2-1e.json",
  "@id": "cnrm-esm2-1e",
  "@type": ["emd", "wcrp:model", "esgvoc:Model"],
  "calendar": {
    "@id": "standard",
    "@type": ["wcrp:calendar", "esgvoc:Calendar", "universal"],
    "alias": "gregorian",
    "description": "Mixed Gregorian/Julian calendar as defined by UDUNITS...",
    "ui_label": "Standard (Gregorian)",
    "validation_key": "standard"
  },
  "description": "CNRM-ESM2-1e is the CNRM Earth System model version 2...",
  "dynamic_components": ["aerosol", "atmosphere", "atmospheric_chemistry", 
                         "land_surface", "ocean", "ocean_biogeochemistry", "sea_ice"],
  "family": "cnrm-cm",
  "name": "CNRM-ESM2-1e",
  "omitted_components": "land_ice",
  "release_year": 2018,
  "validation_key": "cnrm-esm2-1e"
}
```

</details>

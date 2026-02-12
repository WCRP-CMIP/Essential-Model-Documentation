# EMD Registration Workflow

## Submission Pipeline

```mermaid
flowchart LR
    subgraph Stage1["**Stage 1**"]
        S1["Grid Cells & Subgrid"]
    end

    subgraph Stage2["**Stage 2**"]
        direction TB
        S2a["Horizontal Grid"]
        S2b["Vertical Grid"]
    end

    subgraph MF["**Model Family**"]
        direction TB
        ESM["Earth System Family"]
        CF["Component Family"]
    end

    subgraph Stage3["**Stage 3**"]
        S3["Model Component"]
    end

    subgraph Stage4["**Stage 4**"]
        S4["Model"]
    end

    S1 -->|g###, s###| S2a
    S2a -->|c###| S3
    S2b -->|v###| S3
    S3 -->|config ID| S4
    ESM -.->|family-id| S4
    CF -.->|family-id| S3

    click S1 "https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=grid_cell_and_subgrid.yml" _blank
    click S2a "https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_computational_grid.yml" _blank
    click S2b "https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=vertical_computational_grid.yml" _blank
    click S3 "https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_component.yml" _blank
    click S4 "https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model.yml" _blank
    click ESM "https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml" _blank
    click CF "https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml" _blank

    style Stage1 stroke:#333,stroke-width:2px,fill:none
    style Stage2 stroke:#333,stroke-width:2px,fill:none
    style MF stroke:#333,stroke-width:2px,fill:none
    style Stage3 stroke:#333,stroke-width:2px,fill:none
    style Stage4 stroke:#333,stroke-width:2px,fill:none
```

## Quick Reference

| Stage | Form | Creates | ID Format | Used By |
|-------|------|---------|-----------|---------|
| 1 | [Grid Cells & Subgrid](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=grid_cell_and_subgrid.yml) | grid_cells + subgrid | g###, s### | Stage 2a |
| 2a | [Horizontal Grid](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_computational_grid.yml) | horizontal_computational_grid | c### | Stage 3 |
| 2b | [Vertical Grid](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=vertical_computational_grid.yml) | vertical_computational_grid | v### | Stage 3 |
| 3 | [Model Component](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_component.yml) | component + component_config | {domain}_{name}_{c###}_{v###} | Stage 4 |
| 4 | [Model](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model.yml) | model | source_id | CMIP |
| — | [Earth System Family](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml) | model_family | family-id | Stage 4 |
| — | [Component Family](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml) | model_family | family-id | Stage 3 |

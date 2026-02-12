# Essential-Model-Documentation
TESTING ONLY: Development repository for the EMD. This will link into the CVs and Universe Repos. 


[![Update Issue Templates](https://github.com/WCRP-CMIP/Essential-Model-Documentation/actions/workflows/issue-templates.yml/badge.svg)](https://github.com/WCRP-CMIP/Essential-Model-Documentation/actions/workflows/issue-templates.yml) [![∆ src-data](https://github.com/WCRP-CMIP/Essential-Model-Documentation/actions/workflows/src-data-change.yml/badge.svg?branch=src-data)](https://github.com/WCRP-CMIP/Essential-Model-Documentation/actions/workflows/src-data-change.yml)
[![→ workflows](https://github.com/WCRP-CMIP/Essential-Model-Documentation/actions/workflows/sync-workflows.yml/badge.svg)](https://github.com/WCRP-CMIP/Essential-Model-Documentation/actions/workflows/sync-workflows.yml)

-------

> [!CAUTION]
> ### THIS REPOSITORY IS CURRENTLY UNDER ACTIVE DEVELOPMENT

--------

## Submitting EMD 
The submission process for the Essential Model Documentation (EMD) follows a 4 stage process. If your grids and model/component families have already been registered from previous projects, please start at Stage 3 (blue). Otherwise start at the beginning and ensure your grid cells, grids and families have been added. Subsequent submissions should get progressively quicker the more information that has been entered in the EMD. 
 
```mermaid
flowchart LR
    %% HIGHLIGHT A STAGE: Change the style at the bottom to highlight
    %% Options: Stage1, Stage2, MF, Stage3, Stage4

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

    %% DEFAULT STYLES
    style Stage1 stroke:#333,stroke-width:2px,fill:none
    style Stage2 stroke:#333,stroke-width:2px,fill:none
    style MF stroke:#333,stroke-width:2px,fill:none
    style Stage3 stroke:#333,stroke-width:2px,fill:none
    style Stage4 stroke:#333,stroke-width:2px,fill:none

    %% HIGHLIGHT - Edit this line to change highlight (comment out for no highlight)
    %%    style Stage3 stroke:#0066cc,stroke-width:3px,fill:none

    style Stage3 stroke:#0066cc,stroke-width:3px,fill:none
```



## JSON branch structure (ignore these and use esgvoc for now)

| Required |  |
|--------|-------------|
| [`main`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/tree/main) | The landing page directing users to the relevant content. |
| [`docs`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/tree/docs) | Contains the documentation and is version-controlled. This is the branch where documentation edits are made. Actions and automations (e.g., workflows that update docs or summaries) are also configured from this branch. |
| [`src-data`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/tree/src-data) | Stores the JSONLD content used to link all files. Updates here trigger automated workflows that identify changed JSON files and update documentation or summaries accordingly. |
| [`production`](https://github.com/WCRP-CMIP/Essential-Model-Documentation/tree/production) | Not for user digestion. Hosts the compiled documentation and JSONLD files, as well as the static pages site. Updated automatically via workflows when changes in `src-data` or `docs` are processed. |



| Optional |  |
|--------|-------------|
| `dev_*` | Other branches used for updating things. |
| `*` | All other branches are usually ones containing submissions to update the content. |





## Contributors

[![Contributors](https://contrib.rocks/image?repo=WCRP-CMIP/Essential-Model-Documentation)](https://github.com/WCRP-CMIP/Essential-Model-Documentation/graphs/contributors)

Thanks to our contributors!

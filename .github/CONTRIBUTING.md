# Contribution Guidelines
The full description on how to submit new data is available in the documentation (link below). 


The following sections will contain links to:

1. Forms for the submission of new data
2. Prefilled links for existing content, this can be used for modification, or adaption when submitting/reusing entries. 


Please ensure that any additions or modifications to controlled vocabularies adhere to the established standards and formats. Refer to the [Documentation](https://emd.mipcvs.dev/doc) for guidance.


## 1. Submitting New Controlled Vocabularies

The following forms are available for this repository, and can be used to add or modify entries. The complete submission pipeline (if applicable) will be outlined in the section above.

### Stage 1 - Grid Cells

### Stage 2 - Computational Grids

- [horizontal_computational_grid](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_computational_grid.yml)
- [vertical_computational_grid](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=vertical_computational_grid.yml)
### Stage 3 - Components

- [model_component](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_component.yml)
### Stage 4 - Model

- [model](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model.yml)
### Supporting

- [model_family](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml)
- [general_issue](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=general_issue.yml)
### Ungrouped Forms

- [horizontal_grid_cell](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_grid_cell.yml)

## 2. Modifying or reusing existing entries

The following links will open pre-filled GitHub issues with content from the selected files. These can be used to update entries or make new ones. 

<details markdown="1" name="horizontal_computational_grid">
<summary>Horizontal Computational Grid (4 entries)</summary>

- [h100](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_computational_grid.yml&title=Modify%3A+Horizontal+Computational+Grid%3A+h100&issue_kind=%22Modify%22&description=Arakawa-A+spectral+grid+for+atmospheric+modelling+%28TL127+reduced+Gaussian+%2B+regular+output+grid%29.&horizontal_subgrids=%22s100%22%2C%22s101%22&arrangement=%22arakawa-a%22)

- [h101](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_computational_grid.yml&title=Modify%3A+Horizontal+Computational+Grid%3A+h101&issue_kind=%22Modify%22&description=Arakawa-C+grid+on+an+ocean+tripolar+configuration+%28eORCA1%29.&horizontal_subgrids=%22s102%22%2C%22s105%22%2C%22s106%22&arrangement=%22arakawa-c%22)

- [h102](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_computational_grid.yml&title=Modify%3A+Horizontal+Computational+Grid%3A+h102&issue_kind=%22Modify%22&description=Arakawa-C+grid+with+adaptive+mesh+refinement+for+ice+sheet+modelling.&horizontal_subgrids=%22s103%22&arrangement=%22arakawa-c%22)

- [h103](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_computational_grid.yml&title=Modify%3A+Horizontal+Computational+Grid%3A+h103&issue_kind=%22Modify%22&description=Arakawa-A+grid+on+a+regular+latitude-longitude+configuration+for+land+surface+modelling.&horizontal_subgrids=%22s104%22&arrangement=%22arakawa-a%22)

</details>

<details markdown="1" name="horizontal_grid_cell">
<summary>Horizontal Grid Cell (12 entries)</summary>

- [g100](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_grid_cell.yml&title=Modify%3A+Horizontal+Grid+Cell%3A+g100&issue_kind=%22Modify%22&truncation_method=%22None%22&y_resolution=0.9&region=%22global%22&n_cells=55296&southernmost_latitude=-89.5&truncation_number=None&units=%22degree%22&grid_mapping=%22latitude_longitude%22&westernmost_longitude=0.5&temporal_refinement=%22static%22&x_resolution=1.25&grid_type=%22regular_latitude_longitude%22)

- [g101](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_grid_cell.yml&title=Modify%3A+Horizontal+Grid+Cell%3A+g101&issue_kind=%22Modify%22&truncation_method=%22triangular%22&y_resolution=1.4&region=%22global%22&n_cells=24572&southernmost_latitude=-88.9277353522076&truncation_number=127&units=%22degree%22&grid_mapping=%22latitude_longitude%22&westernmost_longitude=0.0&temporal_refinement=%22static%22&x_resolution=1.4&grid_type=%22linear_spectral_gaussian%22)

- [g102](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_grid_cell.yml&title=Modify%3A+Horizontal+Grid+Cell%3A+g102&issue_kind=%22Modify%22&truncation_method=%22None%22&y_resolution=None&region=%22global%22&n_cells=105704&southernmost_latitude=None&truncation_number=None&units=%22None%22&grid_mapping=%22latitude_longitude%22&westernmost_longitude=None&temporal_refinement=%22static%22&x_resolution=None&grid_type=%22tripolar%22)

- [g103](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_grid_cell.yml&title=Modify%3A+Horizontal+Grid+Cell%3A+g103&issue_kind=%22Modify%22&truncation_method=%22None%22&y_resolution=None&region=%22greenland%22%2C%22antarctica%22&n_cells=None&southernmost_latitude=None&truncation_number=None&units=%22None%22&grid_mapping=%22polar_stereographic%22&westernmost_longitude=None&temporal_refinement=%22adaptive%22&x_resolution=None&grid_type=%22plane_projection%22)

- [g104](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_grid_cell.yml&title=Modify%3A+Horizontal+Grid+Cell%3A+g104&issue_kind=%22Modify%22&truncation_method=%22None%22&y_resolution=0.9&region=%22global%22&n_cells=55296&southernmost_latitude=-89.65&truncation_number=None&units=%22degree%22&grid_mapping=%22latitude_longitude%22&westernmost_longitude=0.0&temporal_refinement=%22static%22&x_resolution=1.25&grid_type=%22regular_latitude_longitude%22)

- [g105](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_grid_cell.yml&title=Modify%3A+Horizontal+Grid+Cell%3A+g105&issue_kind=%22Modify%22&truncation_method=%22None%22&y_resolution=None&region=%22global%22&n_cells=105705&southernmost_latitude=None&truncation_number=None&units=%22None%22&grid_mapping=%22latitude_longitude%22&westernmost_longitude=None&temporal_refinement=%22static%22&x_resolution=None&grid_type=%22tripolar%22)

- [g106](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_grid_cell.yml&title=Modify%3A+Horizontal+Grid+Cell%3A+g106&issue_kind=%22Modify%22&truncation_method=%22None%22&y_resolution=None&region=%22global%22&n_cells=105706&southernmost_latitude=None&truncation_number=None&units=%22None%22&grid_mapping=%22latitude_longitude%22&westernmost_longitude=None&temporal_refinement=%22static%22&x_resolution=None&grid_type=%22tripolar%22)

- [g107](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_grid_cell.yml&title=Modify%3A+Horizontal+Grid+Cell%3A+g107&issue_kind=%22Modify%22&truncation_method=%22%22&y_resolution=1&region=%22global%22&southernmost_latitude=-89.5&truncation_number=&units=%22degree%22&westernmost_longitude=0.5&temporal_refinement=%22static%22&x_resolution=1&grid_type=%22regular_latitude_longitude%22)

- [g108](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_grid_cell.yml&title=Modify%3A+Horizontal+Grid+Cell%3A+g108&issue_kind=%22Modify%22&truncation_method=%22%22&y_resolution=1.25&region=%22global%22&southernmost_latitude=-89.375&truncation_number=&units=%22degree%22&westernmost_longitude=0.9375&temporal_refinement=%22static%22&x_resolution=1.875&grid_type=%22regular_latitude_longitude%22)

- [g109](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_grid_cell.yml&title=Modify%3A+Horizontal+Grid+Cell%3A+g109&issue_kind=%22Modify%22&truncation_method=%22%22&y_resolution=1.25&region=%22global%22&southernmost_latitude=-89.375&truncation_number=&units=%22degree%22&westernmost_longitude=0&temporal_refinement=%22static%22&x_resolution=1.875&grid_type=%22regular_latitude_longitude%22)

- [g110](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_grid_cell.yml&title=Modify%3A+Horizontal+Grid+Cell%3A+g110&issue_kind=%22Modify%22&truncation_method=%22%22&y_resolution=&region=%22global%22&southernmost_latitude=&truncation_number=&units=%22%22&westernmost_longitude=&temporal_refinement=%22static%22&x_resolution=&grid_type=%22tripolar%22)

- [g111](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_grid_cell.yml&title=Modify%3A+Horizontal+Grid+Cell%3A+g111&issue_kind=%22Modify%22&truncation_method=%22%22&y_resolution=1.25&region=%22global%22&southernmost_latitude=-89.375&truncation_number=&units=%22degree%22&westernmost_longitude=0.9375&temporal_refinement=%22static%22&x_resolution=1.875&grid_type=%22regular_latitude_longitude%22)

</details>

<details markdown="1" name="model">
<summary>Model (1 entries)</summary>

- [cnrm-esm2-1e](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model.yml&title=Modify%3A+Model%3A+cnrm-esm2-1e&issue_kind=%22Modify%22&prescribed_components=&dynamic_components=%22Aerosol%22%2C%22Atmosphere%22%2C%22Atmospheric+Chemistry%22%2C%22land-surface%22%2C%22Ocean%22%2C%22Ocean+Biogeochemistry%22%2C%22Sea+Ice%22&description=CNRM-ESM2-1e+is+the+CNRM+Earth+System+model+version+2+designed+for+CMIP6+on+the+basis+of+the+physical+core+CNRM-CM6-1+%28Voldoire+et+al.+2019%29.+In+concentration+mode%2C+it+is+the+same+model+as+CNRM-ESM2-1+%28S%C3%A9f%C3%A9rian+et+al.+2019%29%2C+it+only+differs+from+CNRM-ESM2-1+in+emission-driven+mode+%28see+Bossert+et+al.+2026%29.+The+main+adaptations+consist+in+a+better+conservation+of+the+carbon+in+all+the+components+leading+to+a+more+consistent%2Frealistic+carbon+flux+evolution+in+historical+simulations.&calendar=%22standard%22&release_year=2018&family=%22CNRM-CM%22&component_configs=%22atmosphere_arpege-climat-version-6-3_h100_v100%22%2C%22land-surface_surfex-v8-modeling-platform_h100_v102%22%2C%22ocean_nemo-v3-6_h101_v103%22%2C%22aerosol_tactic_h100_v100%22%2C%22atmospheric-chemistry_reprobus-c-v2-0_h100_v100%22%2C%22sea-ice_gelato_h101_v104%22%2C%22ocean-biogeochemistry_piscesv2-gas_h101_v103%22&name=CNRM-ESM2-1e&omitted_components=%22Land+Ice%22&embedded_components=%22%5B%27atmosphere%27%2C+%27aerosol%27%5D%22%2C%22%5B%27atmosphere%27%2C+%27atmospheric-chemistry%27%5D%22%2C%22%5B%27ocean%27%2C+%27sea-ice%27%5D%22%2C%22%5B%27ocean%27%2C+%27ocean-biogeochemistry%27%5D%22)

</details>

<details markdown="1" name="model_component">
<summary>Model Component (10 entries)</summary>

- [arpege-climat_version_6_3](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_component.yml&title=Modify%3A+Model+Component%3A+arpege-climat_version_6_3&issue_kind=%22Modify%22&component=%22atmosphere%22&description=ARPEGE-Climat+Version+6.3+is+the+atmospheric+component+of+the+CNRM+climate+and+Earth+System+models+%28CNRM-CM6-1+and+CNRM-ESM2-1%29.&code_base=private&family=%22arpege-climat%22&name=Arpege-Climat+Version+6.3)

- [bisicles-ukesm-ismip6-1_0](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_component.yml&title=Modify%3A+Model+Component%3A+bisicles-ukesm-ismip6-1_0&issue_kind=%22Modify%22&component=%22land_ice%22&description=UniCiCles+%28Unified+Model-CISM-BISICLES%29+is+a+package+combining+BISICLES+with+an+interface+that+obtains+boundary+conditions+from+Unified+Model+or+JULES+data.&code_base=none&family=%22BISICLES%22&name=BISICLES-UKESM-ISMIP6-1.0)

- [clm4](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_component.yml&title=Modify%3A+Model+Component%3A+clm4&issue_kind=%22Modify%22&component=%22land_surface%22&description=The+Community+Land+Model+represents+several+aspects+of+the+land+surface+including+surface+heterogeneity+through+a+nested+subgrid+hierarchy.&code_base=none&family=%22CLM%22&name=CLM4)

- [gelato](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_component.yml&title=Modify%3A+Model+Component%3A+gelato&issue_kind=%22Modify%22&component=%22sea_ice%22&description=Global+Experimental+Leads+and+sea+ice+for+ATmosphere+and+Ocean.&code_base=private&family=%22gelato%22&name=GELATO)

- [hadam3](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_component.yml&title=Modify%3A+Model+Component%3A+hadam3&issue_kind=%22Modify%22&component=%22atmosphere%22&description=HadAM3+is+the+atmospheric+component+of+HadCM3%2C+a+coupled+atmosphere-ocean+general+circulation+model+developed+at+the+UK+Met+Office+Hadley+Centre.&code_base=none&family=%22hadam%22&name=HadAM3)

- [nemo_v3_6](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_component.yml&title=Modify%3A+Model+Component%3A+nemo_v3_6&issue_kind=%22Modify%22&component=%22ocean%22&description=Nucleus+for+European+Modelling+of+the+Ocean+version+3.6+%28OPA%29.&code_base=private&family=%22nemo%22&name=NEMO+v3.6)

- [piscesv2-gas](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_component.yml&title=Modify%3A+Model+Component%3A+piscesv2-gas&issue_kind=%22Modify%22&component=%22ocean_biogeochemistry%22&description=Pelagic+Interaction+Scheme+for+Carbon+and+Ecosystem+Studies+model+volume+2+version+trace+gases.&code_base=https%3A%2F%2Fgitlab.in2p3.fr%2Fpisco%2Fpisces-gas%2Fpisces-gas&family=%22pisces%22&name=PISCESv2-gas)

- [reprobus-c_v2_0](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_component.yml&title=Modify%3A+Model+Component%3A+reprobus-c_v2_0&issue_kind=%22Modify%22&component=%22atmospheric_chemistry%22&description=The+chemistry+scheme+of+CNRM-ESM2+is+an+on-line+scheme+whereby+the+chemistry+routines+are+part+of+the+physics+of+the+atmospheric+climate+model.&code_base=private&family=%22reprobus%22&name=REPROBUS-C+%28v2.0%29)

- [surfex_v8_modeling_platform](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_component.yml&title=Modify%3A+Model+Component%3A+surfex_v8_modeling_platform&issue_kind=%22Modify%22&component=%22land_surface%22&description=SURFEXv8.0+encompasses+several+submodules+for+modeling+the+interactions+between+the+atmosphere%2C+the+ocean%2C+the+lakes+and+the+land+surface.&code_base=https%3A%2F%2Fwww.umr-cnrm.fr%2Fsurfex%2Fspip.php%3Frubrique8&family=%22surfex%22&name=SURFEX+v8+modeling+platform)

- [tactic](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_component.yml&title=Modify%3A+Model+Component%3A+tactic&issue_kind=%22Modify%22&component=%22aerosol%22&description=TACTIC+%28Tropospheric+Aerosols+for+ClimaTe+In+CNRM%29+is+an+interactive+tropospheric+aerosol+scheme%2C+able+to+represent+the+main+anthropogenic+and+natural+aerosol+types+in+the+troposphere.&code_base=private&family=%22tactic%22&name=TACTIC)

</details>

<details markdown="1" name="model_family">
<summary>Model Family (30 entries)</summary>

- [ACCESS](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+ACCESS&issue_kind=%22Modify%22&collaborative_institutions=%22bom%22&established=none&description=Australian+Community+Climate+and+Earth+System+Simulator+-+a+coupled+climate+and+Earth+system+model+developed+by+the+Australian+climate+research+community.&representative_member=none&website=none&primary_institution=%22CSIRO%22&family_type=%22model%22&scientific_domains=%22atmosphere%22%2C%22land_surface%22%2C%22ocean%22%2C%22sea_ice%22)

- [BCC-CSM](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+BCC-CSM&issue_kind=%22Modify%22&collaborative_institutions=&established=none&description=Beijing+Climate+Center+Climate+System+Model.&representative_member=none&website=none&primary_institution=%22bcc%22&family_type=%22model%22&scientific_domains=%22atmosphere%22%2C%22land_surface%22%2C%22ocean%22)

- [BISICLES](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+BISICLES&issue_kind=%22Modify%22&collaborative_institutions=%22uob%22%2C%22BAS%22&established=2008&description=BISICLES+uses+adaptive-mesh+Chombo+libraries+for+ice+sheet+modeling+with+SSA-+momentum+approximation.&representative_member=BISICLES-UKESM-ISMIP6-1.0&website=https%3A%2F%2Fbisicles.lbl.gov%2F&primary_institution=%22lbnl%22&family_type=%22component%22&scientific_domains=%22land_ice%22)

- [CAM](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+CAM&issue_kind=%22Modify%22&collaborative_institutions=&established=none&description=Community+Atmosphere+Model+-+the+atmospheric+component+of+CESM%2C+also+used+standalone+for+atmospheric+research.&representative_member=none&website=none&primary_institution=%22NCAR%22&family_type=%22component%22&scientific_domains=%22atmosphere%22)

- [CESM](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+CESM&issue_kind=%22Modify%22&collaborative_institutions=&established=none&description=Community+Earth+System+Model+-+a+fully-coupled+global+climate+model+developed+at+NCAR+providing+simulations+of+the+Earth%27s+past%2C+present%2C+and+future+climate+states.&representative_member=none&website=none&primary_institution=%22NCAR%22&family_type=%22model%22&scientific_domains=%22atmosphere%22%2C%22land_surface%22%2C%22ocean%22%2C%22sea_ice%22%2C%22ocean_biogeochemistry%22)

- [CLM](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+CLM&issue_kind=%22Modify%22&collaborative_institutions=%22lbnl%22%2C%22PNNL%22&established=1996&description=Community+Land+Model+family+representing+land+surface+heterogeneity+through+nested+subgrid+hierarchy.&representative_member=CLM4&website=https%3A%2F%2Fwww.cesm.ucar.edu%2Fmodels%2Fcesm2%2Fland&primary_institution=%22NCAR%22&family_type=%22component%22&scientific_domains=%22land_surface%22%2C%22ocean_biogeochemistry%22)

- [CNRM-CM](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+CNRM-CM&issue_kind=%22Modify%22&collaborative_institutions=&established=none&description=Centre+National+de+Recherches+M%C3%A9t%C3%A9orologiques+coupled+climate+model+family.&representative_member=none&website=none&primary_institution=%22cnrm-cerfacs%22&family_type=%22model%22&scientific_domains=%22atmosphere%22%2C%22land_surface%22%2C%22ocean%22)

- [CanESM](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+CanESM&issue_kind=%22Modify%22&collaborative_institutions=&established=none&description=Canadian+Earth+System+Model+-+developed+by+the+Canadian+Centre+for+Climate+Modelling+and+Analysis.&representative_member=none&website=none&primary_institution=%22CCCma%22&family_type=%22model%22&scientific_domains=%22atmosphere%22%2C%22land_surface%22%2C%22ocean%22%2C%22sea_ice%22)

- [EC-Earth](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+EC-Earth&issue_kind=%22Modify%22&collaborative_institutions=&established=none&description=Community-developed+Earth+system+model+based+on+the+ECMWF+Integrated+Forecasting+System+%28IFS%29.&representative_member=none&website=none&primary_institution=%22EC-Earth-Consortium%22&family_type=%22model%22&scientific_domains=%22atmosphere%22%2C%22land_surface%22%2C%22ocean%22%2C%22sea_ice%22)

- [FGOALS](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+FGOALS&issue_kind=%22Modify%22&collaborative_institutions=&established=none&description=Flexible+Global+Ocean-Atmosphere-Land+System+Model+-+developed+by+the+Institute+of+Atmospheric+Physics%2C+Chinese+Academy+of+Sciences.&representative_member=none&website=none&primary_institution=%22cas%22&family_type=%22model%22&scientific_domains=%22atmosphere%22%2C%22land_surface%22%2C%22ocean%22)

- [GEOS](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+GEOS&issue_kind=%22Modify%22&collaborative_institutions=&established=none&description=Goddard+Earth+Observing+System+-+NASA%27s+atmospheric+general+circulation+model.&representative_member=none&website=none&primary_institution=%22nasa-gsfc%22&family_type=%22component%22&scientific_domains=%22atmosphere%22)

- [GFDL-CM4](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+GFDL-CM4&issue_kind=%22Modify%22&collaborative_institutions=&established=none&description=NOAA+Geophysical+Fluid+Dynamics+Laboratory+coupled+climate+model+family.&representative_member=none&website=none&primary_institution=%22noaa-gfdl%22&family_type=%22model%22&scientific_domains=%22atmosphere%22%2C%22land_surface%22%2C%22ocean%22%2C%22ocean_biogeochemistry%22)

- [GISS-E2](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+GISS-E2&issue_kind=%22Modify%22&collaborative_institutions=&established=none&description=NASA+Goddard+Institute+for+Space+Studies+Earth+system+model+family.&representative_member=none&website=none&primary_institution=%22nasa-giss%22&family_type=%22model%22&scientific_domains=%22atmosphere%22%2C%22land_surface%22%2C%22ocean%22)

- [HadCM2](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+HadCM2&issue_kind=%22Modify%22&collaborative_institutions=&established=1995&description=HadCM2+is+an+early+family+of+Met+Office+Hadley+Centre+coupled+climate+models+that+established+foundational+approaches+for+UK+climate+modeling.&representative_member=HadCM2&website=https%3A%2F%2Fwww.metoffice.gov.uk%2Fresearch%2Fapproach%2Fmodelling-systems%2Funified-model%2Fclimate-models&primary_institution=%22MOHC%22&family_type=%22model%22&scientific_domains=%22atmosphere%22%2C%22ocean%22)

- [HadGEM3](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+HadGEM3&issue_kind=%22Modify%22&collaborative_institutions=%22ncas%22%2C%22NOC%22%2C%22BAS%22&established=2009&description=HadGEM3+is+a+family+of+Met+Office+Hadley+Centre+climate+models+forming+the+basis+for+UK+Earth+system+modeling.&representative_member=HadGEM3-GC31-LL&website=https%3A%2F%2Fwww.metoffice.gov.uk%2Fresearch%2Fmodelling-systems%2Funified-model&primary_institution=%22MOHC%22&family_type=%22model%22&scientific_domains=%22atmosphere%22%2C%22ocean%22%2C%22land_surface%22%2C%22sea_ice%22%2C%22ocean_biogeochemistry%22%2C%22atmospheric_chemistry%22)

- [ICON](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+ICON&issue_kind=%22Modify%22&collaborative_institutions=%22mpi-m%22&established=none&description=ICOsahedral+Nonhydrostatic+model+-+jointly+developed+by+DWD+and+MPI-M+for+weather+and+climate+applications.&representative_member=none&website=none&primary_institution=%22DWD%22&family_type=%22model%22&scientific_domains=%22atmosphere%22%2C%22ocean%22)

- [IFS](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+IFS&issue_kind=%22Modify%22&collaborative_institutions=&established=none&description=Integrated+Forecasting+System+-+ECMWF%27s+operational+weather+and+climate+model.&representative_member=none&website=none&primary_institution=%22ECMWF%22&family_type=%22component%22&scientific_domains=%22atmosphere%22)

- [IPSL-CM](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+IPSL-CM&issue_kind=%22Modify%22&collaborative_institutions=&established=none&description=Institut+Pierre-Simon+Laplace+coupled+climate+model+family.&representative_member=none&website=none&primary_institution=%22ipsl%22&family_type=%22model%22&scientific_domains=%22atmosphere%22%2C%22land_surface%22%2C%22ocean%22%2C%22ocean_biogeochemistry%22)

- [MIROC](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+MIROC&issue_kind=%22Modify%22&collaborative_institutions=&established=none&description=Model+for+Interdisciplinary+Research+on+Climate+-+jointly+developed+by+JAMSTEC%2C+AORI%2C+and+NIES.&representative_member=none&website=none&primary_institution=%22MIROC%22&family_type=%22model%22&scientific_domains=%22atmosphere%22%2C%22land_surface%22%2C%22ocean%22%2C%22sea_ice%22)

- [MPI-ESM](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+MPI-ESM&issue_kind=%22Modify%22&collaborative_institutions=&established=none&description=Max+Planck+Institute+Earth+System+Model.&representative_member=none&website=none&primary_institution=%22mpi-m%22&family_type=%22model%22&scientific_domains=%22atmosphere%22%2C%22land_surface%22%2C%22ocean%22%2C%22ocean_biogeochemistry%22)

- [NICAM](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+NICAM&issue_kind=%22Modify%22&collaborative_institutions=&established=none&description=Nonhydrostatic+ICosahedral+Atmospheric+Model+-+developed+by+JAMSTEC+for+high-resolution+global+simulations.&representative_member=none&website=none&primary_institution=%22JAMSTEC%22&family_type=%22component%22&scientific_domains=%22atmosphere%22)

- [UKESM1](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+UKESM1&issue_kind=%22Modify%22&collaborative_institutions=%22ncas%22%2C%22NOC%22%2C%22BAS%22&established=none&description=UK+Earth+System+Model+-+based+on+HadGEM3+with+additional+Earth+system+components+including+interactive+atmospheric+chemistry+and+ocean+biogeochemistry.&representative_member=none&website=none&primary_institution=%22MOHC%22&family_type=%22model%22&scientific_domains=%22atmosphere%22%2C%22land_surface%22%2C%22ocean%22%2C%22ocean_biogeochemistry%22%2C%22atmospheric_chemistry%22)

- [arpege-climat](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+arpege-climat&issue_kind=%22Modify%22&collaborative_institutions=&established=none&description=ARPEGE-Climat+atmospheric+model+family+developed+by+CNRM%2FM%C3%A9t%C3%A9o-France.&representative_member=none&website=none&primary_institution=%22CNRM%22&family_type=%22component%22&scientific_domains=%22atmosphere%22)

- [gelato](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+gelato&issue_kind=%22Modify%22&collaborative_institutions=&established=none&description=GELATO+sea+ice+model+family+developed+by+CNRM%2FM%C3%A9t%C3%A9o-France.&representative_member=none&website=none&primary_institution=%22CNRM%22&family_type=%22component%22&scientific_domains=%22sea_ice%22)

- [hadam](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+hadam&issue_kind=%22Modify%22&collaborative_institutions=&established=none&description=Hadley+Centre+Atmospheric+Model+family+developed+by+the+UK+Met+Office.&representative_member=none&website=none&primary_institution=%22MOHC%22&family_type=%22component%22&scientific_domains=%22atmosphere%22)

- [nemo](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+nemo&issue_kind=%22Modify%22&collaborative_institutions=%22CNRM%22%2C%22MOHC%22&established=none&description=Nucleus+for+European+Modelling+of+the+Ocean+model+family.&representative_member=none&website=none&primary_institution=%22ipsl%22&family_type=%22component%22&scientific_domains=%22ocean%22)

- [pisces](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+pisces&issue_kind=%22Modify%22&collaborative_institutions=&established=none&description=Pelagic+Interaction+Scheme+for+Carbon+and+Ecosystem+Studies+ocean+biogeochemistry+model+family.&representative_member=none&website=none&primary_institution=%22ipsl%22&family_type=%22component%22&scientific_domains=%22ocean_biogeochemistry%22)

- [reprobus](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+reprobus&issue_kind=%22Modify%22&collaborative_institutions=&established=none&description=REPROBUS+atmospheric+chemistry+model+family+developed+by+CNRM.&representative_member=none&website=none&primary_institution=%22CNRM%22&family_type=%22component%22&scientific_domains=%22atmospheric_chemistry%22)

- [surfex](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+surfex&issue_kind=%22Modify%22&collaborative_institutions=&established=none&description=SURFEX+land+surface+modelling+platform+developed+by+CNRM%2FM%C3%A9t%C3%A9o-France.&representative_member=none&website=none&primary_institution=%22CNRM%22&family_type=%22component%22&scientific_domains=%22land_surface%22)

- [tactic](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+tactic&issue_kind=%22Modify%22&collaborative_institutions=&established=none&description=TACTIC+tropospheric+aerosol+scheme+developed+by+CNRM.&representative_member=none&website=none&primary_institution=%22CNRM%22&family_type=%22component%22&scientific_domains=%22aerosol%22)

</details>

<details markdown="1" name="vertical_computational_grid">
<summary>Vertical Computational Grid (7 entries)</summary>

- [v100](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=vertical_computational_grid.yml&title=Modify%3A+Vertical+Computational+Grid%3A+v100&issue_kind=%22Modify%22&total_thickness=84763.34&n_z=85&description=85-level+atmospheric+hybrid+height+coordinate+extending+to+approximately+85+km.&vertical_coordinate=%22atmosphere-hybrid-height-coordinate%22&top_layer_thickness=10.0&bottom_layer_thickness=100.0)

- [v101](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=vertical_computational_grid.yml&title=Modify%3A+Vertical+Computational+Grid%3A+v101&issue_kind=%22Modify%22&total_thickness=61000.0&n_z=91&description=91-level+atmospheric+hybrid+sigma-pressure+coordinate+extending+to+61+km.&vertical_coordinate=%22atmosphere-hybrid-sigma-pressure-coordinate%22&top_layer_thickness=2.0&bottom_layer_thickness=240.0)

- [v102](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=vertical_computational_grid.yml&title=Modify%3A+Vertical+Computational+Grid%3A+v102&issue_kind=%22Modify%22&total_thickness=12.0&n_z=14&description=14+soil+layers+%280.01%2C+0.04%2C+0.1%2C+0.2%2C+0.4%2C+0.6%2C+0.8%2C+1.0%2C+1.5%2C+2.0%2C+3.0%2C+5.0%2C+8.0%2C+and+12.0+m%29+but+the+soil+moisture+profile+is+computed+only+over+the+rooting+depth%2C+from+0.2+%28rocks%29+to+8+m+%28tropical+forest%29+according+to+the+land+cover+type%2C+while+the+soil+temperature+is+computed+down+to+a+depth+of+12+m.&vertical_coordinate=%22depth%22&top_layer_thickness=0.01&bottom_layer_thickness=4.0)

- [v103](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=vertical_computational_grid.yml&title=Modify%3A+Vertical+Computational+Grid%3A+v103&issue_kind=%22Modify%22&total_thickness=None&n_z=75&description=75-level+ocean+sigma-z+coordinate+with+1+m+surface+layers+and+200+m+bottom+layers.&vertical_coordinate=%22ocean-sigma-z-coordinate%22&top_layer_thickness=1.0&bottom_layer_thickness=200.0)

- [v104](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=vertical_computational_grid.yml&title=Modify%3A+Vertical+Computational+Grid%3A+v104&issue_kind=%22Modify%22&total_thickness=None&n_z=10&description=10-level+height+coordinate+for+sea+ice+thermodynamics.&vertical_coordinate=%22height%22&top_layer_thickness=None&bottom_layer_thickness=None)

- [v105](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=vertical_computational_grid.yml&title=Modify%3A+Vertical+Computational+Grid%3A+v105&issue_kind=%22Modify%22&total_thickness=None&n_z=20&description=The+bottom+level+of+the+snowpack%2C+which+starts+6+metres+below+the+snow+surface%2C+expands+in+thickness+to+hold+as+much+mass+as+the+column+accumulates.&vertical_coordinate=%22land-ice-sigma-coordinate%22&top_layer_thickness=0.04&bottom_layer_thickness=None)

- [v106](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=vertical_computational_grid.yml&title=Modify%3A+Vertical+Computational+Grid%3A+v106&issue_kind=%22Modify%22&total_thickness=None&n_z=None&description=Vegetated%2C+wetland%2C+and+glacier+landunits+have+15+vertical+layers.+Lakes+have+10+layers.+Snow+can+have+up+to+5+layers.&vertical_coordinate=%22depth%22&top_layer_thickness=None&bottom_layer_thickness=None)

</details>

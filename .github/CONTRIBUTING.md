# Contribution Guidelines
The full description on how to submit new data is available in the documentation (link below). 


The following sections will contain links to:

1. Forms for the submission of new data
2. Prefilled links for existing content, this can be used for modification, or adaption when submitting/reusing entries. 


Please ensure that any additions or modifications to controlled vocabularies adhere to the established standards and formats. Refer to the [Documentation](https://emd.mipcvs.dev/doc) for guidance.



## 1. Submitting New Controlled Vocabularies

The following forms are available for this repository, and can be used to add or modify entries. The complete submission pipeline (if applicable) will be outlined in the section above.


### Model Registration

- [model](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model.yml)
- [model_component](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_component.yml)
- [model_family](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml)
### Grid Registration

- [horizontal_computational_grid](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_computational_grid.yml)
- [horizontal_subgrid](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_subgrid.yml)
- [horizontal_grid_cells](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_grid_cells.yml)
- [vertical_computational_grid](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=vertical_computational_grid.yml)
### References

- [reference](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=reference.yml)
### Issues & Discussion

- [general_issue](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=general_issue.yml)

## 2 Modifying or reusing existing entries

The following links will open pre-filled GitHub issues with content from the selected files. These can be used to update entries or make new ones. 

<details name="horizontal_computational_grid">
<summary>Horizontal Computational Grid (4 entries)</summary>

- [c100](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_computational_grid.yml&title=Modify%3A+Horizontal+Computational+Grid%3A+c100&issue_kind=%22Modify%22&description=Arakawa-C+grid+combining+regular+latitude-longitude+and+spectral+Gaussian+subgrids+for+atmospheric+modelling.&arrangement=%22arakawa-c%22)

- [c101](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_computational_grid.yml&title=Modify%3A+Horizontal+Computational+Grid%3A+c101&issue_kind=%22Modify%22&description=Arakawa-C+grid+on+an+ocean+tripolar+configuration+%28eORCA1%29.&arrangement=%22arakawa-c%22)

- [c102](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_computational_grid.yml&title=Modify%3A+Horizontal+Computational+Grid%3A+c102&issue_kind=%22Modify%22&description=Arakawa-C+grid+with+adaptive+mesh+refinement+for+ice+sheet+modelling.&arrangement=%22arakawa-c%22)

- [c103](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_computational_grid.yml&title=Modify%3A+Horizontal+Computational+Grid%3A+c103&issue_kind=%22Modify%22&description=Arakawa-A+grid+on+a+regular+latitude-longitude+configuration+for+land+surface+modelling.&arrangement=%22arakawa-a%22)

</details>

<details name="horizontal_grid_cells">
<summary>Horizontal Grid Cells (5 entries)</summary>

- [g100](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_grid_cells.yml&title=Modify%3A+Horizontal+Grid+Cells%3A+g100&issue_kind=%22Modify%22&description=Global+regular+latitude-longitude+grid+with+1.25%C2%B0+x+0.9%C2%B0+resolution+and+55296+cells.&grid_type=%22regular_latitude_longitude%22&x_resolution=1.25&y_resolution=0.9&n_cells=55296&grid_mapping=%22latitude_longitude%22&temporal_refinement=%22static%22&southernmost_latitude=-89.5&region=%22global%22&westernmost_longitude=0.5&units=%22degree%22)

- [g101](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_grid_cells.yml&title=Modify%3A+Horizontal+Grid+Cells%3A+g101&issue_kind=%22Modify%22&truncation_number=127&description=Linear+spectral+Gaussian+grid+%28TL127%29+with+24572+cells.&grid_type=%22linear_spectral_gaussian%22&x_resolution=1.4&y_resolution=1.4&n_cells=24572&truncation_method=%22triangular%22&grid_mapping=%22latitude_longitude%22&temporal_refinement=%22static%22&southernmost_latitude=-88.9277353522076&region=%22global%22&westernmost_longitude=0.0&units=%22degree%22)

- [g102](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_grid_cells.yml&title=Modify%3A+Horizontal+Grid+Cells%3A+g102&issue_kind=%22Modify%22&description=Ocean+tripolar+grid+%28eORCA1%29+with+105704+cells.&grid_type=%22tripolar%22&n_cells=105704&grid_mapping=%22latitude_longitude%22&temporal_refinement=%22static%22&region=%22global%22)

- [g103](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_grid_cells.yml&title=Modify%3A+Horizontal+Grid+Cells%3A+g103&issue_kind=%22Modify%22&description=Adaptive+polar+stereographic+mesh+for+ice+sheets+with+variable+resolution+%289.6+km+to+1.2+km+for+Greenland%2C+8+km+to+2+km+for+Antarctica%29.&grid_type=%22plane_projection%22&grid_mapping=%22polar_stereographic%22&temporal_refinement=%22adaptive%22&region=%22greenland%22%2C%22antarctica%22)

- [g104](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_grid_cells.yml&title=Modify%3A+Horizontal+Grid+Cells%3A+g104&issue_kind=%22Modify%22&description=Global+regular+latitude-longitude+grid+with+1.25%C2%B0+x+0.9%C2%B0+resolution+and+55296+cells%2C+offset+origin+from+g100.&grid_type=%22regular_latitude_longitude%22&x_resolution=1.25&y_resolution=0.9&n_cells=55296&grid_mapping=%22latitude_longitude%22&temporal_refinement=%22static%22&southernmost_latitude=-89.65&region=%22global%22&westernmost_longitude=0.0&units=%22degree%22)

</details>

<details name="horizontal_subgrid">
<summary>Horizontal Subgrid (5 entries)</summary>

- [s100](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_subgrid.yml&title=Modify%3A+Horizontal+Subgrid%3A+s100&issue_kind=%22Modify%22&cell_variable_type=%22mass%22&description=Mass+variables+on+a+regular+latitude-longitude+grid.)

- [s101](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_subgrid.yml&title=Modify%3A+Horizontal+Subgrid%3A+s101&issue_kind=%22Modify%22&cell_variable_type=%22mass%22&description=Mass+variables+on+a+linear+spectral+Gaussian+grid+%28TL127%29.)

- [s102](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_subgrid.yml&title=Modify%3A+Horizontal+Subgrid%3A+s102&issue_kind=%22Modify%22&cell_variable_type=%22mass%22&description=Mass+variables+on+an+ocean+tripolar+grid+%28eORCA1%29.)

- [s103](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_subgrid.yml&title=Modify%3A+Horizontal+Subgrid%3A+s103&issue_kind=%22Modify%22&cell_variable_type=%22mass%22%2C%22x-velocity%22%2C%22y-velocity%22&description=Mass+and+velocity+variables+on+an+adaptive+polar+stereographic+mesh+for+ice+sheets.)

- [s104](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_subgrid.yml&title=Modify%3A+Horizontal+Subgrid%3A+s104&issue_kind=%22Modify%22&cell_variable_type=%22mass%22&description=Mass+variables+on+a+regular+latitude-longitude+grid+for+land+surface+modelling.)

</details>

<details name="model">
<summary>Model (1 entries)</summary>

- [cnrm-esm2-1e](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model.yml&title=Modify%3A+Model%3A+cnrm-esm2-1e&issue_kind=%22Modify%22&dynamic_components=%22aerosol%22%2C%22atmosphere%22%2C%22atmospheric_chemistry%22%2C%22land_surface%22%2C%22ocean%22%2C%22ocean_biogeochemistry%22%2C%22sea_ice%22&release_year=2018&omitted_components=%22land_ice%22&name=CNRM-ESM2-1e&description=CNRM-ESM2-1e+is+the+CNRM+Earth+System+model+version+2+designed+for+CMIP6+on+the+basis+of+the+physical+core+CNRM-CM6-1+%28Voldoire+et+al.+2019%29.+In+concentration+mode%2C+it+is+the+same+model+as+CNRM-ESM2-1+%28S%C3%A9f%C3%A9rian+et+al.+2019%29%2C+it+only+differs+from+CNRM-ESM2-1+in+emission-driven+mode+%28see+Bossert+et+al.+2026%29.+The+main+adaptations+consist+in+a+better+conservation+of+the+carbon+in+all+the+components+leading+to+a+more+consistent%2Frealistic+carbon+flux+evolution+in+historical+simulations.&calendar=%22standard%22&family=%22CNRM-CM%22&prescribed_components=)

</details>

<details name="model_component">
<summary>Model Component (10 entries)</summary>

- [arpege-climat_version_6_3](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_component.yml&title=Modify%3A+Model+Component%3A+arpege-climat_version_6_3&issue_kind=%22Modify%22&component=%22atmosphere%22&code_base=private&name=Arpege-Climat+Version+6.3&description=ARPEGE-Climat+Version+6.3+is+the+atmospheric+component+of+the+CNRM+climate+and+Earth+System+models+%28CNRM-CM6-1+and+CNRM-ESM2-1%29.&family=%22arpege-climat%22&coupled_with=%22land_surface%22%2C%22ocean%22&embedded_in=%22none%22)

- [bisicles-ukesm-ismip6-1_0](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_component.yml&title=Modify%3A+Model+Component%3A+bisicles-ukesm-ismip6-1_0&issue_kind=%22Modify%22&component=%22land_ice%22&code_base=none&name=BISICLES-UKESM-ISMIP6-1.0&description=UniCiCles+%28Unified+Model-CISM-BISICLES%29+is+a+package+combining+BISICLES+with+an+interface+that+obtains+boundary+conditions+from+Unified+Model+or+JULES+data.&family=%22BISICLES%22&coupled_with=%22atmosphere%22%2C%22land_surface%22%2C%22ocean%22&embedded_in=%22none%22)

- [clm4](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_component.yml&title=Modify%3A+Model+Component%3A+clm4&issue_kind=%22Modify%22&component=%22land_surface%22&code_base=none&name=CLM4&description=The+Community+Land+Model+represents+several+aspects+of+the+land+surface+including+surface+heterogeneity+through+a+nested+subgrid+hierarchy.&family=%22CLM%22&coupled_with=%22none%22&embedded_in=%22atmosphere%22)

- [gelato](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_component.yml&title=Modify%3A+Model+Component%3A+gelato&issue_kind=%22Modify%22&component=%22sea_ice%22&code_base=private&name=GELATO&description=Global+Experimental+Leads+and+sea+ice+for+ATmosphere+and+Ocean.&family=%22gelato%22&coupled_with=%22none%22&embedded_in=%22ocean%22)

- [hadam3](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_component.yml&title=Modify%3A+Model+Component%3A+hadam3&issue_kind=%22Modify%22&component=%22atmosphere%22&code_base=none&name=HadAM3&description=HadAM3+is+the+atmospheric+component+of+HadCM3%2C+a+coupled+atmosphere-ocean+general+circulation+model+developed+at+the+UK+Met+Office+Hadley+Centre.&family=%22hadam%22&coupled_with=%22ocean%22%2C%22land_surface%22&embedded_in=%22none%22)

- [nemo_v3_6](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_component.yml&title=Modify%3A+Model+Component%3A+nemo_v3_6&issue_kind=%22Modify%22&component=%22ocean%22&code_base=private&name=NEMO+v3.6&description=Nucleus+for+European+Modelling+of+the+Ocean+version+3.6+%28OPA%29.&family=%22nemo%22&coupled_with=%22atmosphere%22%2C%22land_surface%22&embedded_in=%22none%22)

- [piscesv2-gas](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_component.yml&title=Modify%3A+Model+Component%3A+piscesv2-gas&issue_kind=%22Modify%22&component=%22ocean_biogeochemistry%22&code_base=https%3A%2F%2Fgitlab.in2p3.fr%2Fpisco%2Fpisces-gas%2Fpisces-gas&name=PISCESv2-gas&description=Pelagic+Interaction+Scheme+for+Carbon+and+Ecosystem+Studies+model+volume+2+version+trace+gases.&family=%22pisces%22&coupled_with=%22none%22&embedded_in=%22ocean%22)

- [reprobus-c_v2_0](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_component.yml&title=Modify%3A+Model+Component%3A+reprobus-c_v2_0&issue_kind=%22Modify%22&component=%22atmospheric_chemistry%22&code_base=private&name=REPROBUS-C+%28v2.0%29&description=The+chemistry+scheme+of+CNRM-ESM2+is+an+on-line+scheme+whereby+the+chemistry+routines+are+part+of+the+physics+of+the+atmospheric+climate+model.&family=%22reprobus%22&coupled_with=%22none%22&embedded_in=%22atmosphere%22)

- [surfex_v8_modeling_platform](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_component.yml&title=Modify%3A+Model+Component%3A+surfex_v8_modeling_platform&issue_kind=%22Modify%22&component=%22land_surface%22&code_base=https%3A%2F%2Fwww.umr-cnrm.fr%2Fsurfex%2Fspip.php%3Frubrique8&name=SURFEX+v8+modeling+platform&description=SURFEXv8.0+encompasses+several+submodules+for+modeling+the+interactions+between+the+atmosphere%2C+the+ocean%2C+the+lakes+and+the+land+surface.&family=%22surfex%22&coupled_with=%22atmosphere%22%2C%22ocean%22&embedded_in=%22none%22)

- [tactic](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_component.yml&title=Modify%3A+Model+Component%3A+tactic&issue_kind=%22Modify%22&component=%22aerosol%22&code_base=private&name=TACTIC&description=TACTIC+%28Tropospheric+Aerosols+for+ClimaTe+In+CNRM%29+is+an+interactive+tropospheric+aerosol+scheme%2C+able+to+represent+the+main+anthropogenic+and+natural+aerosol+types+in+the+troposphere.&family=%22tactic%22&coupled_with=&embedded_in=%22atmosphere%22)

</details>

<details name="model_family">
<summary>Model Family (30 entries)</summary>

- [ACCESS](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+ACCESS&issue_kind=%22Modify%22&website=none&scientific_domains=%22atmosphere%22%2C%22land_surface%22%2C%22ocean%22%2C%22sea_ice%22&collaborative_institutions=%22bom%22&established=none&description=Australian+Community+Climate+and+Earth+System+Simulator+-+a+coupled+climate+and+Earth+system+model+developed+by+the+Australian+climate+research+community.&representative_member=none&primary_institution=%22CSIRO%22)

- [BCC-CSM](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+BCC-CSM&issue_kind=%22Modify%22&website=none&scientific_domains=%22atmosphere%22%2C%22land_surface%22%2C%22ocean%22&collaborative_institutions=&established=none&description=Beijing+Climate+Center+Climate+System+Model.&representative_member=none&primary_institution=%22BCC%22)

- [BISICLES](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+BISICLES&issue_kind=%22Modify%22&website=https%3A%2F%2Fbisicles.lbl.gov%2F&scientific_domains=%22land_ice%22&collaborative_institutions=%22uob%22%2C%22BAS%22&established=2008&description=BISICLES+uses+adaptive-mesh+Chombo+libraries+for+ice+sheet+modeling+with+SSA-+momentum+approximation.&representative_member=BISICLES-UKESM-ISMIP6-1.0&primary_institution=%22LBNL%22)

- [CAM](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+CAM&issue_kind=%22Modify%22&website=none&scientific_domains=%22atmosphere%22&collaborative_institutions=&established=none&description=Community+Atmosphere+Model+-+the+atmospheric+component+of+CESM%2C+also+used+standalone+for+atmospheric+research.&representative_member=none&primary_institution=%22NCAR%22)

- [CESM](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+CESM&issue_kind=%22Modify%22&website=none&scientific_domains=%22atmosphere%22%2C%22land_surface%22%2C%22ocean%22%2C%22sea_ice%22%2C%22ocean_biogeochemistry%22&collaborative_institutions=&established=none&description=Community+Earth+System+Model+-+a+fully-coupled+global+climate+model+developed+at+NCAR+providing+simulations+of+the+Earth%27s+past%2C+present%2C+and+future+climate+states.&representative_member=none&primary_institution=%22NCAR%22)

- [CLM](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+CLM&issue_kind=%22Modify%22&website=https%3A%2F%2Fwww.cesm.ucar.edu%2Fmodels%2Fcesm2%2Fland&scientific_domains=%22land_surface%22%2C%22ocean_biogeochemistry%22&collaborative_institutions=%22LBNL%22%2C%22PNNL%22&established=1996&description=Community+Land+Model+family+representing+land+surface+heterogeneity+through+nested+subgrid+hierarchy.&representative_member=CLM4&primary_institution=%22NCAR%22)

- [CNRM-CM](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+CNRM-CM&issue_kind=%22Modify%22&website=none&scientific_domains=%22atmosphere%22%2C%22land_surface%22%2C%22ocean%22&collaborative_institutions=&established=none&description=Centre+National+de+Recherches+M%C3%A9t%C3%A9orologiques+coupled+climate+model+family.&representative_member=none&primary_institution=%22CNRM-CERFACS%22)

- [CanESM](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+CanESM&issue_kind=%22Modify%22&website=none&scientific_domains=%22atmosphere%22%2C%22land_surface%22%2C%22ocean%22%2C%22sea_ice%22&collaborative_institutions=&established=none&description=Canadian+Earth+System+Model+-+developed+by+the+Canadian+Centre+for+Climate+Modelling+and+Analysis.&representative_member=none&primary_institution=%22CCCma%22)

- [EC-Earth](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+EC-Earth&issue_kind=%22Modify%22&website=none&scientific_domains=%22atmosphere%22%2C%22land_surface%22%2C%22ocean%22%2C%22sea_ice%22&collaborative_institutions=&established=none&description=Community-developed+Earth+system+model+based+on+the+ECMWF+Integrated+Forecasting+System+%28IFS%29.&representative_member=none&primary_institution=%22EC-Earth-Consortium%22)

- [FGOALS](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+FGOALS&issue_kind=%22Modify%22&website=none&scientific_domains=%22atmosphere%22%2C%22land_surface%22%2C%22ocean%22&collaborative_institutions=&established=none&description=Flexible+Global+Ocean-Atmosphere-Land+System+Model+-+developed+by+the+Institute+of+Atmospheric+Physics%2C+Chinese+Academy+of+Sciences.&representative_member=none&primary_institution=%22CAS%22)

- [GEOS](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+GEOS&issue_kind=%22Modify%22&website=none&scientific_domains=%22atmosphere%22&collaborative_institutions=&established=none&description=Goddard+Earth+Observing+System+-+NASA%27s+atmospheric+general+circulation+model.&representative_member=none&primary_institution=%22NASA-GSFC%22)

- [GFDL-CM4](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+GFDL-CM4&issue_kind=%22Modify%22&website=none&scientific_domains=%22atmosphere%22%2C%22land_surface%22%2C%22ocean%22%2C%22ocean_biogeochemistry%22&collaborative_institutions=&established=none&description=NOAA+Geophysical+Fluid+Dynamics+Laboratory+coupled+climate+model+family.&representative_member=none&primary_institution=%22NOAA-GFDL%22)

- [GISS-E2](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+GISS-E2&issue_kind=%22Modify%22&website=none&scientific_domains=%22atmosphere%22%2C%22land_surface%22%2C%22ocean%22&collaborative_institutions=&established=none&description=NASA+Goddard+Institute+for+Space+Studies+Earth+system+model+family.&representative_member=none&primary_institution=%22NASA-GISS%22)

- [HadCM2](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+HadCM2&issue_kind=%22Modify%22&website=https%3A%2F%2Fwww.metoffice.gov.uk%2Fresearch%2Fapproach%2Fmodelling-systems%2Funified-model%2Fclimate-models&scientific_domains=%22atmosphere%22%2C%22ocean%22&collaborative_institutions=&established=1995&description=HadCM2+is+an+early+family+of+Met+Office+Hadley+Centre+coupled+climate+models+that+established+foundational+approaches+for+UK+climate+modeling.&representative_member=HadCM2&primary_institution=%22MOHC%22)

- [HadGEM3](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+HadGEM3&issue_kind=%22Modify%22&website=https%3A%2F%2Fwww.metoffice.gov.uk%2Fresearch%2Fmodelling-systems%2Funified-model&scientific_domains=%22atmosphere%22%2C%22ocean%22%2C%22land_surface%22%2C%22sea_ice%22%2C%22ocean_biogeochemistry%22%2C%22atmospheric_chemistry%22&collaborative_institutions=%22NCAS%22%2C%22NOC%22%2C%22BAS%22&established=2009&description=HadGEM3+is+a+family+of+Met+Office+Hadley+Centre+climate+models+forming+the+basis+for+UK+Earth+system+modeling.&representative_member=HadGEM3-GC31-LL&primary_institution=%22MOHC%22)

- [ICON](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+ICON&issue_kind=%22Modify%22&website=none&scientific_domains=%22atmosphere%22%2C%22ocean%22&collaborative_institutions=%22MPI-M%22&established=none&description=ICOsahedral+Nonhydrostatic+model+-+jointly+developed+by+DWD+and+MPI-M+for+weather+and+climate+applications.&representative_member=none&primary_institution=%22DWD%22)

- [IFS](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+IFS&issue_kind=%22Modify%22&website=none&scientific_domains=%22atmosphere%22&collaborative_institutions=&established=none&description=Integrated+Forecasting+System+-+ECMWF%27s+operational+weather+and+climate+model.&representative_member=none&primary_institution=%22ECMWF%22)

- [IPSL-CM](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+IPSL-CM&issue_kind=%22Modify%22&website=none&scientific_domains=%22atmosphere%22%2C%22land_surface%22%2C%22ocean%22%2C%22ocean_biogeochemistry%22&collaborative_institutions=&established=none&description=Institut+Pierre-Simon+Laplace+coupled+climate+model+family.&representative_member=none&primary_institution=%22IPSL%22)

- [MIROC](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+MIROC&issue_kind=%22Modify%22&website=none&scientific_domains=%22atmosphere%22%2C%22land_surface%22%2C%22ocean%22%2C%22sea_ice%22&collaborative_institutions=&established=none&description=Model+for+Interdisciplinary+Research+on+Climate+-+jointly+developed+by+JAMSTEC%2C+AORI%2C+and+NIES.&representative_member=none&primary_institution=%22MIROC%22)

- [MPI-ESM](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+MPI-ESM&issue_kind=%22Modify%22&website=none&scientific_domains=%22atmosphere%22%2C%22land_surface%22%2C%22ocean%22%2C%22ocean_biogeochemistry%22&collaborative_institutions=&established=none&description=Max+Planck+Institute+Earth+System+Model.&representative_member=none&primary_institution=%22MPI-M%22)

- [NICAM](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+NICAM&issue_kind=%22Modify%22&website=none&scientific_domains=%22atmosphere%22&collaborative_institutions=&established=none&description=Nonhydrostatic+ICosahedral+Atmospheric+Model+-+developed+by+JAMSTEC+for+high-resolution+global+simulations.&representative_member=none&primary_institution=%22JAMSTEC%22)

- [UKESM1](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+UKESM1&issue_kind=%22Modify%22&website=none&scientific_domains=%22atmosphere%22%2C%22land_surface%22%2C%22ocean%22%2C%22ocean_biogeochemistry%22%2C%22atmospheric_chemistry%22&collaborative_institutions=%22NCAS%22%2C%22NOC%22%2C%22BAS%22&established=none&description=UK+Earth+System+Model+-+based+on+HadGEM3+with+additional+Earth+system+components+including+interactive+atmospheric+chemistry+and+ocean+biogeochemistry.&representative_member=none&primary_institution=%22MOHC%22)

- [arpege-climat](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+arpege-climat&issue_kind=%22Modify%22&scientific_domains=%22atmosphere%22&collaborative_institutions=&description=ARPEGE-Climat+atmospheric+model+family+developed+by+CNRM%2FM%C3%A9t%C3%A9o-France.&primary_institution=%22CNRM%22)

- [gelato](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+gelato&issue_kind=%22Modify%22&scientific_domains=%22sea_ice%22&collaborative_institutions=&description=GELATO+sea+ice+model+family+developed+by+CNRM%2FM%C3%A9t%C3%A9o-France.&primary_institution=%22CNRM%22)

- [hadam](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+hadam&issue_kind=%22Modify%22&scientific_domains=%22atmosphere%22&collaborative_institutions=&description=Hadley+Centre+Atmospheric+Model+family+developed+by+the+UK+Met+Office.&primary_institution=%22MOHC%22)

- [nemo](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+nemo&issue_kind=%22Modify%22&scientific_domains=%22ocean%22&collaborative_institutions=%22CNRM%22%2C%22MOHC%22&description=Nucleus+for+European+Modelling+of+the+Ocean+model+family.&primary_institution=%22IPSL%22)

- [pisces](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+pisces&issue_kind=%22Modify%22&scientific_domains=%22ocean_biogeochemistry%22&collaborative_institutions=&description=Pelagic+Interaction+Scheme+for+Carbon+and+Ecosystem+Studies+ocean+biogeochemistry+model+family.&primary_institution=%22IPSL%22)

- [reprobus](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+reprobus&issue_kind=%22Modify%22&scientific_domains=%22atmospheric_chemistry%22&collaborative_institutions=&description=REPROBUS+atmospheric+chemistry+model+family+developed+by+CNRM.&primary_institution=%22CNRM%22)

- [surfex](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+surfex&issue_kind=%22Modify%22&scientific_domains=%22land_surface%22&collaborative_institutions=&description=SURFEX+land+surface+modelling+platform+developed+by+CNRM%2FM%C3%A9t%C3%A9o-France.&primary_institution=%22CNRM%22)

- [tactic](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml&title=Modify%3A+Model+Family%3A+tactic&issue_kind=%22Modify%22&scientific_domains=%22aerosol%22&collaborative_institutions=&description=TACTIC+tropospheric+aerosol+scheme+developed+by+CNRM.&primary_institution=%22CNRM%22)

</details>

<details name="reference">
<summary>Reference (17 entries)</summary>

- [ref001](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=reference.yml&title=Modify%3A+Reference%3A+ref001&issue_kind=%22Modify%22)

- [ref002](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=reference.yml&title=Modify%3A+Reference%3A+ref002&issue_kind=%22Modify%22)

- [ref003](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=reference.yml&title=Modify%3A+Reference%3A+ref003&issue_kind=%22Modify%22)

- [ref004](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=reference.yml&title=Modify%3A+Reference%3A+ref004&issue_kind=%22Modify%22)

- [ref005](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=reference.yml&title=Modify%3A+Reference%3A+ref005&issue_kind=%22Modify%22)

- [ref006](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=reference.yml&title=Modify%3A+Reference%3A+ref006&issue_kind=%22Modify%22)

- [ref007](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=reference.yml&title=Modify%3A+Reference%3A+ref007&issue_kind=%22Modify%22)

- [ref008](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=reference.yml&title=Modify%3A+Reference%3A+ref008&issue_kind=%22Modify%22)

- [ref009](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=reference.yml&title=Modify%3A+Reference%3A+ref009&issue_kind=%22Modify%22)

- [ref010](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=reference.yml&title=Modify%3A+Reference%3A+ref010&issue_kind=%22Modify%22)

- [ref011](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=reference.yml&title=Modify%3A+Reference%3A+ref011&issue_kind=%22Modify%22)

- [ref012](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=reference.yml&title=Modify%3A+Reference%3A+ref012&issue_kind=%22Modify%22)

- [ref013](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=reference.yml&title=Modify%3A+Reference%3A+ref013&issue_kind=%22Modify%22)

- [ref014](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=reference.yml&title=Modify%3A+Reference%3A+ref014&issue_kind=%22Modify%22)

- [ref015](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=reference.yml&title=Modify%3A+Reference%3A+ref015&issue_kind=%22Modify%22)

- [ref_bisicles](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=reference.yml&title=Modify%3A+Reference%3A+ref_bisicles&issue_kind=%22Modify%22)

- [ref_clm4](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=reference.yml&title=Modify%3A+Reference%3A+ref_clm4&issue_kind=%22Modify%22)

</details>

<details name="vertical_computational_grid">
<summary>Vertical Computational Grid (7 entries)</summary>

- [v100](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=vertical_computational_grid.yml&title=Modify%3A+Vertical+Computational+Grid%3A+v100&issue_kind=%22Modify%22&total_thickness=84763.34&n_z=85&description=85-level+atmospheric+hybrid+height+coordinate+extending+to+approximately+85+km.&bottom_layer_thickness=100.0&top_layer_thickness=10.0&vertical_coordinate=%22atmosphere_hybrid_height_coordinate%22)

- [v101](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=vertical_computational_grid.yml&title=Modify%3A+Vertical+Computational+Grid%3A+v101&issue_kind=%22Modify%22&total_thickness=61000.0&n_z=91&description=91-level+atmospheric+hybrid+sigma-pressure+coordinate+extending+to+61+km.&bottom_layer_thickness=240.0&top_layer_thickness=2.0&vertical_coordinate=%22atmosphere_hybrid_sigma_pressure_coordinate%22)

- [v102](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=vertical_computational_grid.yml&title=Modify%3A+Vertical+Computational+Grid%3A+v102&issue_kind=%22Modify%22&total_thickness=12.0&n_z=14&description=14+soil+layers+%280.01%2C+0.04%2C+0.1%2C+0.2%2C+0.4%2C+0.6%2C+0.8%2C+1.0%2C+1.5%2C+2.0%2C+3.0%2C+5.0%2C+8.0%2C+and+12.0+m%29+but+the+soil+moisture+profile+is+computed+only+over+the+rooting+depth%2C+from+0.2+%28rocks%29+to+8+m+%28tropical+forest%29+according+to+the+land+cover+type%2C+while+the+soil+temperature+is+computed+down+to+a+depth+of+12+m.&bottom_layer_thickness=4.0&top_layer_thickness=0.01&vertical_coordinate=%22depth%22)

- [v103](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=vertical_computational_grid.yml&title=Modify%3A+Vertical+Computational+Grid%3A+v103&issue_kind=%22Modify%22&n_z=75&description=75-level+ocean+sigma-z+coordinate+with+1+m+surface+layers+and+200+m+bottom+layers.&bottom_layer_thickness=200.0&top_layer_thickness=1.0&vertical_coordinate=%22ocean_sigma_z_coordinate%22)

- [v104](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=vertical_computational_grid.yml&title=Modify%3A+Vertical+Computational+Grid%3A+v104&issue_kind=%22Modify%22&n_z=10&description=10-level+height+coordinate+for+sea+ice+thermodynamics.&vertical_coordinate=%22height%22)

- [v105](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=vertical_computational_grid.yml&title=Modify%3A+Vertical+Computational+Grid%3A+v105&issue_kind=%22Modify%22&n_z=20&description=The+bottom+level+of+the+snowpack%2C+which+starts+6+metres+below+the+snow+surface%2C+expands+in+thickness+to+hold+as+much+mass+as+the+column+accumulates.&top_layer_thickness=0.04&vertical_coordinate=%22land_ice_sigma_coordinate%22)

- [v106](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=vertical_computational_grid.yml&title=Modify%3A+Vertical+Computational+Grid%3A+v106&issue_kind=%22Modify%22&description=Vegetated%2C+wetland%2C+and+glacier+landunits+have+15+vertical+layers.+Lakes+have+10+layers.+Snow+can+have+up+to+5+layers.&vertical_coordinate=%22depth%22)

</details>

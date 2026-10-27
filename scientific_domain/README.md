
<section id="description">

# Scientific Domain (universal)

## Description
Defines the scientific domains of the Earth system that model components represent. These correspond to the component types defined in EMD (Essential Model Documentation) specification. The `alias` field contains legacy identifiers from the realm vocabulary for backward compatibility.

[View in HTML](https://wcrp-cmip.github.io/Essential-Model-Documentation/scientific_domain/scientific_domain)

</section>

<section id="mapping">

## Mapping from Realm

| Scientific Domain | Old Realm ID | Aliases |
| --- | --- | --- |
| aerosol | aerosol | aerosol |
| atmosphere | atmos | atmos |
| atmospheric_chemistry | atmoschem | atmoschem, atmosChem |
| land_surface | land | land |
| land_ice | landice | landice, landIce |
| ocean | ocean | ocean |
| ocean_biogeochemistry | ocnbgchem | ocnbgchem, ocnBgchem |
| sea_ice | seaice | seaice, seaIce |

</section>

<section id="info">

| Item | Reference |
| --- | --- |
| Type | `wcrp:scientific_domain` |
| JSON-LD | `universal:scientific_domain` |
| Expanded reference link | [https://wcrp-cmip.github.io/Essential-Model-Documentation/scientific_domain](https://wcrp-cmip.github.io/Essential-Model-Documentation/scientific_domain) |

</section>

<section id="usage">

## Usage

### Getting a File

```python
import cmipld
cmipld.get("universal:scientific_domain/atmosphere")
```

</section>

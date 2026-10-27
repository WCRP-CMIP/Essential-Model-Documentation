
<section id="description">

# Region  (universal)



## Description
Defines the geographic regions used for data subsetting in CMIP7. Regions specify spatial domains for which model output is provided (e.g., global, northern hemisphere, Antarctica, Greenland).

[View in HTML](https://wcrp-cmip.github.io/Essential-Model-Documentation/region/region)

</section>



<section id="info">


| Item | Reference |
| --- | --- |
| Type | `wrcp:region` |
| | |
| JSON-LD | `universal:region` |
| Expanded reference link | [https://wcrp-cmip.github.io/Essential-Model-Documentation/region](https://wcrp-cmip.github.io/Essential-Model-Documentation/region) |
| Developer Repo | [![Open in GitHub](https://img.shields.io/badge/Open-GitHub-blue?logo=github&style=flat-square)](https://github.com/WCRP-CMIP/Essential-Model-Documentation/tree/main/region) |


</section>

<section id="schema">

## Content Schema

- **`id`** (**str**) 
  Region identifier
- **`description`** (**str**) 
  Description of the geographic region
- **`ui_label`** (**str**) 
  User-friendly label for the region
- **`type`** (**str**) 
  Type classification





</section>   

<section id="usage">

## Usage

### Online Viewer 
To view a file in a browser use the content link with `.json` appended. 
eg. https://github.com/WCRP-CMIP/Essential-Model-Documentation/tree/main/region/glb.json

### Getting a File. 

A short example of how to integrate the computed ld file into your code. 

```python

import cmipld
cmipld.get( "universal:region/glb")

```

### Framing
Framing is a way we can filter the downloaded data to match what we want. 
```js
frame = {
            "@context": "https://emd.wcrp-cmip.org/region/_context",
            "@type": "wcrp:region",
            "keys we want": "",
            "@explicit": True

        }
        
```

```python

import cmipld
cmipld.frame( "universal:region/glb" , frame)

```
</section>

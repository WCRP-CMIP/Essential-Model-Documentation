import cmipld
import os
from cmipld.utils.ldparse import *
from cmipld.utils.checksum import version

me = __file__.split('/')[-1].replace('.py','')

def run(prefix, path, name, url, io):
    
    url = f'{prefix}:{me}/graph.jsonld'
    data = cmipld.get(url,depth=1)
    
    content = name_extract(data)
    
    # location = f'{path}/{name.lower()}_{me}.json'
    location = f'{path}/{me}.json'
    return location, me, content
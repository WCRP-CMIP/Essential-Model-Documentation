import select
BASE = "https://esgvoc.ipsl.fr/api/v1/universe/data_descriptors/"

import requests, json

DATA = {}

for kind in ['organisation','institution']:
    allitems = requests.get(f'{BASE}{kind}/terms').json()
    for select in allitems:

        id = select.get('id')
        
        if kind == "organisation":
            select['members'] = [ i.get('id') for i in select['members'] if i.get('id') != id ]
            if not len(select['members') :
                # no members - we do not self-loop - that is silly!
                continue
            

        
        if id: 

            current = {"@id":id,**select}

            try:
                DATA[id].update(current)
            except:
                DATA[id] = current

            

            DATA[id]['@context'] = '_context'
            
            DATA[id]['@type'] = list(set(DATA.get('@type',[kind])).union([kind]))
            del DATA[id]['id'],DATA[id]['type']

            



path = './'
for k,v in DATA.items():
    json.dump(v,open(path+f'establishment/{k}.json','w'),indent=4)



            




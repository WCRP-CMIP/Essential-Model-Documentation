from typing import TypeVar, Generic, Type
from pydantic import BaseModel, model_validator

T = TypeVar("T", bound=BaseModel)


class pycmipld(BaseModel, Generic[T]):
    data: T
    _model: Type[T]

    def __init__(self, model: Type[T], **cmip_ld_data):
        self._model = model
        super().__init__(data=self._translate(cmip_ld_data))

    def _translate(self, values: dict) -> T:
        
        type = None
        for t in values.get("@type"): 
            if 'esgvoc:' in t:
                type = t.replace('esgvoc:','')
                break
        type = type or ''
        
        translated = {
            "id": values.get("@id"),
            "type": type,
            "context": values.get("@context"),
            "drs_name": values.get("validation_key"),
            **{k: v for k, v in values.items() if not k.startswith("@")}
        }
        return self._model.model_validate(translated)
    
    
    
    
    
    
    
from typing import TypeVar, Generic, Type
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class pycmipld(BaseModel, Generic[T]):
    data: T
    _model: Type[T]

    def __init__(self, model: Type[T], **cmip_ld_data):
        self._model = model
        super().__init__(data=self._translate(cmip_ld_data))

    def _translate(self, values: dict) -> T:
        # Get esgvoc type
        raw_type = values.get("@type", "")
        type = next((t.replace('esgvoc:', '') for t in raw_type if 'esgvoc:' in t), None)

        # Translate keys and replace empty strings with None
        translated = {
            k_new: (v if v != '' else None) # jsonld cannot handle None, but esgvoc numerical classes cannot parse strings in integer fields. 
            for k_old, v in {
                "id": values.get("@id"),
                "type": type,
                "context": values.get("@context"),
                "drs_name": values.get("validation_key"),
                **{k: v for k, v in values.items() if not k.startswith("@")}
            }.items()
            for k_new in [k_old]
        }

        return self._model.model_validate(translated)
    
    
    
    
    
    
    
pycmipld(api.data_descriptors.HorizontalGridCells,**d)
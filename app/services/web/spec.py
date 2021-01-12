from pydantic import BaseModel
from pydantic.main import ModelMetaclass

from app.api import request, response

definitions = {}
base_types = {}
_default_root = '#/definitions/'
_replace_root = '#/components/schemas/'


def _is_schema_model(obj) -> bool:
    return obj.__class__ is ModelMetaclass and obj is not BaseModel


def _replace_refs(obj: dict) -> dict:
    if not isinstance(obj, dict):
        return obj

    for k, v in obj.items():
        if isinstance(v, list):
            obj[k] = [_replace_refs(i) for i in v]
        elif isinstance(v, dict):
            obj[k] = _replace_refs(v)
        elif k == '$ref' and v in base_types:
            obj = base_types[v]
        elif k == '$ref' and isinstance(v, str):
            obj[k] = v.replace(_default_root, _replace_root)

    return obj


def _update_definitions(module):
    for k, v in module.__dict__.items():
        if not _is_schema_model(v):
            continue

        schema: dict = v.schema()

        for ref_name, ref_schema in schema.pop('definitions', {}).items():
            if ref_schema.get('type') == 'object':
                definitions[ref_name] = ref_schema
            else:
                base_types[_default_root + ref_name] = ref_schema

        for prop_name, prop_schema in schema['properties'].items():
            if prop_schema.get('$ref') in base_types:
                schema['properties'][prop_name] = base_types[prop_schema.get('$ref')]

        definitions[k] = _replace_refs(schema)


_update_definitions(request)
_update_definitions(response)

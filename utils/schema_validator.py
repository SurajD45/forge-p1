import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError


def validate_trd(trd: dict):
    with open("schemas/trd_schema.json") as f:
        schema = json.load(f)

    try:
        validate(instance=trd, schema=schema)
    except ValidationError as e:
        raise ValueError(f"TRD validation failed:\n{e.message}")
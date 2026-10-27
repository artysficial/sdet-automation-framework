import json
from pathlib import Path

from jsonschema import validate

_SCHEMAS = Path(__file__).parent


def assert_matches_schema(instance: dict, schema_name: str) -> None:
    schema = json.loads((_SCHEMAS / f"{schema_name}.schema.json").read_text(encoding="utf-8"))
    validate(instance=instance, schema=schema)

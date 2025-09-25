import json
import os

import jsonschema
from jsonschema import validate

schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "curseforge": {"type": "string"},
            "source": {"type": ["string", "null"]},
        },
    },
    "required": ["name", "curseforge", "source"],
    "additionalProperties": False,
}


def list_sources(filename: str) -> list[str]:
    github_list = []
    with open(filename, "r") as f:
        try:
            data: list = json.load(f)
            validate(instance=data, schema=schema)

            for item in data:
                if item["source"] is None:
                    print("No source found")
                else:
                    print(f"Source         : {item['source']}")
                    github_list.append(item["source"])

        except jsonschema.ValidationError as e:
            print(f"Could not validate schema: {e.message}")

    return github_list


if __name__ == "__main__":
    github_list = list_sources("sandbox/mod_sources.json")

    for github in github_list:
        print(":q")

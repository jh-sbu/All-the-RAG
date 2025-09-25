import json
from tqdm import tqdm

from git import Repo

import jsonschema
from jsonschema import validate

import time

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


def list_sources(filename: str) -> list[dict]:
    github_list = []
    with open(filename, "r") as f:
        try:
            data: list = json.load(f)
            validate(instance=data, schema=schema)

            for item in data:
                if item["source"] is None:
                    # print("No source found")
                    pass
                else:
                    print(f"Name:          : {item['name']}")
                    print(f"Source         : {item['source']}")
                    github_list.append(item)

        except jsonschema.ValidationError as e:
            print(f"Could not validate schema: {e.message}")

    return github_list


if __name__ == "__main__":
    github_list = list_sources("sandbox/mod_sources.json")

    print(len(github_list))

    for github in tqdm(github_list):
        print(f"Downloading github {github['name']} from repo: {github['source']}")
        Repo.clone_from(github["source"], f"github_repos/{github['name']}")
        time.sleep(60)

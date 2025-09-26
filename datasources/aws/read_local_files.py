# from collections import namedtuple
import argparse
import json

import jsonschema

from preprocess_docs import IndexFile


index_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "repo_name": {"type": "string"},
            "file_abspath": {"type": "string"},
            "file_relpath": {"type": "string"},
            "repo_remote_origin": {"type": ["string", "null"]},
        },
    },
    "required": ["repo_name", "file_abspath", "file_relpath", "repo_remote_origin"],
    "additionalProperties": True,
}


def read_index_json(filename: str) -> list[IndexFile]:
    mds = []

    with open(filename, "r") as f:
        try:
            data = json.load(f)
            jsonschema.validate(data, index_schema)

            for item in data:
                if "repo_remote_origin" in item.keys():
                    # if item["source"] is not None:
                    mds.append(
                        IndexFile(
                            item["repo_name"],
                            item["file_abspath"],
                            item["file_relpath"],
                            item["repo_remote_origin"],
                        )
                    )

        except jsonschema.ValidationError as e:
            print(f"Could not validate source list: {e.message}")

    return mds


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    stuff = read_index_json(args.filename)

    print("Read file")

    for thing in stuff:
        print(f"Thing: {thing}")

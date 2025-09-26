from pathlib import Path
import boto3
import json
import os
from mypy_boto3_bedrock_runtime.client import BedrockRuntimeClient
from chunk_text import chunk_text

from dotenv import load_dotenv

from typing import NamedTuple


class IndexFile(NamedTuple):
    repo_name: str
    filepath: str
    file_relpath: str
    repo_remote_origin: str


load_dotenv()

BUCKET_NAME = os.environ.get("BUCKET_NAME") or ""
INDEX_NAME = os.environ.get("INDEX_NAME") or ""
MODEL_ID = os.environ.get("MODEL_ID") or ""
PROFILE_NAME = os.environ.get("PROFILE_NAME") or ""
REGION_NAME = os.environ.get("REGION_NAME") or ""

if BUCKET_NAME == "":
    raise RuntimeError("Could not read BUCKET_NAME from environment")

if INDEX_NAME == "":
    raise RuntimeError("Could not read INDEX_NAME from environment")

if MODEL_ID == "":
    raise RuntimeError("Could not read MODEL_ID from environment")

if PROFILE_NAME == "":
    raise RuntimeError("Could not read PROFILE_NAME from environment")

if REGION_NAME == "":
    raise RuntimeError("Could not read REGION_NAME from environment")


def build_message(text: str) -> dict:
    return {
        "inputText": text,
        "dimensions": 256,
        "normalize": True,
    }


def chunk_and_upload(
    docs: list[IndexFile], chunk_size: int = 1000, overlap: int = 200
) -> None:
    session = boto3.Session(profile_name=PROFILE_NAME)
    s3vectors = session.client("s3vectors", region_name=REGION_NAME)

    bedrock: BedrockRuntimeClient = session.client(
        "bedrock-runtime", region_name=REGION_NAME
    )
    for reponame, filepath, file_relpath, repo_remote_origin in docs:
        with open(filepath, "r") as f:
            doc = f.read()

        filename = Path(file_relpath).name

        chunks = chunk_text(doc, chunk_size=chunk_size, overlap=overlap)

        vectors = []

        for i, chunk in enumerate(chunks):
            req = build_message(chunk)

            # Embed the chunk
            # res = bedrock.invoke_model(
            #     modelId=MODEL_ID,
            #     body=json.dumps(req),
            #     accept="application/json",
            #     contentType="application/json",
            # )

            # payload = json.loads(res["body"].read())
            # vector = payload.get("embedding") or payload["embeddingsByType"]["float"]

            vector = [1.0, 2.0, 3.0]

            # Create a dictionary for uploading to S3 vectors

            new_vec = {
                "key": f"vector-{reponame}-{filename}-{i}",
                "data": {"float32": vector},
                "metadata": {
                    "url": repo_remote_origin,
                    "summary": "NOT IMPLEMENTED",
                    "category": "NOT IMPLEMENTED",
                    "text": chunk,
                },
            }

            print("Created new dict:")
            print(f"Filename: {filename}")
            print(new_vec)
            print("\n\n")

            vectors.append(new_vec)

        # Upload this doc's vectors to s3
        # res = s3vectors.put_vectors(
        #     vectorBucketName=BUCKET_NAME, indexName=INDEX_NAME, vectors=vectors
        # )

        # print("Got Response:")
        # print(res)

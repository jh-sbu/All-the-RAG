import boto3
import json
import os
from mypy_boto3_bedrock_runtime.client import BedrockRuntimeClient
from chunk_text import chunk_text

from dotenv import load_dotenv

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
    docs: list[str], chunk_size: int = 1000, overlap: int = 200
) -> None:
    session = boto3.Session(profile_name=PROFILE_NAME)

    bedrock: BedrockRuntimeClient = session.client(
        "bedrock-runtime", region_name=REGION_NAME
    )
    for doc in docs:
        chunks = chunk_text(doc, chunk_size=chunk_size, overlap=overlap)

        for chunk in chunks:
            req = build_message(chunk)

            # Embed the chunk
            res = bedrock.invoke_model(
                modelId=MODEL_ID,
                body=json.dumps(req),
                accept="application/json",
                contentType="application/json",
            )

            payload = json.loads(res["body"].read())
            vector = payload.get("embedding") or payload["embeddingsByType"]["float"]

            print("Vector:")
            print(vector)
            print("\n\n")

            # Create a dictionary for uploading to S3 vectors

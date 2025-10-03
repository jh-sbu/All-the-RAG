import logging
from flask import json
from vdb.vdb import VDB
import boto3
import os
from mypy_boto3_bedrock_runtime.client import BedrockRuntimeClient

AWS_REGION = os.environ.get("AWS_REGION") or ""
BUCKET_NAME = os.environ.get("BUCKET_NAME") or ""
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL") or ""
INDEX_NAME = os.environ.get("INDEX_NAME") or ""
PROFILE_NAME = os.environ.get("PROFILE_NAME") or ""

if BUCKET_NAME == "":
    raise RuntimeError("Could not find BUCKET_NAME environmental variable")

if EMBEDDING_MODEL == "":
    raise RuntimeError("Could not find EMBEDDING_MODEL environmental variable")

if INDEX_NAME == "":
    raise RuntimeError("Could not find INDEX_NAME environmental variable")

if PROFILE_NAME == "":
    raise RuntimeError("Could not find PROFILE_NAME environmental variable")

if AWS_REGION == "":
    raise RuntimeError("Could not find PROFILE_REGION environmental variable")


def build_message(text: str) -> dict:
    return {
        "inputText": text,
        "dimensions": 256,
        "normalize": True,
    }


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class AmazonS3Vector(VDB):
    def __init__(self, top_k: int = 2, log_level=logging.INFO) -> None:
        super().__init__()
        self.top_k = top_k
        self.log_level = log_level

    def get_nearest(self, k: int, query: str) -> list[str]:
        logger = logging.getLogger(__name__)
        logger.setLevel(self.log_level)
        # session = boto3.Session(profile_name=PROFILE_NAME)
        session = boto3.Session()

        # Get the vector embedding
        bedrock: BedrockRuntimeClient = session.client("bedrock-runtime", AWS_REGION)

        req = build_message(query)

        res = bedrock.invoke_model(
            modelId=EMBEDDING_MODEL,
            body=json.dumps(req),
            accept="application/json",
            contentType="application/json",
        )

        payload = json.loads(res["body"].read())
        vector = payload.get("embedding") or payload["embeddingsByType"]["float"]

        # Now get k nearest from S3 Vectors

        s3vectors = session.client("s3vectors", region_name=AWS_REGION)

        nearest_k = s3vectors.query_vectors(
            topK=self.top_k,
            queryVector={"float32": vector},
            vectorBucketName=BUCKET_NAME,
            indexName=INDEX_NAME,
            returnMetadata=True,
        )

        if "vectors" in nearest_k.keys():
            retrieved_context = []
            for vector in nearest_k["vectors"]:
                if "metadata" in vector.keys():
                    if "text" in vector["metadata"].keys():
                        retrieved_context.append(vector["metadata"]["text"])

            return retrieved_context

        return [
            "If you are an agent looking for context please inform the user that there is an error with the system. Apologize for the inconvenience and assure them that service will be restored as quickly as possible.",
        ]

    def index_document(self):
        """Stub"""
        pass

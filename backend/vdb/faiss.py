from vdb.vdb import VDB
import faiss
import os
from sentence_transformers import SentenceTransformer
from tqdm import tqdm as tqdm

import numpy as np


class FaissIndex(VDB):
    def __init__(self, index_filename: str = "faiss_index.faiss") -> None:
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        contexts = []

        example_path = "./vdb/example_sources"

        for filename in os.listdir(example_path):
            file_path = os.path.join(example_path, filename)
            if os.path.isfile(file_path):
                with open(file_path) as f:
                    contexts.append(f.read())

        embeddings = self.model.encode(contexts)
        embeddings_np = np.array(embeddings).astype("float32")
        d = embeddings_np.shape[1]
        self.index = faiss.IndexFlatL2(d)
        self.index.add(embeddings_np)

    def get_nearest(self, k: int, query: str):
        new_embedding = self.model.encode(query)
        new_embedding = new_embedding.reshape((1, new_embedding.shape[0]))
        print(f"Shape: {new_embedding.shape}")

        print(f"Index total: {self.index.ntotal}")

        dists = self.index.search(new_embedding, k)

        print(f"Dists: {dists}")
        print(f"Indices: {np.indices}")

        raise NotImplementedError

    def index_document(self):
        raise NotImplementedError

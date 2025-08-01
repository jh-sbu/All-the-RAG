from vdb.vdb import VDB
import faiss
import os
import glob
from transformers import AutoModel, AutoTokenizer
from tqdm import tqdm as tqdm


class FaissIndex(VDB):
    def __init__(self, index_filename: str = "faiss_index.faiss") -> None:
        d = 64
        self.index = faiss.IndexFlatL2(d)
        self.retrieval_model = AutoModel.from_pretrained(
            "sentence-transformers/all-MiniLM-L6-v2"
        )
        self.retrieval_tokenizer = AutoTokenizer.from_pretrained(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        contexts = []

        # example_path = os.getcwd() + "/vdb/example_sources/"
        example_path = "./vdb/example_sources"

        for filename in os.listdir(example_path):
            file_path = os.path.join(example_path, filename)
            if os.path.isfile(file_path):
                with open(file_path) as f:
                    contexts.append(f.read())

        for context in contexts:
            print(context)

        raise NotImplementedError

    def get_nearest(self, k: int):
        raise NotImplementedError

    def index_document(self):
        raise NotImplementedError

from vdb.vdb import VDB


class FaissIndex(VDB):
    def __init__(self) -> None:
        raise NotImplementedError

    def get_nearest(self, k: int):
        raise NotImplementedError

    def index_document(self):
        raise NotImplementedError

import abc


class VDB(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_nearest(self, k: int):
        """
        Get the k nearest matches stored in the vector DB
        """
        raise NotImplementedError

    @abc.abstractmethod
    def index_document(self):
        """
        Index a document and add it to the vector DB
        """
        raise NotImplementedError

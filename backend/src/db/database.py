import abc


class Database(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def createUser():
        """
        Create a user
        """
        raise NotImplementedError

    @abc.abstractmethod
    def readUser():
        """
        Read a user
        """
        raise NotImplementedError

    @abc.abstractmethod
    def updateUser():
        """
        Update a user
        """
        raise NotImplementedError

    @abc.abstractmethod
    def deleteUser():
        """
        Delete a user
        """
        raise NotImplementedError

    @abc.abstractmethod
    def createChat():
        """
        Create a chat
        """
        raise NotImplementedError

    @abc.abstractmethod
    def readChat():
        """
        Read a chat
        """
        raise NotImplementedError

    @abc.abstractmethod
    def updateChat():
        """
        Update a chat
        """
        raise NotImplementedError

    @abc.abstractmethod
    def deleteChat():
        """
        Delete a chat
        """
        raise NotImplementedError

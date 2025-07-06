from models.base import BaseMongoModel


class Supplier(BaseMongoModel):
    collection_name = "supplier"

    def __init__(self):
        self.__uuid = None
        self.__name = None
        self.__createTime = None
        self.__updateTime = None
        self.__deleted = None

    @property
    def uuid(self):
        return self.__uuid

    @uuid.setter
    def uuid(self, value):
        self.__uuid = value

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def createTime(self):
        return self.__createTime

    @createTime.setter
    def createTime(self, value):
        self.__createTime = value

    @property
    def updateTime(self):
        return self.__updateTime

    @updateTime.setter
    def updateTime(self, value):
        self.__updateTime = value

    @property
    def deleted(self):
        return self.__deleted

    @deleted.setter
    def deleted(self, value):
        self.__deleted = value

    def to_dict(self):
        return {
            'uuid': self.__uuid,
            'name': self.__name,
            'createTime': self.__createTime,
            'updateTime': self.__updateTime,
            'deleted': self.__deleted,
        }

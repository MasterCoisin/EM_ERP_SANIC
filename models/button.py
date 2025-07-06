from models.base import BaseMongoModel


class Button(BaseMongoModel):
    collection_name = "button"

    def __init__(self):
        self.__permission_code = None
        self.__name = None
        self.__createTime = None
        self.__updateTime = None
        self.__deleted = None

    @property
    def permission_code(self):
        return self.__permission_code

    @permission_code.setter
    def permission_code(self, value):
        self.__permission_code = value

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
            'permission_code': self.__permission_code,
            'name': self.__name,
            'createTime': self.__createTime,
            'updateTime': self.__updateTime,
            'deleted': self.__deleted,
        }

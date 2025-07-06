from models.base import BaseMongoModel


class ConfigData(BaseMongoModel):
    collection_name = "config_data"

    def __init__(self):
        self.__field_name = None
        self.__data = None
        self.__createTime = None
        self.__updateTime = None
        self.__deleted = None

    @property
    def field_name(self):
        return self.__field_name

    @field_name.setter
    def field_name(self, value):
        self.__field_name = value

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value):
        self.__data = value

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
            'field_name': self.__field_name,
            'data': self.__data,
            'createTime': self.__createTime,
            'updateTime': self.__updateTime,
            'deleted': self.__deleted,
        }

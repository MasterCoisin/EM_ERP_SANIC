from models.base import BaseMongoModel


class Route(BaseMongoModel):
    collection_name = "route"

    def __init__(self):
        self.__path = None
        self.__name = None
        self.__meta = None
        self.__linkUrl = None
        self.__deleted = None

    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, value):
        self.__path = value

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def meta(self):
        return self.__meta

    @meta.setter
    def meta(self, value):
        self.__meta = value

    @property
    def linkUrl(self):
        return self.__linkUrl

    @linkUrl.setter
    def linkUrl(self, value):
        self.__linkUrl = value

    @property
    def deleted(self):
        return self.__deleted

    @deleted.setter
    def deleted(self, value):
        self.__deleted = value

    def to_dict(self):
        return {
            'path': self.__path,
            'name': self.__name,
            'meta': self.__meta,
            'linkUrl': self.__linkUrl,
            'deleted': self.__deleted,
        }

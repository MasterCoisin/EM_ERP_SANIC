from models.base import BaseMongoModel


class Festival(BaseMongoModel):
    collection_name = "festival"

    def __init__(self):
        self.__festival_code = None
        self.__festival_name = None
        self.__deleted = None

    @property
    def festival_code(self):
        return self.__festival_code

    @festival_code.setter
    def festival_code(self, value):
        self.__festival_code = value

    @property
    def festival_name(self):
        return self.__festival_name

    @festival_name.setter
    def festival_name(self, value):
        self.__festival_name = value

    @property
    def deleted(self):
        return self.__deleted

    @deleted.setter
    def deleted(self, value):
        self.__deleted = value

    def to_dict(self):
        return {
            'festival_code': self.__festival_code,
            'festival_name': self.__festival_name,
            'deleted': self.__deleted,
        }

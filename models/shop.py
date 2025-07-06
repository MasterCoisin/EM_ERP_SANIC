from models.base import BaseMongoModel


class Shop(BaseMongoModel):
    collection_name = "shop"

    def __init__(self):
        self.__shop_id = None
        self.__shop_name = None
        self.__company_info = None
        self.__rep = None
        self.__token1688 = None
        self.__deleted = None

    @property
    def shop_id(self):
        return self.__shop_id

    @shop_id.setter
    def shop_id(self, value):
        self.__shop_id = value

    @property
    def shop_name(self):
        return self.__shop_name

    @shop_name.setter
    def shop_name(self, value):
        self.__shop_name = value

    @property
    def company_info(self):
        return self.__company_info

    @company_info.setter
    def company_info(self, value):
        self.__company_info = value

    @property
    def rep(self):
        return self.__rep

    @rep.setter
    def rep(self, value):
        self.__rep = value

    @property
    def token1688(self):
        return self.__token1688

    @token1688.setter
    def token1688(self, value):
        self.__token1688 = value

    @property
    def deleted(self):
        return self.__deleted

    @deleted.setter
    def deleted(self, value):
        self.__deleted = value

    def to_dict(self):
        return {
            'shop_id': self.__shop_id,
            'shop_name': self.__shop_name,
            'company_info': self.__company_info,
            'rep': self.__rep,
            'token1688': self.__token1688,
            'deleted': self.__deleted,
        }

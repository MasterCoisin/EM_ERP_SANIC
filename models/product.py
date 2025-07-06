from models.base import BaseMongoModel


class Product(BaseMongoModel):
    collection_name = "product"

    def __init__(self):
        self.__sku = None
        self.__productName = None
        self.__url1688 = None
        self.__images = None
        self.__tip = None
        self.__competitorUrls = None
        self.__length = None
        self.__width = None
        self.__height = None
        self.__weight = None
        self.__volumeWeight = None
        self.__weighing = None
        self.__supplierInfo = None
        self.__createTime = None
        self.__updateTime = None
        self.__deleted = None

    @property
    def sku(self):
        return self.__sku

    @sku.setter
    def sku(self, value):
        self.__sku = value

    @property
    def productName(self):
        return self.__productName

    @productName.setter
    def productName(self, value):
        self.__productName = value

    @property
    def url1688(self):
        return self.__url1688

    @url1688.setter
    def url1688(self, value):
        self.__url1688 = value

    @property
    def images(self):
        return self.__images

    @images.setter
    def images(self, value):
        self.__images = value

    @property
    def tip(self):
        return self.__tip

    @tip.setter
    def tip(self, value):
        self.__tip = value

    @property
    def competitorUrls(self):
        return self.__competitorUrls

    @competitorUrls.setter
    def competitorUrls(self, value):
        self.__competitorUrls = value

    @property
    def length(self):
        return self.__length

    @length.setter
    def length(self, value):
        self.__length = value

    @property
    def width(self):
        return self.__width

    @width.setter
    def width(self, value):
        self.__width = value

    @property
    def height(self):
        return self.__height

    @height.setter
    def height(self, value):
        self.__height = value

    @property
    def weight(self):
        return self.__weight

    @weight.setter
    def weight(self, value):
        self.__weight = value

    @property
    def volumeWeight(self):
        return self.__volumeWeight

    @volumeWeight.setter
    def volumeWeight(self, value):
        self.__volumeWeight = value

    @property
    def weighing(self):
        return self.__weighing

    @weighing.setter
    def weighing(self, value):
        self.__weighing = value

    @property
    def supplierInfo(self):
        return self.__supplierInfo

    @supplierInfo.setter
    def supplierInfo(self, value):
        self.__supplierInfo = value

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
            'sku': self.__sku,
            'productName': self.__productName,
            'url1688': self.__url1688,
            'images': self.__images,
            'tip': self.__tip,
            'competitorUrls': self.__competitorUrls,
            'length': self.__length,
            'width': self.__width,
            'height': self.__height,
            'weight': self.__weight,
            'volumeWeight': self.__volumeWeight,
            'weighing': self.__weighing,
            'supplierInfo': self.__supplierInfo,
            'createTime': self.__createTime,
            'updateTime': self.__updateTime,
            'deleted': self.__deleted,
        }

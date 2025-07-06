from models.base import BaseMongoModel


class Listing(BaseMongoModel):
	collection_name="listing"
	def __init__(self):
		self.__ean = None
		self.__msku = None
		self.__listingName = None
		self.__images = None
		self.__baseInfo = None
		self.__emAttribute = None
		self.__logisticsAttributes = None
		self.__flag = None
		self.__invoiceInfo = None
		self.__gprs = None
		self.__addFee = None
		self.__skuList = None
		self.__packingList = None
		self.__profitCalResult = None
		self.__productProfitCalData = None
		self.__tip = None
		self.__shop = None
		self.__emSaleInfo = None
		self.__createTime = None
		self.__updateTime = None
		self.__deleted = None
	

	@property
	def ean(self):
		return self.__ean

	@ean.setter
	def ean(self, value):
		self.__ean = value

	@property
	def msku(self):
		return self.__msku

	@msku.setter
	def msku(self, value):
		self.__msku = value

	@property
	def listingName(self):
		return self.__listingName

	@listingName.setter
	def listingName(self, value):
		self.__listingName = value

	@property
	def images(self):
		return self.__images

	@images.setter
	def images(self, value):
		self.__images = value

	@property
	def baseInfo(self):
		return self.__baseInfo

	@baseInfo.setter
	def baseInfo(self, value):
		self.__baseInfo = value

	@property
	def emAttribute(self):
		return self.__emAttribute

	@emAttribute.setter
	def emAttribute(self, value):
		self.__emAttribute = value

	@property
	def logisticsAttributes(self):
		return self.__logisticsAttributes

	@logisticsAttributes.setter
	def logisticsAttributes(self, value):
		self.__logisticsAttributes = value

	@property
	def flag(self):
		return self.__flag

	@flag.setter
	def flag(self, value):
		self.__flag = value

	@property
	def invoiceInfo(self):
		return self.__invoiceInfo

	@invoiceInfo.setter
	def invoiceInfo(self, value):
		self.__invoiceInfo = value

	@property
	def gprs(self):
		return self.__gprs

	@gprs.setter
	def gprs(self, value):
		self.__gprs = value

	@property
	def addFee(self):
		return self.__addFee

	@addFee.setter
	def addFee(self, value):
		self.__addFee = value

	@property
	def skuList(self):
		return self.__skuList

	@skuList.setter
	def skuList(self, value):
		self.__skuList = value

	@property
	def packingList(self):
		return self.__packingList

	@packingList.setter
	def packingList(self, value):
		self.__packingList = value

	@property
	def profitCalResult(self):
		return self.__profitCalResult

	@profitCalResult.setter
	def profitCalResult(self, value):
		self.__profitCalResult = value

	@property
	def productProfitCalData(self):
		return self.__productProfitCalData

	@productProfitCalData.setter
	def productProfitCalData(self, value):
		self.__productProfitCalData = value

	@property
	def tip(self):
		return self.__tip

	@tip.setter
	def tip(self, value):
		self.__tip = value

	@property
	def shop(self):
		return self.__shop

	@shop.setter
	def shop(self, value):
		self.__shop = value

	@property
	def emSaleInfo(self):
		return self.__emSaleInfo

	@emSaleInfo.setter
	def emSaleInfo(self, value):
		self.__emSaleInfo = value

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
			'ean':self.__ean,
			'msku':self.__msku,
			'listingName':self.__listingName,
			'images':self.__images,
			'baseInfo':self.__baseInfo,
			'emAttribute':self.__emAttribute,
			'logisticsAttributes':self.__logisticsAttributes,
			'flag':self.__flag,
			'invoiceInfo':self.__invoiceInfo,
			'gprs':self.__gprs,
			'addFee':self.__addFee,
			'skuList':self.__skuList,
			'packingList':self.__packingList,
			'profitCalResult':self.__profitCalResult,
			'productProfitCalData':self.__productProfitCalData,
			'tip':self.__tip,
			'shop':self.__shop,
			'emSaleInfo':self.__emSaleInfo,
			'createTime':self.__createTime,
			'updateTime':self.__updateTime,
			'deleted':self.__deleted,
			}

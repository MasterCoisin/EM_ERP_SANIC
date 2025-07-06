from models.base import BaseMongoModel


class OrderManager(BaseMongoModel):
	collection_name = "order_manager"

	def __init__(self):
		self.__orderId = None
		self.__supplierUuid = None
		self.__purchaseOrderId = None
		self.__status = None
		self.__tradeInfo = None
		self.__createTime = None
		self.__updateTime = None
		self.__deleted = None
	

	@property
	def orderId(self):
		return self.__orderId

	@orderId.setter
	def orderId(self, value):
		self.__orderId = value

	@property
	def supplierUuid(self):
		return self.__supplierUuid

	@supplierUuid.setter
	def supplierUuid(self, value):
		self.__supplierUuid = value

	@property
	def purchaseOrderId(self):
		return self.__purchaseOrderId

	@purchaseOrderId.setter
	def purchaseOrderId(self, value):
		self.__purchaseOrderId = value

	@property
	def status(self):
		return self.__status

	@status.setter
	def status(self, value):
		self.__status = value

	@property
	def tradeInfo(self):
		return self.__tradeInfo

	@tradeInfo.setter
	def tradeInfo(self, value):
		self.__tradeInfo = value

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
			'orderId':self.__orderId,
			'supplierUuid':self.__supplierUuid,
			'purchaseOrderId':self.__purchaseOrderId,
			'status':self.__status,
			'tradeInfo':self.__tradeInfo,
			'createTime':self.__createTime,
			'updateTime':self.__updateTime,
			'deleted':self.__deleted,
			}

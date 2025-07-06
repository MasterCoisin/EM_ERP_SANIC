from models.base import BaseMongoModel


class OverseasWarehouse(BaseMongoModel):
	collection_name = "overseas_warehouse"

	def __init__(self):
		self.__whId = None
		self.__whName = None
		self.__createTime = None
		self.__updateTime = None
		self.__deleted = None
	

	@property
	def whId(self):
		return self.__whId

	@whId.setter
	def whId(self, value):
		self.__whId = value

	@property
	def whName(self):
		return self.__whName

	@whName.setter
	def whName(self, value):
		self.__whName = value

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
			'whId':self.__whId,
			'whName':self.__whName,
			'createTime':self.__createTime,
			'updateTime':self.__updateTime,
			'deleted':self.__deleted,
			}

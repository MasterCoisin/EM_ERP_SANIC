from models.base import BaseMongoModel


class SkuInventoryIndex(BaseMongoModel):
	collection_name = 'sku_inventory_index'

	def __init__(self):
		self.__createTime = None
		self.__updateTime = None
		self.__deleted = None
	

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
			'createTime':self.__createTime,
			'updateTime':self.__updateTime,
			'deleted':self.__deleted,
			}

from models.base import BaseMongoModel


class SkuWarehouse(BaseMongoModel):
	collection_name = "sku_warehouse"

	def __init__(self):
		self.__sku = None
	

	@property
	def sku(self):
		return self.__sku

	@sku.setter
	def sku(self, value):
		self.__sku = value

	def to_dict(self):
		return {
			'sku':self.__sku,
			}

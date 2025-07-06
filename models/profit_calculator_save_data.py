from models.base import BaseMongoModel


class ProfitCalculatorSaveData(BaseMongoModel):
	collection_name = "profit_calculator_save_data"

	def __init__(self):
		self.__uuid = None
		self.__createTime = None
		self.__updateTime = None
		self.__deleted = None
	

	@property
	def uuid(self):
		return self.__uuid

	@uuid.setter
	def uuid(self, value):
		self.__uuid = value

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
			'uuid':self.__uuid,
			'createTime':self.__createTime,
			'updateTime':self.__updateTime,
			'deleted':self.__deleted,
			}

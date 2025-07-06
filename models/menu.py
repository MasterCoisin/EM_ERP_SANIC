from models.base import BaseMongoModel


class Menu(BaseMongoModel):
	collection_name = "menu"

	def __init__(self):
		self.__nodeId = None
		self.__parentId = None
		self.__title = None
		self.__tabId = None
		self.__createTime = None
		self.__updateTime = None
		self.__deleted = None
	

	@property
	def nodeId(self):
		return self.__nodeId

	@nodeId.setter
	def nodeId(self, value):
		self.__nodeId = value

	@property
	def parentId(self):
		return self.__parentId

	@parentId.setter
	def parentId(self, value):
		self.__parentId = value

	@property
	def title(self):
		return self.__title

	@title.setter
	def title(self, value):
		self.__title = value

	@property
	def tabId(self):
		return self.__tabId

	@tabId.setter
	def tabId(self, value):
		self.__tabId = value

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
			'nodeId':self.__nodeId,
			'parentId':self.__parentId,
			'title':self.__title,
			'tabId':self.__tabId,
			'createTime':self.__createTime,
			'updateTime':self.__updateTime,
			'deleted':self.__deleted,
			}

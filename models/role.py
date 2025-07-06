from models.base import BaseMongoModel


class Role(BaseMongoModel):
	collection_name = "role"

	def __init__(self):
		self.__role_code = None
		self.__role_name = None
		self.__routers = None
		self.__permissionsCode = None
		self.__menus = None
		self.__createTime = None
		self.__updateTime = None
		self.__deleted = None
	

	@property
	def role_code(self):
		return self.__role_code

	@role_code.setter
	def role_code(self, value):
		self.__role_code = value

	@property
	def role_name(self):
		return self.__role_name

	@role_name.setter
	def role_name(self, value):
		self.__role_name = value

	@property
	def routers(self):
		return self.__routers

	@routers.setter
	def routers(self, value):
		self.__routers = value

	@property
	def permissionsCode(self):
		return self.__permissionsCode

	@permissionsCode.setter
	def permissionsCode(self, value):
		self.__permissionsCode = value

	@property
	def menus(self):
		return self.__menus

	@menus.setter
	def menus(self, value):
		self.__menus = value

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
			'role_code':self.__role_code,
			'role_name':self.__role_name,
			'routers':self.__routers,
			'permissionsCode':self.__permissionsCode,
			'menus':self.__menus,
			'createTime':self.__createTime,
			'updateTime':self.__updateTime,
			'deleted':self.__deleted,
			}

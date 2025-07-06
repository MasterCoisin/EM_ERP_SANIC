class SysUser():
    collection_name = "sys_user"

    def __init__(self):
        self.__avatar_big = None
        self.__avatar_middle = None
        self.__avatar_thumb = None
        self.__avatar_url = None
        self.__email = None
        self.__employee_no = None
        self.__en_name = None
        self.__enterprise_email = None
        self.__mobile = None
        self.__name = None
        self.__open_id = None
        self.__tenant_key = None
        self.__union_id = None
        self.__user_id = None

    @property
    def avatar_big(self):
        return self.__avatar_big

    @avatar_big.setter
    def avatar_big(self, value):
        self.__avatar_big = value

    @property
    def avatar_middle(self):
        return self.__avatar_middle

    @avatar_middle.setter
    def avatar_middle(self, value):
        self.__avatar_middle = value

    @property
    def avatar_thumb(self):
        return self.__avatar_thumb

    @avatar_thumb.setter
    def avatar_thumb(self, value):
        self.__avatar_thumb = value

    @property
    def avatar_url(self):
        return self.__avatar_url

    @avatar_url.setter
    def avatar_url(self, value):
        self.__avatar_url = value

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, value):
        self.__email = value

    @property
    def employee_no(self):
        return self.__employee_no

    @employee_no.setter
    def employee_no(self, value):
        self.__employee_no = value

    @property
    def en_name(self):
        return self.__en_name

    @en_name.setter
    def en_name(self, value):
        self.__en_name = value

    @property
    def enterprise_email(self):
        return self.__enterprise_email

    @enterprise_email.setter
    def enterprise_email(self, value):
        self.__enterprise_email = value

    @property
    def mobile(self):
        return self.__mobile

    @mobile.setter
    def mobile(self, value):
        self.__mobile = value

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def open_id(self):
        return self.__open_id

    @open_id.setter
    def open_id(self, value):
        self.__open_id = value

    @property
    def tenant_key(self):
        return self.__tenant_key

    @tenant_key.setter
    def tenant_key(self, value):
        self.__tenant_key = value

    @property
    def union_id(self):
        return self.__union_id

    @union_id.setter
    def union_id(self, value):
        self.__union_id = value

    @property
    def user_id(self):
        return self.__user_id

    @user_id.setter
    def user_id(self, value):
        self.__user_id = value

    def to_dict(self):
        return {
            'avatar_big': self.__avatar_big,
            'avatar_middle': self.__avatar_middle,
            'avatar_thumb': self.__avatar_thumb,
            'avatar_url': self.__avatar_url,
            'email': self.__email,
            'employee_no': self.__employee_no,
            'en_name': self.__en_name,
            'enterprise_email': self.__enterprise_email,
            'mobile': self.__mobile,
            'name': self.__name,
            'open_id': self.__open_id,
            'tenant_key': self.__tenant_key,
            'union_id': self.__union_id,
            'user_id': self.__user_id,
        }

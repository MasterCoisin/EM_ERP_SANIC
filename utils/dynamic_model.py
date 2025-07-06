import copy
from mongoengine import *


class BaseDynamicModel(object):
    def __init__(self, model_meta):
        self.model_meta = model_meta
        self.meta = copy.deepcopy(model_meta.get("meta", {}))
        self.models = {}

    def __product_model(self, version: int):
        """
        :param version:
        :return:
        """
        if version == "base":
            field = copy.deepcopy(self.model_meta['field'])
            meta = copy.deepcopy(self.meta)
            field['meta'] = meta
            self.models[version] = type('Test', (DynamicDocument,), field)
        else:
            meta = copy.deepcopy(self.meta)
            meta['collection'] += f'_{version}'
            # meta['db_alias'] += f'_{version}'
            field = copy.deepcopy(self.model_meta['field'])
            field['meta'] = meta
            self.models[version] = type(meta['collection'], (DynamicDocument,), field)
        self.connect_mongo(version)

    def connect_mongo(self, version):
        if version == "base":
            connect(**self.model_meta['db'])
            return
        db = copy.deepcopy(self.model_meta['db'])
        # db['alias'] += f'_{version}'
        connect(**db)

    def get_model(self, version, need_return=True):
        if version not in self.models:
            self.__product_model(version=version)
        if need_return:
            return self.models[version]

import json, decimal


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        super(DecimalEncoder, self).default(o)


def read_json(path):
    '''
    读取json文件
    :param path:
    :return:
    '''
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            f.close()
            return data
    except:
        print("error", path)


def save_json(data, path, debug=False):
    '''
    读取json文件
    :param data:
    :param path:
    :param debug
    :return:
    '''
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, cls=DecimalEncoder,ensure_ascii=False)
        f.close()
    if debug:
        print(f"save to {path}!")

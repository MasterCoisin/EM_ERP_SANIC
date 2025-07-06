from hashlib import md5
from utils.models import ModelManager
from bson import ObjectId

sys_user_model = ModelManager.get_model("sys_user", "base")



def get_md5(s):
    return str(md5(s.encode()).hexdigest())


def craete_user(username, password, isAdmin):
    if sys_user_model.objects(userName=username).first():
        return False, "用户名已存在"
    else:
        sys_user_model(userName=username, password=get_md5(password), isAdmin=isAdmin).save()
        return True, username

def check_login(username, password):
    if sys_user_model.objects(userName=username, password=get_md5(password)).first():
        return True, sys_user_model.objects(userName=username).first().isAdmin
    return False, None


def get_sys_user_type(username):
    return sys_user_model.objects(userName=username).first().isAdmin


def get_all_sys_user_data():
    data = [i.to_mongo().to_dict() for i in sys_user_model.objects()]
    print(data)
    for i in data:
        i["_id"] = str(i["_id"])
        del i["password"]
    return data


def delete_user(id):
    try:
        if not id:
            return
        sys_user_model.objects(_id=ObjectId(id)).delete()
    except:
        pass


def change_psw_(id, psw):
    try:
        print(id,psw)

        if not id:
            return False
        obj = sys_user_model.objects(_id=ObjectId(id)).first()
        obj.password = get_md5(psw)
        obj.save()
        return True
    except Exception as e:
        print(e)
        return False

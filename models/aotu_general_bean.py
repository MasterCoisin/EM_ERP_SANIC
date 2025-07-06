# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：aotu_general_bean.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024-11-18 1:04 
-------------------------------------
'''
from functools import reduce


class MyTools():
    @staticmethod
    def MakeClass(className,db_name, filepath, P_Father=[], p=[]):
        """
            自动生成类和getter setter
        :param className: 类名字符串
        :param filepath: 路径字符串，最好绝对路径，如果生成在当前目录就写空字符串
        :param P_Father: 继承的父类和父类参数列表，格式如下
                [
                    ["父类1","父类1第一个参数名或值","父类1第二个参数名或值","父类1第三个参数名或值",……],
                    ["父类2","父类2第一个参数名或值","父类2第二个参数名或值","父类2第三个参数名或值",……]
                ]
        :param p: 类中的属性列表
        :return:
        """
        lines = [
            "from models.base import BaseMongoModel\n\n"
            "\nclass {0}(".format(className) + (
                reduce(lambda a, b: a[0] + ", " + b[0], P_Father) if P_Father else "") + "):",
            "\tcollection_name = '"+db_name+"'\n\n"
            "\tdef __init__(self):"
        ]

        # for superClass in P_Father:
        #     str = "\t\t{0}.__init__(self".format(superClass[0]) + ((", " + reduce(lambda a, b: a + ", " + b, superClass[1:])) if superClass[1:] else "") + ")"
        #     lines.append(str)
        #     pass

        lines += ["\t\tself.__{0} = None".format(param) for param in p]
        lines += ["\t", ""]

        for param in p:
            methodLines = []
            methodLines.append("\t@property")
            methodLines.append("\tdef {0}(self):".format(param))
            methodLines.append("\t\treturn self.__{0}".format(param))
            methodLines.append("")
            methodLines.append("\t@{0}.setter".format(param))
            methodLines.append("\tdef {0}(self, value):".format(param))
            methodLines.append("\t\tself.__{0} = value".format(param))
            methodLines.append("")
            lines += methodLines
            pass
        str = "+ (", " + reduce(lambda a, b: a + ", " + b, p_属性列表) if p_属性列表 else "") + "
        lines.append("\tdef to_dict(self):")
        lines.append('\t\treturn {')
        lines += ['\t\t\t{0}:{1},'.format("'" + p1 + "'", 'self.__' + p2) for p1, p2 in zip(p, p)]
        lines.append('\t\t\t}')
        print(lines)
        lines = [i + "\n" for i in lines]
        with open(filepath, "w", encoding="utf-8") as fp:
            fp.writelines(lines)
            print("类{0}生成成功".format(className))
            pass
        pass

    pass


MyTools.MakeClass("rootAnalysis","root_analysis", "root_analysis.py", P_Father=["BaseMongoModel"],
                  p=["createTime",
                     "updateTime", "deleted"])

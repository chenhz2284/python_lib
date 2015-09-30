# encoding: utf8


from common_util import DictUtil, JSONUtil



def printObject(obj):
    print(JSONUtil.toJSONString(DictUtil.toDictionary(obj), indent=6) )
    
        








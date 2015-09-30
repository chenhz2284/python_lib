# encoding: utf8


import json


def toJSONString(obj, encoding="utf8", indent=None):
    if indent==None:
        return json.dumps(obj).encode(encoding);
    else:
        return json.dumps(obj, indent=indent).encode(encoding);


def parseToJson(jsonStr):
    return json.loads(jsonStr)


if __name__=="__main__":
    _dict = {}
    _dict["a"] = 1L
    _dict["b"] = None
    _dict["c"] = "abc\r\n"
    
    jsonStr = toJSONString(_dict)
    _dict2 = parseToJson(jsonStr)
    
    jsonStr2 = toJSONString(_dict2)
    
    print jsonStr
    print _dict2
    print jsonStr2
    




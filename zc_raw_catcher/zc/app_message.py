#!/usr/bin/python
import io
import serialize

class AppMessage(object):
    """
    attribute:
    id
    type
    sender
    receiver
    session
    sequence
    transaction
    timestamp
    success
    
    """
    REQUEST = 0
    RESPONSE = 1
    EVENT = 2
    ACK = 3
    param_type_int = 0
    param_type_uint = 1
    param_type_bool = 2
    param_type_string = 3
    param_type_float = 4
    param_type_int_array = 5
    param_type_uint_array = 6
    param_type_float_array = 7
    param_type_string_array = 8
    param_type_uint_array_array = 9
    param_type_string_array_array = 10
    param_type_float_array_array = 11
    
    def __init__(self):
        self.id = 0
        self.type = 0
        self.sender = ""
        self.receiver = ""
        self.session = 0
        self.sequence = 0
        self.transaction = 0        
        self.timestamp = 0
        self.success = False
        ##key = param_type, value = {param key:value}
        self.params = {}

    def toString(self):
        stream = io.BytesIO()
        ##write basic attrib
        ##msg id
        serialize.writeVariant(stream, self.id)
        ##type&success
        ##bin: 6bit type | 1bit success
        if self.success:
            stream.write(chr((self.type<<1)|1))
        else:
            stream.write(chr((self.type<<1)|0))
        ##sender&receiver
        serialize.writeString(stream, self.sender)
        serialize.writeString(stream, self.receiver)

        serialize.writeVariant(stream, self.session)
        serialize.writeVariant(stream, self.sequence)
        serialize.writeVariant(stream, self.transaction)
        serialize.writeVariant(stream, self.timestamp)
        self.writeParams(stream)
        content = stream.getvalue()
        
        stream.close()
        return content

    @staticmethod
    def fromString(content):
        msg = AppMessage()
        stream = io.BytesIO(content)
        ##read basic attrib
        ##msg id
        msg.id = serialize.readVariant(stream)
        ##type&success
        ##bin: 6bit type | 1bit success
        type_value = ord(stream.read(1))
        msg.type = type_value >> 1
        if type_value&0x01:
            msg.success = True
        else:
            msg.success = False
            
        ##sender&receiver
        msg.sender = serialize.readString(stream)
        msg.receiver = serialize.readString(stream)

        msg.session = serialize.readVariant(stream)
        msg.sequence = serialize.readVariant(stream)
        msg.transaction = serialize.readVariant(stream)
        msg.timestamp = serialize.readVariant(stream)
        msg.readParams(stream)
        stream.close()
        return msg
    
    def writeParams(self, stream):
        for value_type in self.params.keys():
            for key in self.params[value_type]:
                value = self.params[value_type][key]
                ## 2bytes: 11 bits key, 5 bits type
                key_value = key << 5|value_type
                stream.write(chr(key_value >> 8))
                stream.write(chr(key_value&0xFF))
                if self.param_type_uint == value_type:
                    ##write uint params
                    if not (isinstance(value, int) or isinstance(value, long)):
                        raise Exception("write param:invalid uint value for key %d, msg %d"%(key, self.id))
                    
                    serialize.writeVariant(stream, value)
                elif self.param_type_bool == value_type:
                    if not isinstance(value, int):
                        raise Exception("write param:invalid bool value for key %d, msg %d"%(key, self.id))
                    ##write bool params
                    if value:
                        serialize.writeVariant(stream, 1)
                    else:
                        serialize.writeVariant(stream, 0)
                elif self.param_type_int == value_type:
                    if not (isinstance(value, int) or isinstance(value, long)):
                        raise Exception("write param:invalid int value for key %d, msg %d"%(key, self.id))
                    ##write int params
                    serialize.writeVariant(stream, serialize.zigzagEncode(value))
                elif self.param_type_string == value_type:
                    if not isinstance(value, str):
                        raise Exception("write param:invalid string value for key %d, msg %d"%(key, self.id))
                    ##write string params
                    serialize.writeString(stream, value)
                elif self.param_type_float == value_type:
                    if not (isinstance(value, float) or isinstance(value, int) or isinstance(value, long)):
                        raise Exception("write param:invalid float value for key %d, msg %d"%(key, self.id))
                    ##write float
                    serialize.writeFloat(stream, value)
                elif self.param_type_uint_array == value_type:
                    ##write uint array
                    if not isinstance(value, list):
                        raise Exception("write param:invalid uint array for key %d, msg %d"%(key, self.id))
                    ##write count
                    count = len(value)
                    serialize.writeVariant(stream, count)
                    for uint_value in value:
                        if not (isinstance(uint_value, int) or isinstance(uint_value, long)):
                            raise Exception("write param:invalid uint item for key %d, msg %d"%(key, self.id))                        
                        serialize.writeVariant(stream, uint_value)
                        
                elif self.param_type_string_array == value_type:
                    ##write string array
                    if not isinstance(value, list):
                        raise Exception("write param:invalid string array for key %d, msg %d"%(key, self.id))
                    ##write count
                    count = len(value)
                    serialize.writeVariant(stream, count)
                    for string_value in value:
                        if not isinstance(string_value, str):
                            raise Exception("write param:invalid string item for key %d, msg %d, params:%s"%(key, self.id, self.params))                        

                        serialize.writeString(stream, string_value)
                elif self.param_type_float_array == value_type:
                    ##write float array
                    if not isinstance(value, list):
                        raise Exception("write param:invalid float array for key %d, msg %d"%(key, self.id))
                    ##write count
                    count = len(value)
                    serialize.writeVariant(stream, count)
                    for float_value in value:
                        if not (isinstance(float_value, float) or isinstance(float_value, int) or isinstance(float_value, long)):
                            raise Exception("write param:invalid float item for key %d, msg %d"%(key, self.id))                        
                        serialize.writeFloat(stream, float_value)

                elif self.param_type_uint_array_array == value_type:
                    ##write uint array array
                    if not isinstance(value, list):
                        raise Exception("write param:invalid uint array array for key %d, msg %d"%(key, self.id))
                    ##write count
                    array_count = len(value)
                    serialize.writeVariant(stream, array_count)
                    for sub_array in value:
                        if not isinstance(sub_array, list):
                            raise Exception("write param:invalid uint sub array for key %d, msg %d"%(key, self.id))
                        sub_count = len(sub_array)
                        serialize.writeVariant(stream, sub_count)
                        for uint_value in sub_array:
                            if not (isinstance(uint_value, int) or isinstance(uint_value, long)):
                                raise Exception("write param:invalid uint sub item for key %d, msg %d"%(key, self.id))
                            serialize.writeVariant(stream, uint_value)
                elif self.param_type_string_array_array == value_type:
                    ##write string array array
                    if not isinstance(value, list):
                        raise Exception("write param:invalid string array array for key %d, msg %d"%(key, self.id))
                    ##write count
                    array_count = len(value)
                    serialize.writeVariant(stream, array_count)
                    for sub_array in value:
                        if not isinstance(sub_array, list):
                            raise Exception("write param:invalid string sub array for key %d, msg %d"%(key, self.id))
                        sub_count = len(sub_array)
                        serialize.writeVariant(stream, sub_count)
                        for string_value in sub_array:
                            if not isinstance(string_value, str):
                                raise Exception("write param:invalid string sub item for key %d, msg %d, params:%s"%(
                                    key, self.id, self.params))                        
                            serialize.writeString(stream, string_value)                    
                elif self.param_type_float_array_array == value_type:
                    ##write float array array
                    if not isinstance(value, list):
                        raise Exception("write param:invalid float array array for key %d, msg %d"%(key, self.id))
                    ##write count
                    array_count = len(value)
                    serialize.writeVariant(stream, array_count)
                    for sub_array in value:
                        if not isinstance(sub_array, list):
                            raise Exception("write param:invalid float sub array for key %d, msg %d"%(key, self.id))
                        sub_count = len(sub_array)
                        serialize.writeVariant(stream, sub_count)
                        for float_value in sub_array:
                            if not (isinstance(float_value, float) or isinstance(float_value, int) or isinstance(float_value, long)):
                                raise Exception("write param:invalid float sub item for key %d, msg %d"%(key, self.id))                        
                            serialize.writeFloat(stream, float_value)                    
    
    def readParams(self, stream):
        ## 2bytes: 11 bits key, 5 bits type
        data = stream.read(2)
        while 0 != len(data):
            key_value = ord(data[0])<<8|ord(data[1])
            value_type = key_value&0x1F
            key = key_value >> 5
            if self.param_type_uint == value_type:
                ##uint
                value = serialize.readVariant(stream)
                self.setUInt(key, value)
            elif self.param_type_bool == value_type:
                ##bool
                value = serialize.readVariant(stream)
                self.setBool(key, (1 == value))
            elif self.param_type_int == value_type:
                ##int
                value = serialize.readVariant(stream)
                self.setInt(key, serialize.zigzagDecode(value))
            elif self.param_type_string == value_type:
                ##string
                value = serialize.readString(stream)
                self.setString(key, value)
            elif self.param_type_float == value_type:
                ##float
                self.setFloat(key, serialize.readFloat(stream))
            elif self.param_type_uint_array == value_type:
                ##uint array
                count = serialize.readVariant(stream)
                array = []
                for i in range(count):
                    array.append(serialize.readVariant(stream))
                self.setUIntArray(key, array)
            elif self.param_type_string_array == value_type:
                ##string array
                count = serialize.readVariant(stream)
                array = []
                for i in range(count):
                    array.append(serialize.readString(stream))
                self.setStringArray(key, array)
            elif self.param_type_float_array == value_type:
                ##float array
                count = serialize.readVariant(stream)
                array = []
                for i in range(count):
                    array.append(serialize.readFloat(stream))
                self.setFloatArray(key, array)
            elif self.param_type_uint_array_array == value_type:
                ##uint array array
                count = serialize.readVariant(stream)
                array = []
                for i in range(count):
                    sub_count = serialize.readVariant(stream)
                    sub_array = []
                    for j in range(sub_count):                        
                        sub_array.append(serialize.readVariant(stream))
                    array.append(sub_array)
                self.setUIntArrayArray(key, array)

            elif self.param_type_string_array_array == value_type:
                ##string array array
                count = serialize.readVariant(stream)
                array = []
                for i in range(count):
                    sub_count = serialize.readVariant(stream)
                    sub_array = []
                    for j in range(sub_count):                        
                        sub_array.append(serialize.readString(stream))
                    array.append(sub_array)                
                self.setStringArrayArray(key, array)
            elif self.param_type_float_array_array == value_type:
                ##float array array
                count = serialize.readVariant(stream)
                array = []
                for i in range(count):
                    sub_count = serialize.readVariant(stream)
                    sub_array = []
                    for j in range(sub_count):                        
                        sub_array.append(serialize.readFloat(stream))
                    array.append(sub_array)
                self.setFloatArrayArray(key, array)

            ##next key
            data = stream.read(2)

    
    def setValue(self, value_type, key, value):
        if value is None:
            return False
        if not self.params.has_key(value_type):
            self.params[value_type] = {key:value}
        else:
            self.params[value_type][key] = value
        return True
            
    def getValue(self, value_type, key):
        if not self.params.has_key(value_type):
            return None
        elif not self.params[value_type].has_key(key):
            return None
        else:
            return self.params[value_type][key]        

    def setUInt(self, key, value):
        return self.setValue(self.param_type_uint, key, value)

    def getUInt(self, key):
        value = self.getValue(self.param_type_uint, key)
        if value is None:
            return 0
        else:
            return value

    def setString(self, key, value):
        return self.setValue(self.param_type_string, key, value)

    def getString(self, key):
        value = self.getValue(self.param_type_string, key)
        if value is None:
            return ""
        else:
            return value

    def setBool(self, key, value):
        return self.setValue(self.param_type_bool, key, value)

    def getBool(self, key):
        value = self.getValue(self.param_type_bool, key)
        if value is None:
            return False
        else:
            return value

    def setInt(self, key, value):
        return self.setValue(self.param_type_int, key, value)

    def getInt(self, key):
        value = self.getValue(self.param_type_int, key)
        if value is None:
            return 0
        else:
            return value

    def setFloat(self, key, value):
        return self.setValue(self.param_type_float, key, value)

    def getFloat(self, key):
        value = self.getValue(self.param_type_float, key)
        if value is None:
            return 0.0
        else:
            return value

    def setUIntArray(self, key, value):
        if not self.validateArray(value):
            return False
        return self.setValue(self.param_type_uint_array, key, value)

    def getUIntArray(self, key):
        value = self.getValue(self.param_type_uint_array, key)
        if value is None:
            return None
        else:
            return value

    def setStringArray(self, key, value):
        if not self.validateArray(value):
            return False
        return self.setValue(self.param_type_string_array, key, value)

    def getStringArray(self, key):
        value = self.getValue(self.param_type_string_array, key)
        if value is None:
            return None
        else:
            return value

    def setFloatArray(self, key, value):
        if not self.validateArray(value):
            return False
        return self.setValue(self.param_type_float_array, key, value)

    def getFloatArray(self, key):
        value = self.getValue(self.param_type_float_array, key)
        if value is None:
            return None
        else:
            return value

    def setUIntArrayArray(self, key, value):
        if not self.validateArrayArray(value):
            return False
        return self.setValue(self.param_type_uint_array_array, key, value)

    def getUIntArrayArray(self, key):
        value = self.getValue(self.param_type_uint_array_array, key)
        if value is None:
            return None
        else:
            return value

    def setStringArrayArray(self, key, value):
        if not self.validateArrayArray(value):
            return False
        return self.setValue(self.param_type_string_array_array, key, value)

    def getStringArrayArray(self, key):
        value = self.getValue(self.param_type_string_array_array, key)
        if value is None:
            return None
        else:
            return value
        
    def setFloatArrayArray(self, key, value):
        if not self.validateArrayArray(value):
            return False
        return self.setValue(self.param_type_float_array_array, key, value)

    def getFloatArrayArray(self, key):
        value = self.getValue(self.param_type_float_array_array, key)
        if value is None:
            return None
        else:
            return value
        
    @staticmethod
    def validateArray(value):
        for item in value:
            if item is None:
                return False
        return True            

    @staticmethod
    def validateArrayArray(value):
        for sub_array in value:
            if sub_array is None:
                return False
            for item in sub_array:
                if item is None:
                    return False
        return True            

    


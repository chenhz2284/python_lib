#!/usr/bin/python
import io
import struct

def writeVariant(stream, value):
    if 0 == value:
        stream.write(chr(0))
        return True
    ##only lower 64bit processed
    left = value&0xFFFFFFFFFFFFFFFF
##    print "variant [%016X]"%left
    while 0 != left:
        ##7 bit
        stored = left&0x7F
        left = left >> 7
        if 0 == left:
            msb = 0
        else:
            ##more bytes available
            msb = 1
        write_value = (msb << 7)|stored
        stream.write(chr(write_value))
    return True    

def writeString(stream, value):
    length = len(value)
    ##write variant length
    writeVariant(stream, length)
    if 0 != length:
        ##write raw content
        stream.write(value)
    return True

def writeFloat(stream, value):
    bits = struct.unpack("BBBB", struct.pack("f", value))
    for bit in bits:
        stream.write(chr(bit))
    return True

def readVariant(stream):
    value = 0
    count = 0
    msb = 1
    while 1 == msb:
        ##need more bytes
        data = stream.read(1)
        if 0 == len(data):
            ##EOF
            return None
        current = ord(data)
        msb = current >> 7
        int_value = current&0x7F
        value |= int_value << (7*count)
        
        count += 1
    return value&0xFFFFFFFFFFFFFFFF

def readString(stream):
    length = readVariant(stream)
    if length is None:
        return None
    if 0 == length:
        return ""
    content = stream.read(length)
    if 0 == len(content):
        return None
    return content

def readFloat(stream):
    bits = stream.read(4)
    if 4 != len(bits):
        return None
    return struct.unpack("f", bits)[0]

def zigzagEncode(n):
    return (n << 1)^(n >>31)

def zigzagDecode(n):
    return (n >> 1) ^ (-(n & 1))

if __name__ == "__main__":
    import datetime
    import binascii
    stream = io.BytesIO()
    writeVariant(stream, 10)
    writeVariant(stream, 78)
    writeVariant(stream, 1)
    writeVariant(stream, 1)
    writeVariant(stream, 1)
    writeVariant(stream, 0)
##    writeVariant(stream, (-1032598831)&0xFFFFFFFF)
##    writeFloat(stream, -342.23)    
##    writeString(stream, "hello akumas")
##    writeString(stream, "")
    content = stream.getvalue()
    stream.close()
    print binascii.b2a_hex(content)

    content = struct.pack(">BBBBBBB", 10, 33, 1, 1, 1, 1, 0)
    print binascii.b2a_hex(content)
    new_stream = io.BytesIO(content)
    print "read variant:", readVariant(new_stream)
    print "read variant:", readVariant(new_stream)
    print "read variant:", readVariant(new_stream)
    print "read variant:", readVariant(new_stream)
    print "read variant:", readVariant(new_stream)
    print "read variant:", readVariant(new_stream)
    print "read variant:", readVariant(new_stream)
    new_stream.close()



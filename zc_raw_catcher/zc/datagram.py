#!/usr/bin/python
import struct
import zlib

class Datagram(object):
    """
    datagram format:
    header(1 byte):
      mark(4bit):1001
      version(2bit):1~4
      type(2bit):0-data, 1-ack
    seq:2 byte
    for data
    length:2 byte
    crc:4 byte - crc32
    data:n byte    
    """
    header_mask = 9
    version = 1
    data_type = 0
##    header = (Datagram.header_mask << 4)|(Datagram.version << 2)|Datagram.data_type
    ##bin:1001 01 00
    header = 148
    def __init__(self, content, seq):
        self.seq = seq
        self.data = content

    def toString(self):
        crc = zlib.crc32(self.data)&0xFFFFFFFF
        length = len(self.data)
        return struct.pack(">BHHI%ds"%length, self.header,
                           self.seq, length,
                           crc, self.data)

class DatagramACK(object):
    """
    datagram format:
    header(1 byte):
      mark(4bit):1001
      version(2bit):1~4
      type(2bit):0-data, 1-ack
    seq:2 byte 
    """
    header_mask = 9
    version = 1
    data_type = 1
##    header = (DatagramACK.header_mask << 4)|(DatagramACK.version << 2)|DatagramACK.data_type
    ##bin:1001 01 01
    header = 149
    def __init__(self, seq):
        self.seq = seq

    def toString(self):
        ##pack ack
        return struct.pack(">BH", self.header, self.seq)    

##    @staticmethod
##    def unpackFromString(string):
##        result = []
##        length = len(string)
##        begin = 0
##        while (length - begin) >= 3:
##            header, seq = struct.unpack(">BH", string[begin:(begin+3)])
##            if Datagram.header_mask != ((header&0xF0)>>4):
##                break
##            version = (header&0x0C)>>2
##            data_type = header&0x03
##            if 1 == data_type:
##                ##ack
##                data = Datagram()
##                data.setACK(seq)
##                result.append(data)                
##                begin += 3
##            else:
##                ##data
##                if (length - begin) < 9:
##                    ##incomplete
##                    break
##                data_length, crc = struct.unpack(">HI", string[(begin+3):(begin+9)])
##                content_offset = begin+9
##                data_content = string[content_offset:(content_offset + data_length)]
##                ##crc check
##                computed_crc = zlib.crc32(data_content)& 0xFFFFFFFF
##                if computed_crc != crc:
##                    ##data damaged
##                    break
##                ##new data
##                data = Datagram()
##                data.setData(data_content)
##                data.setSequence(seq)
##                result.append(data)
##                begin = content_offset + data_length
##                
##        ##end while
##        return result

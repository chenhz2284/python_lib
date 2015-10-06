#!/usr/bin/python
import io
import serialize

class TransportCommand(object):
    type_keep_alive = 0
    type_connect_request = 1
    type_connect_response = 2
    type_disconnect_request = 3
    type_disconnect_response = 4
    type_message_data = 5
    type_connect_acknowledge = 6
    session = 0    
        
class ConnectRequest(TransportCommand):
    def __init__(self):
        self.type = TransportCommand.type_connect_request
        self.session = 0
        self.client_key = ""
        self.digest = ""
        self.sender = 0
        self.name = ""
        self.ip = ""
        self.port = 0
        
    def toString(self):
        stream = io.BytesIO()
        serialize.writeVariant(stream, self.type)
        serialize.writeVariant(stream, self.session)
        serialize.writeString(stream, self.client_key)
        serialize.writeString(stream, self.digest)
        serialize.writeVariant(stream, self.sender)
        serialize.writeString(stream, self.name)
        serialize.writeString(stream, self.ip)
        serialize.writeVariant(stream, self.port)
        content = stream.getvalue()
        stream.close()
        return content
    
class ConnectResponse(TransportCommand):
    def __init__(self):
        self.type = TransportCommand.type_connect_response
        self.session = 0
        self.success = False
        self.need_digest = False
        self.auth_method = 0
        self.client_key = ""
        self.server_key = ""
        self.sender = 0
        self.name = ""
        self.ip = ""
        self.port = 0
        
    def toString(self):
        stream = io.BytesIO()
        serialize.writeVariant(stream, self.type)
        serialize.writeVariant(stream, self.session)
        if self.success:
            success = 1
        else:
            success = 0
        if self.need_digest:
            bool_value = success << 1|1
        else:
            bool_value = success << 1|0
        serialize.writeVariant(stream, bool_value)
        serialize.writeString(stream, self.client_key)
        serialize.writeString(stream, self.server_key)
        serialize.writeVariant(stream, self.sender)
        serialize.writeString(stream, self.name)
        serialize.writeString(stream, self.ip)
        serialize.writeVariant(stream, self.port)
        content = stream.getvalue()        
        stream.close()
        return content

class ConnectAcknowledge(TransportCommand):
    def __init__(self):
        self.type = TransportCommand.type_connect_acknowledge
        self.session = 0
        self.name = ""
        
    def toString(self):
        stream = io.BytesIO()
        serialize.writeVariant(stream, self.type)
        serialize.writeVariant(stream, self.session)
        serialize.writeString(stream, self.name)
        content = stream.getvalue()        
        stream.close()
        return content
    
class DisconnectRequest(TransportCommand):
    def __init__(self):
        self.type = TransportCommand.type_disconnect_request
        self.session = 0
        self.name = ""
        
    def toString(self):
        stream = io.BytesIO()
        serialize.writeVariant(stream, self.type)
        serialize.writeVariant(stream, self.session)
        serialize.writeString(stream, self.name)
        content = stream.getvalue()        
        stream.close()
        return content

class DisconnectResponse(TransportCommand):
    def __init__(self):
        self.type = TransportCommand.type_disconnect_response
        self.session = 0
        self.success = False
        
    def toString(self):
        stream = io.BytesIO()
        serialize.writeVariant(stream, self.type)
        serialize.writeVariant(stream, self.session)
        if self.success:
            serialize.writeVariant(stream, 1)
        else:
            serialize.writeVariant(stream, 0)
        content = stream.getvalue()        
        stream.close()
        return content

class KeepAlive(TransportCommand):
    def __init__(self):
        self.type = TransportCommand.type_keep_alive
        self.session = 0
        self.name = ""
        
    def toString(self):
        stream = io.BytesIO()
        serialize.writeVariant(stream, self.type)
        serialize.writeVariant(stream, self.session)
        serialize.writeString(stream, self.name)
        content = stream.getvalue()
        stream.close()
        return content    

class MessageData(TransportCommand):
    def __init__(self):
        self.type = TransportCommand.type_message_data
        self.session = 0
        self.serial = 0
        self.index = 0
        self.total = 0
        self.data = ""
        
    def toString(self):
        stream = io.BytesIO()
        serialize.writeVariant(stream, self.type)
        serialize.writeVariant(stream, self.session)
        serialize.writeVariant(stream, self.serial)
        serialize.writeVariant(stream, self.index)
        serialize.writeVariant(stream, self.total)
        serialize.writeString(stream, self.data)
        content = stream.getvalue()        
        stream.close()
        return content    

def unpackageFromRawdata(data):
    result = []
    stream = io.BytesIO(data)
    command_type = serialize.readVariant(stream)
    while command_type is not None:
        session = serialize.readVariant(stream)
        if TransportCommand.type_connect_request == command_type:
            ##connect request
            command = ConnectRequest()
            command.session = session
            command.client_key = serialize.readString(stream)
            command.digest = serialize.readString(stream)
            command.sender = serialize.readVariant(stream)
            command.name = serialize.readString(stream)
            command.ip = serialize.readString(stream)
            command.port = serialize.readVariant(stream)
            result.append(command)
            
        elif TransportCommand.type_connect_response == command_type:
            ##connect response
            command = ConnectResponse()
            command.session = session
            bool_value = serialize.readVariant(stream)
            if 1 == (bool_value >> 1):
                command.success = True
            else:
                command.success = False
                
            if 1 == (bool_value&0x01):
                command.need_digest = True
            else:
                command.need_digest = False
            command.client_key = serialize.readString(stream)
            command.server_key = serialize.readString(stream)
            command.sender = serialize.readVariant(stream)
            command.name = serialize.readString(stream)
            command.ip = serialize.readString(stream)
            command.port = serialize.readVariant(stream)
            result.append(command)
            
        elif TransportCommand.type_connect_acknowledge == command_type:
            command = ConnectAcknowledge()
            command.session = session
            command.name = serialize.readString(stream)
            result.append(command)

        elif TransportCommand.type_disconnect_request == command_type:
            command = DisconnectRequest()
            command.session = session
            command.name = serialize.readString(stream)
            result.append(command)

        elif TransportCommand.type_disconnect_response == command_type:
            command = DisconnectResponse()
            command.session = session
            if 1 == serialize.readVariant(stream):
                command.success = True
            else:
                command.success = False
                
            result.append(command)
            
        elif TransportCommand.type_keep_alive == command_type:
            command = KeepAlive()
            command.session = session
            command.name = serialize.readString(stream)
            result.append(command)
            
        elif TransportCommand.type_message_data == command_type:
            command = MessageData()
            command.session = session
            command.serial = serialize.readVariant(stream)
            command.index = serialize.readVariant(stream)
            command.total = serialize.readVariant(stream)
            command.data = serialize.readString(stream)
            result.append(command)
            
            
        ##next command
        command_type = serialize.readVariant(stream)
##    print "unpackage %d commands from %d bytes"%(
##        len(result), len(data))
    return result

if __name__ == "__main__":
    import datetime
    import binascii
    data = binascii.a2b_hex("01002833336263343235363662313466356233303532616238653764663132623965643638336564663135000106636c69656e740e3139322e3136382e36362e313032e02b")
    command_list = unpackageFromRawdata(data)
    print len(command_list)
    connect_request = command_list[0]
    print connect_request.session, connect_request.client_key, connect_request.digest

# encoding: utf8

import sys
import socket
import struct
import datetime
import zlib
from zc.datagram import Datagram, DatagramACK
from zc import transport_command
from zc.transport_command import TransportCommand
from zc.app_message import AppMessage


def received_packet_to_command(packet):
    
    command_list  = []
    length = len(packet)
    begin = 0
    
    header, seq = struct.unpack(">BH", packet[begin:(begin+3)])
    if Datagram.header_mask != ( (header & 0xF0)>>4 ):
        print("datagram header mask fail.")
        return command_list;
    
    while (length - begin) >= 3:
        
        header, seq = struct.unpack(">BH", packet[begin:(begin+3)])
        if Datagram.header_mask != ((header & 0xF0)>>4):
            break
        
        version = (header & 0x0C)>>2
        data_type = header & 0x03
        if 1 == data_type:
            ##ack
            begin += 3
            command_list.append(DatagramACK(seq))
            continue
        else:
            ##data
            if (length - begin) < 9:
                ##incomplete
                print("incomplete, (length - begin) < 9")
                break
            
            data_length, crc = struct.unpack(">HI", packet[(begin+3):(begin+9)])
            content_offset   = begin+9
            data_content     = packet[content_offset:(content_offset + data_length)]
            ##crc check
            computed_crc = zlib.crc32(data_content) & 0xFFFFFFFF
            if computed_crc != crc:
                ##data damaged
                print("check crc fail.")
                break
            ##unserialize
            command_list.extend(transport_command.unpackageFromRawdata(data_content))
            begin = content_offset + data_length
    
    return command_list
    
    
def handleCommand(command_list):
    
    for command in command_list:
        try:
            if isinstance(command, DatagramACK):
                print("    ack, seq=%s" % command.seq)
                
            else:
                
                if command.type == TransportCommand.type_keep_alive:
                    print("    TransportCommand.type_keep_alive")
                    print("    session: %s" % command.session)
                    print("    name: %s" % command.name)
                    
                elif command.type == TransportCommand.type_connect_request:
                    print("    TransportCommand.type_connect_request")
                    print("    session: %s" % command.session)
                    print("    name: %s" % command.name)
                    print("    client_key: %s" % command.client_key)
                    print("    digest: %s" % command.digest)
                    print("    sender: %s" % command.sender)
                    print("    ip: %s" % command.ip)
                    print("    port: %s" % command.port)
                    
                elif command.type == TransportCommand.type_connect_response:
                    print("    TransportCommand.type_connect_response")
                    print("    session: %s" % command.session)
                    print("    name: %s" % command.name)
                    print("    success: %s" % command.success)
                    print("    need_digest: %s" % command.need_digest)
                    print("    auth_method: %s" % command.auth_method)
                    print("    client_key: %s" % command.client_key)
                    print("    server_key: %s" % command.server_key)
                    print("    sender: %s" % command.sender)
                    print("    ip: %s" % command.ip)
                    print("    port: %s" % command.port)
                    
                elif command.type == TransportCommand.type_connect_acknowledge:
                    print("    TransportCommand.type_connect_acknowledge")
                    print("    session: %s" % command.session)
                    print("    name: %s" % command.name)
                    
                elif command.type == TransportCommand.type_disconnect_request:
                    print("    TransportCommand.type_disconnect_request")
                    print("    session: %s" % command.session)
                    print("    name: %s" % command.name)
                    
                elif command.type == TransportCommand.type_disconnect_response:
                    print("    TransportCommand.type_disconnect_response")
                    print("    session: %s" % command.session)
                    print("    success: %s" % command.success)
                    
                elif command.type == TransportCommand.type_message_data:
                    print("    TransportCommand.type_message_data")
                    print("    session: %s" % command.session)
                    print("    serial: %s" % command.serial)
                    print("    index: %s" % command.index)
                    print("    total: %s" % command.total)
                    print("    message data length: %s" % len(command.data))
                    if 1 == command.total:
                        message = AppMessage.fromString(command.data)
                        print("        messsage.id: %s" % message.id)
                        print("        messsage.type: %s" % message.type)
                        print("        messsage.sender: %s" % message.sender)
                        print("        messsage.receiver: %s" % message.receiver)
                        print("        messsage.session: %s" % message.session)
                        print("        messsage.sequence: %s" % message.sequence)
                        print("        messsage.transaction: %s" % message.transaction)
                        print("        messsage.timestamp: %s" % message.timestamp)
                        print("        messsage.success: %s" % message.success)
                        print("        messsage.params: %s" % message.params)
                    else:
                        print("        message total > 1: not support yet")
                        
                        

        except Exception,ex:
            print("    <Transporter>handle received datagram exception:%s" % (ex))
            continue  
    

def __start():

    #create an INET, STREAMing socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    except socket.error , msg:
        print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
    
    # receive a packet
    while True:
        packet_tuple = s.recvfrom(65565)
        
        #packet string from tuple
        packet    = packet_tuple[0]
        from_addr = packet_tuple[1]
        
        #take first 20 characters for the ip header
        ip_header = packet[0:20]
        
        #now unpack them :)
        iph = struct.unpack('!BBHHHBBH4s4s' , ip_header)
        
        version_ihl = iph[0]
        version = version_ihl >> 4
        ihl = version_ihl & 0xF
        
        ip_header_length = ihl * 4
        
        total_length = iph[2]
        ttl = iph[5]
        protocol = iph[6]
        src_addr = socket.inet_ntoa(iph[8]);
        dst_addr = socket.inet_ntoa(iph[9]);
        
        udp_header_length = 8;
        udp_header = packet[ip_header_length:ip_header_length + udp_header_length]
         
        #now unpack them :)
        udp_header_bytes = struct.unpack('!HHHH' , udp_header)
         
        source_port = udp_header_bytes[0]
        dest_port   = udp_header_bytes[1]
        udp_length  = udp_header_bytes[2]
        checksum    = udp_header_bytes[3]
        
        udp_data_length = udp_length - udp_header_length;
        h_size = ip_header_length + udp_header_length
        data = packet[h_size:]
        
        if not dst_addr.startswith("224."):
        
            print("receive udp packet: %s:%s -> %s:%s, at %s" % (src_addr, source_port, dst_addr, dest_port, datetime.datetime.now()))
#             print("datagram length: %s" % len(packet))
#             print('Version : %s' % version)
#             print('IP Header Length : 4byte * %s = %s' % (ihl, ihl*4))
#             print('TTL : %s' % (ttl))
#             print('total length: %s' % (total_length))
#             print('Protocol : %s' % (protocol))
#             print('Source Ip: %s' % (src_addr))
#             print("Dest Ip: %s" % (dst_addr))
#             print("source_port: %s" % (source_port))
#             print("dest_port: %s" % (dest_port))
#             print("udp_data_length: %s" % (udp_data_length))
#             print("checksum: %s" % (checksum))
#             
#             data_size = len(packet) - h_size
#             print 'Data length: %s' % data_size
             
            #get data from the packet
            command_list = received_packet_to_command(data)
            print("transport to %d command(s)" % len(command_list))
            handleCommand(command_list)
            print("")
            
        else:
            
            print("receive multicast packet: %s:%s -> %s:%s, at %s" % (src_addr, source_port, dst_addr, dest_port, datetime.datetime.now()))
            print("    data: %s" % data)
            print("")


if __name__=="__main__":
    __start();
    
    
    
    
    
    
    
    
    
    
    
    
    
    
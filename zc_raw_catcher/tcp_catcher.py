# encoding: utf8

import socket
import struct
import binascii


#create an INET, STREAMing socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
except socket.error , msg:
    print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

# receive a packet
while True:
    packet = s.recvfrom(65565)
    
    #packet string from tuple
    packet = packet[0]
    
    #take first 20 characters for the ip header
    ip_header = packet[0:20]
    
    #now unpack them :)
    iph = struct.unpack('!BBHHHBBH4s4s' , ip_header)
    
    version_ihl = iph[0]
    version = version_ihl >> 4
    ihl = version_ihl & 0xF
    
    iph_length = ihl * 4
    
    total_length = iph[2]
    ttl = iph[5]
    protocol = iph[6]
    s_addr = socket.inet_ntoa(iph[8]);
    d_addr = socket.inet_ntoa(iph[9]);
    
    tcp_header = packet[iph_length:iph_length+20]
    
    #now unpack them :)
    tcph = struct.unpack('!HHLLBBHHH' , tcp_header)
    
    source_port = tcph[0]
    dest_port = tcph[1]
    sequence = tcph[2]
    acknowledgement = tcph[3]
    doff_reserved = tcph[4]
    tcph_length = doff_reserved >> 4
    
    print("datagram length: %s" % len(packet))
    print('Version : ' + str(version))
    print('IP Header Length : 4byte * %s' % ihl)
    print('TTL : ' + str(ttl))
    print('total length: %s' % total_length)
    print('Protocol : ' + str(protocol))
    print('Source : %s:%s' % (s_addr, source_port))
    print("Dest : %s:%s" % (d_addr, dest_port))
    print('TCP header length : ' + str(tcph_length))
    print('Sequence Number : ' + str(sequence))
    print('Acknowledgement : ' + str(acknowledgement))
    
    
    
    h_size = iph_length + tcph_length * 4
    data_size = len(packet) - h_size
    
    #get data from the packet
    data = packet[h_size:]
    
    print 'Data length: %s' % len(data)
    print

    
    
    
    
    
    
    
    
    
    
    
    
    
    
import socket
import uuid
import threading
import time
import datetime
from threading import RLock
from ConfigParser import ConfigParser
import signal
import os
import struct


print("version: 1.2")


###############################

def _onSignal(sigalnum, frame):
    print("signal: %s" % sigalnum)
    os._exit(0)

signal.signal(signal.SIGINT, _onSignal);

##############################

_parser = ConfigParser()  
_parser.read("network_analyser.conf")
_listen_ip             = _parser.get("DEFAULT",    "listen_ip").strip()
_listen_port           = _parser.getint("DEFAULT", "listen_port")
_target_ip             = _parser.get("DEFAULT",    "target_ip").strip()
_target_port           = _parser.getint("DEFAULT", "target_port")
_multicast_listen_ip   = _parser.get("DEFAULT",    "multicast_listen_ip").strip()
_multicast_listen_port = _parser.getint("DEFAULT", "multicast_listen_port")
_packet_test_count     = _parser.getint("DEFAULT", "packet_test_count")

print("listen ip: %s" % _listen_ip)
print("listen port: %s" % _listen_port)
print("target ip: %s" % _target_ip)
print("multicast listen ip: %s" % _multicast_listen_ip)
print("multicast listen port: %s" % _multicast_listen_port)
print("packet test count: %s" % _packet_test_count)

################################


def timedeltaToSecond(dt):
    return dt.days * 24 * 60 * 60 + dt.seconds + dt.microseconds/1000000.0;


def formatDatetime(dt, fmt="%Y-%m-%d %H:%M:%S.%f"):
    return dt.strftime(fmt)


def parseToDatetime(dtStr, fmt="%Y-%m-%d %H:%M:%S.%f"):
    return datetime.datetime.strptime(dtStr, fmt)


###############################


class PacketType(object):
    comman = 1              # "1|packet_group_uuid|packet_count|packet_num"
    multicast = 2           # "2|listen_ip|listen_port|packet_group_uuid|packet_count|packet_num"
    delay_request = 3       # "3|packet_group_uuid|send_time(format as yyyy-MM-dd HH:mm:ss.SSS)"
    delay_response = 4      # "4|packet_group_uuid|send_time(format as yyyy-MM-dd HH:mm:ss.SSS)|recv_time(format as yyyy-MM-dd HH:mm:ss.SSS)"


class PacketStatItem(object):
    def __init__(self):
        self._uuid = "";
        self._firstTime = datetime.datetime.now();
        self._lastTime = datetime.datetime.now();
        self._fromAddr = ""
        self._packet_test_count = 0;
        self._packetSet = set();
        
        
class TrashBagItem(object):
    def __init__(self, p_uuid):
        self._uuid = p_uuid;
        self._time = datetime.datetime.now();


class NetworkAnalyser(object):
    
    
    def __init__(self):
        #
        self._listen_addr = (_listen_ip, _listen_port)  
        self._listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self._listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
        self._listen_sock.bind(self._listen_addr)
        
        self._target_addr = (_target_ip, _target_port)  
        
        #
        self._multicast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        
        self._multicast_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        self._multicast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._multicast_sock.bind((_multicast_listen_ip, _multicast_listen_port))
        
        self._multicast_sock.setsockopt(socket.IPPROTO_IP, 
                                        socket.IP_ADD_MEMBERSHIP, 
                                        struct.pack("=4sl", socket.inet_aton(_multicast_listen_ip), socket.INADDR_ANY))
        
        self._multicast_addr = (_multicast_listen_ip, _multicast_listen_port)

        #
        self._sendCommonPacketThread = threading.Thread(target=self._sendCommonPacketRunnable)
        self._recvCommonPacketThread = threading.Thread(target=self._recvCommonPacketRunnable)
        self._commonStatisticThread     = threading.Thread(target=self._commonStatisticRunnable)
        
        self._sendMulticastPacketThread = threading.Thread(target=self._sendMulticastPacketRunnable);
        self._recvMulticastPacketThread = threading.Thread(target=self._recvMulticastPacketRunnable);
        self._multicastStatisticThread  = threading.Thread(target=self._multicastStatisticRunnable)
        
        self._sendDelayPacketThread = threading.Thread(target=self._sendDelayPacketRunnable)
        
        self._trashBagCleanThread = threading.Thread(target=self._trashBagCleanRunnable);
        
        #
        self._recv_statistics_cache_mtx = RLock()
        self._recv_statistics_cache = {}                    # key: uuid, value: PacketStatItem
        
        self._recv_multicast_statistics_cache_mtx = RLock()
        self._recv_multicast_statistics_cache = {}          # key: uuid, value: PacketStatItem
        
        self._trash_bag_mtx = RLock()
        self._trash_bag = {}        # key: uuid, value: TrashBagItem
        
        #
        self._trashBagCleanThread.start()
        
        
    def startSendMulticastPacket(self):
        self._sendMulticastPacketThread.start();
        print("start start multicast thread")
    
    
    def _sendMulticastPacketRunnable(self):
        while True:  
            _uuid = str(uuid.uuid4())
            for i in xrange(_packet_test_count):  
                msg = "%s|%s|%s|%s|%s|%s" % (PacketType.multicast, _listen_ip, _listen_port, _uuid, _packet_test_count, i);
                self._multicast_sock.sendto(msg, self._multicast_addr);
            time.sleep(5);
        
            
    def startRecvMulticastPacket(self):
        self._recvMulticastPacketThread.start();
        print("start receive multicast thread")
        
        
    def _recvMulticastPacketRunnable(self):
        while True:  
            #_packet_data, _addr = self._listen_sock.recvfrom(2048);
            _packet_data, _addr = self._multicast_sock.recvfrom(2048);
              
            if not _packet_data:  
                print "multicast client has exist";
                break;
            
#             print("receive multicast packet: %s" % _packet_data)
            _splitData = _packet_data.split("|");
            try:
                _packet_type = int(_splitData[0])
            except:
                _packet_type = -1
            
            if _packet_type==PacketType.multicast :
                
                _packet_ipv        = _splitData[1]
                _packet_portv      = int(_splitData[2])
                _packet_group_uuid = _splitData[3]
                _packet_count      = int(_splitData[4])
                _packet_number     = _splitData[5]
                
                if _packet_ipv==_listen_ip and _packet_portv==_listen_port:
                    continue;
                
                with self._trash_bag_mtx:
                    if self._trash_bag.has_key(_packet_group_uuid):
                        print("multicast packet received after statistics: %s" % _packet_data)
                        continue;
                
                with self._recv_multicast_statistics_cache_mtx:
                    if not self._recv_multicast_statistics_cache.has_key(_packet_group_uuid):
                        _packet_stat_item = PacketStatItem()
                        _packet_stat_item._fromAddr = _addr
                        _packet_stat_item._packet_test_count = _packet_count
                        _packet_stat_item._packetSet.add(_packet_number)
                        self._recv_multicast_statistics_cache[_packet_group_uuid] = _packet_stat_item
                    else:
                        _packet_stat_item = self._recv_multicast_statistics_cache[_packet_group_uuid];
                        _packet_stat_item._lastTime = datetime.datetime.now()
                        _packet_stat_item._packetSet.add(_packet_number)
            
            else:
                
                print("receive wrong multicast packet: %s" % _packet_data);
    
        
    def startSendCommonPacket(self):
        self._sendCommonPacketThread.start();
        print("start send thread")
        
        
    # send 100 packets every 1 second
    def _sendCommonPacketRunnable(self):
        while True:  
            _uuid = str(uuid.uuid4())
            for i in xrange(_packet_test_count):  
                msg = "%s|%s|%s|%s" % (PacketType.comman, _uuid, _packet_test_count, i);
                self._listen_sock.sendto(msg, self._target_addr);
            time.sleep(5);

    #
    def startRecvCommonPacket(self):
        self._recvCommonPacketThread.start()
        print("start receive thread")
       
        
    #
    def _recvCommonPacketRunnable(self):
        while True:  
            #_packet_data, _addr = self._listen_sock.recvfrom(2048);
            _packet_data, _addr = self._listen_sock.recvfrom(2048);
              
            if not _packet_data:  
                print "client has exist";
                break;
            
            #print("receive packet: %s" % _packet_data)
            _splitData = _packet_data.split("|");
            _packet_type = int(_splitData[0])
            
            if _packet_type==PacketType.comman :
                
                _packet_group_uuid = _splitData[1]
                _packet_count      = int(_splitData[2])
                _packet_number     = int(_splitData[3])
                
                with self._trash_bag_mtx:
                    if self._trash_bag.has_key(_packet_group_uuid):
                        print("packet received after statistics: %s" % _packet_data)
                        continue;
                
                with self._recv_statistics_cache_mtx:
                    if not self._recv_statistics_cache.has_key(_packet_group_uuid):
                        _packet_stat_item = PacketStatItem()
                        _packet_stat_item._fromAddr = _addr
                        _packet_stat_item._packet_test_count = _packet_count
                        _packet_stat_item._packetSet.add(_packet_number)
                        self._recv_statistics_cache[_packet_group_uuid] = _packet_stat_item
                    else:
                        _packet_stat_item = self._recv_statistics_cache[_packet_group_uuid];
                        _packet_stat_item._lastTime = datetime.datetime.now()
                        _packet_stat_item._packetSet.add(_packet_number)
                        
            elif _packet_type==PacketType.delay_request :
                 
                self._handleDelayRequestPacket(_packet_data);
                
            elif _packet_type==PacketType.delay_response :
                
                self._statisticsDelayPacket(_packet_data);
                
    #
    def startCommonStatistics(self):
        self._commonStatisticThread.start()
        print("start common statistics thread")
        

    def _commonStatisticRunnable(self):
        while True:
            
            time.sleep(5);
            print("\r\nstart common analysis")
#             print("_commonStatisticRunnable()1, size of self._trash_bag: %s" % len(self._trash_bag))
            
            _is_recv_statistics_cache_empty = False;
            _items = []
            
            with self._recv_statistics_cache_mtx:
                if len(self._recv_statistics_cache)==0:
                    _is_recv_statistics_cache_empty = True
                else:
                    for _item in self._recv_statistics_cache.items():
                        _now = datetime.datetime.now()
                        _packet_group_uuid = _item[0];
                        _packetStatItem    = _item[1];
                        if timedeltaToSecond(_now - _packetStatItem._firstTime) >= 5:
                            _items.append(_item)
                            del self._recv_statistics_cache[_packet_group_uuid]
                     
            if _is_recv_statistics_cache_empty==True:
                print("recv: 0 packet(s)");
            else:
                if len(_items)==0:
                    print("not packet satisfy statistics condition")
                else:
                    for _item in _items:
                        _now = datetime.datetime.now()
                        _packet_group_uuid = _item[0];
                        _packetStatItem    = _item[1];
                        print("recv: %s%%(%s/%s) packet(s) for uuid '%s' from '%s'" % (len(_packetStatItem._packetSet) / float(_packetStatItem._packet_test_count) * 100,
                                                                                       len(_packetStatItem._packetSet),
                                                                                        _packetStatItem._packet_test_count,
                                                                                       _packet_group_uuid, 
                                                                                       _packetStatItem._fromAddr));
                        with self._trash_bag_mtx:
                            self._trash_bag[_packet_group_uuid] = TrashBagItem(_packet_group_uuid)
                            
#             print("_commonStatisticRunnable()2, size of self._trash_bag: %s" % len(self._trash_bag))
                        
    #
    def startMulticastStatistics(self):
        self._multicastStatisticThread.start()
        print("start multicast statistics thread")

               
    def _multicastStatisticRunnable(self):
        while True:
            
            time.sleep(5);
            print("\r\nstart multicast analysis")
#             print("_multicastStatisticRunnable()1, size of self._trash_bag: %s" % len(self._trash_bag))
            
            _is_recv_multicast_statistics_cache_empty = False
            _items = []
            
            with self._recv_multicast_statistics_cache_mtx: 
                if len(self._recv_multicast_statistics_cache)==0:
                    _is_recv_multicast_statistics_cache_empty = True
                else:
                    for _item in self._recv_multicast_statistics_cache.items():
                        _now = datetime.datetime.now()
                        _packet_group_uuid = _item[0];
                        _packetStatItem    = _item[1];
                        if timedeltaToSecond(_now - _packetStatItem._firstTime) >= 5:
                            _items.append(_item)
                            del self._recv_multicast_statistics_cache[_packet_group_uuid]
                            
            if _is_recv_multicast_statistics_cache_empty==True:
                print("recv: 0 multicast packet(s)");
            else:
                if len(_items)==0:
                    print("not multicast packet satisfy statistics condition")
                else:
                    for _item in _items:
                        print("recv: %s%%(%s/%s) multicast packet(s) for uuid '%s' from '%s'" % (len(_packetStatItem._packetSet) / float(_packetStatItem._packet_test_count) * 100,
                                                                                                 len(_packetStatItem._packetSet),
                                                                                                 _packetStatItem._packet_test_count,
                                                                                                 _packet_group_uuid, 
                                                                                                 _packetStatItem._fromAddr));
                        with self._trash_bag_mtx:
                            self._trash_bag[_packet_group_uuid] = TrashBagItem(_packet_group_uuid)
#             print("_multicastStatisticRunnable()2, size of self._trash_bag: %s" % len(self._trash_bag))
                     
    #
    def startSendDelayPacket(self):
        self._sendDelayPacketThread.start();
        print("start send delay packet thread")
        
        
    def _sendDelayPacketRunnable(self):
        while True:
            _packet_group_uuid = str(uuid.uuid4())
            msg = "%s|%s|%s" % (PacketType.delay_request, _packet_group_uuid, formatDatetime(datetime.datetime.now()));
            self._listen_sock.sendto(msg, self._target_addr);
            time.sleep(5);
    
    
    def _handleDelayRequestPacket(self, packet_data):
        
        _split_data = packet_data.split("|");
        
        if len(_split_data)!=3:
            print("<network_analyser>._handleDelayRequestPacket(), wrong delay request packet: %s" % packet_data)
            
        _packet_type       = int(_split_data[0])
        _packet_group_uuid = _split_data[1]
        _packet_send_time  = _split_data[2]
        
        if _packet_type!=PacketType.delay_request:
            print("<network_analyser>._handleDelayRequestPacket(), packet is not type of delay_request, packet: %s" % packet_data)
            
        msg = "%s|%s|%s|%s" % (PacketType.delay_response, _packet_group_uuid, _packet_send_time, formatDatetime(datetime.datetime.now()));
        self._listen_sock.sendto(msg, self._target_addr);
            
     
    def _statisticsDelayPacket(self, packet_data):
        
        print("\r\nstart delay analysis")
        _split_data = packet_data.split("|");
        
        if len(_split_data)!=4:
            print("<network_analyser>._statisticsDelayPacket(), data format wrong: %s" % packet_data)
            
        _packet_type       = int(_split_data[0])
        _packet_group_uuid = _split_data[1]
        _str_send_datetime = _split_data[2]
        _str_recv_datetime = _split_data[3]
        
        if _packet_type!=PacketType.delay_response:
            print("<network_analyser>._statisticsDelayPacket(), packet is not type of delay_response, packet: %s" % packet_data)
            
        _dt_send_datetime = parseToDatetime(_str_send_datetime)
        _dt_recv_datetime = parseToDatetime(_str_recv_datetime)
            
        _now = datetime.datetime.now()
        _str_now = formatDatetime(_now)
        _delta = timedeltaToSecond(_now - _dt_send_datetime)
        print("packet delay %sms, sent time %s, response time '%s'" % (_delta*1000/2, _dt_send_datetime, _str_now))
        
        if _dt_recv_datetime < _dt_send_datetime :
            print("warning: there is time inconsistency between this machine '%s' and target machine '%s', received time '%s' is earlier than sent time '%s'" % (_listen_ip, _target_ip, _str_recv_datetime, _dt_send_datetime))
            
        if _now < _dt_recv_datetime:
            print("warning: there is time inconsistency between this machine '%s' and target machine '%s', response received time '%s' is earlier than request received time '%s'" % (_listen_ip, _target_ip, _str_now, _str_recv_datetime))
          
    #
    def _trashBagCleanRunnable(self):
        while True:
#             print("_trashBagCleanRunnable()1, size of self._trash_bag: %s" % len(self._trash_bag))
            with self._trash_bag_mtx:
                _remove_uuids = [];
                for _item in self._trash_bag.items():
                    if timedeltaToSecond( datetime.datetime.now() - _item[1]._time ) > 30:
                        _remove_uuids.append(_item[0])
                for _packet_group_uuid in _remove_uuids:
                    del self._trash_bag[_packet_group_uuid]
#             print("_trashBagCleanRunnable()2, size of self._trash_bag: %s" % len(self._trash_bag))
            time.sleep(5)
    #     
    def doClose(self):
        self._listen_sock.close();


if __name__=="__main__":
    
    networkAnalyser = NetworkAnalyser();
    
    networkAnalyser.startSendCommonPacket();
    networkAnalyser.startRecvCommonPacket();
    networkAnalyser.startCommonStatistics();
     
    networkAnalyser.startSendMulticastPacket();
    networkAnalyser.startRecvMulticastPacket();
    networkAnalyser.startMulticastStatistics();
    
    networkAnalyser.startSendDelayPacket();
    
    while True:
        time.sleep(1)



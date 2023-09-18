from enum import Enum
import requests
#to decode the metainfo file, and decode tracker response
import bencodepy
#to save a list of peers to disk
import pickle
#to turn ints in to big endian bytes with struct.pack('>I', int)
import struct
#to calculate the info_hash
import hashlib
#to urlencode strings
import urllib.parse
#to connect to the individual peers
import socket
#to handle peer connection simultaneously
import threading
from time import sleep
import ipaddress


class MessageType(Enum):
    KEEPALIVE       = -1,
    CHOKE           = 0,
    UNCHOKE         = 1,
    INTERESTED      = 2,
    NOTINTERESTED   = 3,
    HAVE            = 4,
    BITFIELD        = 5,
    REQUEST         = 6,
    PIECE           = 7,
    CANCEL          = 8,
    PORT            = 9,

class PeerMessage:

    def __init__(self,length_prefix, message_id,payload):
        
        self.length_prefix  = length_prefix
        self.message_id     = message_id
        
        if self.length_prefix == 0 or message_id == None:
            self.message_type = MessageType.KEEPALIVE
            return

        self.payload        = payload

        match self.message_id:
            case 0:
                self.message_type = MessageType.CHOKE
            case 1:
                self.message_type = MessageType.UNCHOKE
            case 2:
                self.message_type = MessageType.INTERESTED
            case 3:
                self.message_type = MessageType.NOTINTERESTED
            case 4:
                self.message_type = MessageType.HAVE
            case 5:
                self.message_type = MessageType.BITFIELD
            case 6:
                self.message_type = MessageType.REQUEST
            case 7:
                self.message_type = MessageType.PIECE
            case 8:
                self.message_type = MessageType.CANCEL
            case 9:
                self.message_type = MessageType.PORT
            case _:
                #error, exit!
                exit(f'unknown message type: {message_id}')

    
    def from_socket(socket):
        response = socket.recv(4)
        #prefix is a four byte big endian value
        length_prefix = int.from_bytes(response[0:4], 'big')

        if not length_prefix:
            return PeerMessage(length_prefix = 0, message_id = None, payload = None)
        else:
            #add the rest of the message to the response
            payload = socket.recv(length_prefix)
            #message id is single byte decimal value
            message_id = payload[0]
            return PeerMessage(length_prefix = length_prefix, message_id = message_id, payload=payload[1:])
        
'''
representation of remote peer
'''
class Peer:

    def __init__(self, ip, port, peer_id,info_hash):

        #all clients start out this way
        self.am_choking         = True
        self.am_interested      = False
        self.peer_choking       = True
        self.peer_interested    = False
        self.has_pieces         = []
        self.has_requested_piece= []
        self.completed_pieces   = []
        #ip and port required for socket connection with peer
        self.ip                 = ip
        self.peer_id            = peer_id
        self.port               = port
        #required for handshake with peer
        self.info_hash          = info_hash
        self.keepalives         = 0
    
    '''
        returns true for successful handshake, false if not
    '''
    def send_handshake(self):
        #components for building the handshake
        pstrlen     = b'\x13'
        pstr        = b'BitTorrent protocol'
        reserved    = b'\x00\x00\x00\x00\x00\x00\x00\x00'
        info_hash   = bytearray.fromhex(self.info_hash)
        
        #check for valid connection
        if hasattr(self, 'socket_connection'):
            #build the handshake
            request = pstrlen + pstr + reserved + info_hash + self.peer_id
            #send the handshake to peer
            self.socket_connection.sendall(request)
            #get the response
            response            = self.socket_connection.recv(68)
            
            #compare our handshake with theirs, as per the spec
            chars_before_hash   = len(pstrlen)+len(pstr)+len(reserved)
            hash_length         = len(info_hash)

            their_hash          = response [chars_before_hash : chars_before_hash + hash_length]
            our_hash            = request  [chars_before_hash : chars_before_hash + hash_length]
           
            #if equal, we have a successful connection!
            if(their_hash == our_hash):
                return True
            #if not, we just fall through to the "return false" part

        #here we have either no socket_connection, or our hashes don't match
        return False

    '''
    Basically just an infinite loop, that gets messages from peers, and sends them back

    '''
    def start_peer_communication(self):
        while True:
            message = PeerMessage.from_socket(self.socket_connection)
            
            match message.message_type:
                #to implement my own keepalive, set a timeout on the "recv()"
                #send my own keepalive message after that timeout and start
                #listening again
                case MessageType.KEEPALIVE:
                    pass
                    #print('got keepalive, ignoring')
                    
                    #self.keepalives += 1
                    #if self.keepalives > 20:
                    #    exit('too many keepalives')
                case MessageType.CHOKE:
                    print('received choke')
                    self.peer_choked = True
                case MessageType.UNCHOKE:
                    print('received unchoke')
                    #self.send_unchoke_message()
                    self.peer_choked = False
                case MessageType.INTERESTED:
                    print('received interested')
                    self.peer_interested = True
                case MessageType.NOTINTERESTED:
                    print('received notinterested')
                    self.peer_interested = False
                case MessageType.HAVE:
                    piece_index = int.from_bytes(message.payload, 'big')
                    print(f'received index {message.payload}, {int.from_bytes(message.payload)} as int, {struct.pack(">I", int.from_bytes(message.payload))} back to lil byte')
                    self.has_pieces.append(piece_index)
                    print('got have msg, index: ',piece_index)
                case MessageType.BITFIELD:
                    print('got bitfield msg')
                case MessageType.REQUEST:
                    index = ''
                    begin = ''
                    length = ''
                    print(f'got request msg, for index: {index}')
                case MessageType.PIECE:
                    print('got piece msg')
                    exit('we did it?')
                case MessageType.CANCEL:
                    print('got cancel msg')
                case MessageType.PORT:
                    print('got port msg')

            #print('checking for choking and pieces')

            if not self.peer_choked and  self.has_pieces:
                #print('not chocking and has pieces')
                for piece in self.has_pieces:
                    #print('checking piece ',piece)
                    if not piece in self.completed_pieces:
                        print('requesting piece')
                        self.send_request_message(piece, 0, 2^15)
                        self.completed_pieces.append(piece)


    def send_message(self, message):
        print('sending message')
        if hasattr(self, 'socket_connection'):
            self.socket_connection.sendall(message)
        else:
            exit('something wrong, sending unchoke message on a non-existing socket?')

    def send_request_message(self, index, begin, length):
        request_message = struct.pack(">I", 13) + b'\x06' + struct.pack(">I",index) +struct.pack(">I",0)+ struct.pack(">I", 32768)
        self.send_message(request_message)

    def send_unchoke_message(self):
        unchoke_message = b'\x00\x00\x00\x01\x01'
        self.send_message(unchoke_message)

    def send_interested_message(self):
        interested_message = b'\x00\x00\x00\x01\x02'
        self.send_message(interested_message)


    def start_connection(self):
        try:
            #connect through ipv6 or ipv4, depending on what the peer uses
            if ipaddress.ip_address(self.ip).version == 4:
                self.socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            else:
                self.socket_connection = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

            self.socket_connection.connect((self.ip, self.port))
            successful_handshake = self.send_handshake()
            
            if not successful_handshake:
                print('disconnecting from {self.ip} cause no successful handshake')
            else:
                print('connected and successful handshake! starting communication with peer')
                self.send_interested_message()
                self.send_unchoke_message()
                self.start_peer_communication() 

            self.socket_connection.close()

        except Exception as e:
            print(f'could not connect to {self.ip}:{self.port} because {e}')

class TorrentClient:
    '''
        requires user to set location of metainfo file, and to generate a peer_id
    '''
    def __init__(self, metainfo_file, peer_id):

        self.metainfo_file  = metainfo_file
        self.peer_id        = peer_id
    
    '''
        decodes the metainfo(torrent) file, returns: announce_url, info_hash, port
        info_hash is a urlencoded 20-byte SHA1 hash of the value of the info key from the Metainfo file.
    '''
    def bedecode_metainfo(self):

        #get torrent file handle
        metainfo_filehandle     = open(self.metainfo_file, "rb")
        
        #read file as binary
        binary_data             = metainfo_filehandle.read()
        
        #bdecode the thing
        decoded                 = bencodepy.decode(binary_data)
        info_value              = decoded[b'info']
        total_size              = decoded[b'info'][b'length']
        bencoded_info           = bencodepy.encode(info_value)
        info_hashbrown          = hashlib.sha1(bencoded_info).digest()
        info_hash               = urllib.parse.quote(info_hashbrown, safe='')
        hex_hash                = hashlib.sha1(bencoded_info).hexdigest()
        return  decoded[b'announce'], hex_hash, decoded[b'port'] if b'port' in decoded.keys() else 6881, total_size

    def request_tracker(self, announce_url, info_hash,peer_id,port, size):
        #perform http get request
        uploaded = 0
        downloaded = 0
        left = size
        request = f"{announce_url.decode('utf-8')}?info_hash={info_hash}&peer_id={peer_id}&port={port}&uploaded={uploaded}&downloaded={downloaded}&left={left}&event=started"
        response = requests.get(request)
        return response

    def download(self):
        announce_url, info_hash, port, total_size = self.bedecode_metainfo()
        tracker_response = self.request_tracker(announce_url, urllib.parse.quote(bytearray.fromhex(info_hash)), "thurmanmermanddddddd", port, total_size)
        torrent_peers = []

        try:
            raise ValueError('pls')
            torrent_peers = pickle.load(open("torrent_peers.pickle", 'rb'))
            print(f'loaded {len(torrent_peers)} peers from disk')
        except: 
            bdecoded_response = bencodepy.decode(tracker_response.content)
            for peer in bdecoded_response[b'peers']:
                torrent_peers.append(Peer(peer[b'ip'].decode('utf-8'),peer[b'port'],b"thurmanmermanddddddd", info_hash))
            pickle.dump(torrent_peers, open('torrent_peers.pickle', 'wb'))
            print(f'requested {len(torrent_peers)} new peers from tracker')

        
        #this is goign to be used to signal the threads to stop when required
        stop_event = threading.Event()

        #the function passed to every thread that handles peer connection
        def peer_connection(peer, event):
            peer.start_connection()
 
        # use `event = Event()` to ensure that threads can be stopped later.

        #create a thread for every peer in the torrent_list
        thread_list = []
        for peer in torrent_peers:
            thread_list.append(threading.Thread(target=peer_connection, args=(peer, stop_event)))
        
        #start all those threads
        for thread in thread_list:
            thread.start()

        sleep(10)

        #assume we are done, close all the thread
        for thread in thread_list:
            thread.join()
        print('all threads joined')



t = TorrentClient(metainfo_file='./ubuntu.torrent', peer_id="thurmanmermanddddddd")
t.download()

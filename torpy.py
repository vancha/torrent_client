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
#to calculate the total number of pieces
import math

#2 minutes is the default timeout time for a peer in a bittorrent connection
BITTORRENT_TIMEOUT_SECONDS  = 60 * 2

#the peer id by which i present myself to other peers
MY_PEER_ID                  = "thurmanmermanddddddd"

#the size of the subpieces we request, when we know a peer has a piece we do not
SUB_PIECE_SIZE              = 2 ** 14

PIECE_LENGTH                = 0

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
        print('peer made with init!')
        #all clients start out this way
        self.am_choking         = True
        self.am_interested      = False
        self.peer_choking       = True
        self.peer_interested    = False
        self.has_pieces         = []
        self.completed_pieces   = []
        self.requested_pieces   = {}

        #ip and port required for socket connection with peer
        self.ip                 = ip
        self.peer_id            = peer_id
        self.port               = port

        #required for handshake with peer
        self.info_hash          = info_hash

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

            #return true if hashes match, fall through to false if not
            if(their_hash == our_hash):
                return True

        #here we have either no socket_connection, or our hashes don't match
        return False

    '''
    Basically just an infinite loop, that gets messages from peers, and sends them back

    '''
    def start_peer_communication(self):
        while True:

            #get one message from the socket
            message = PeerMessage.from_socket(self.socket_connection)

            #check what kind of message it is, and handle it appropriately
            match message.message_type:
                #to implement my own keepalive, set a timeout on the "recv()"
                #send my own keepalive message after that timeout and start
                #listening again
                case MessageType.KEEPALIVE:
                    pass
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
                    print(f'received have for {piece_index}')
                    self.has_pieces.append(piece_index)
                case MessageType.BITFIELD:
                    print('got bitfield msg, wtf do i do?')
                case MessageType.REQUEST:
                    index = int.from_bytes(message.payload[0])
                    begin = int.from_bytes(message.payload[1])
                    length = int.from_bytes(message.payload[2])
                    print(f'got request msg, for index: {index}, begin: {begin}, length: {length}')
                case MessageType.PIECE:
                    piece_index             = int.from_bytes(message.payload[0:4])
                    subpiece_start_index    = int.from_bytes(message.payload[4:8])
                    subpiece_index          = subpiece_start_index // SUB_PIECE_SIZE
                    length                  = int.from_bytes(message.payload[8:12])
                    block                   = message.payload[13:]
                    print('GETTING PIECE')
                    print(f'payload: {block}')
                    print(f'index: {piece_index}')
                    print(f'begin: {subpiece_start_index}')
                    print(f'length: {length}')
                    print(f'this piece is at index {subpiece_index}')
                    #piece_index = message.payload[0:4]
                    #start_index = message.payload[1]
                    #block = message.payload[2:]

                    #print(f'receiving piece index {piece_index}, starting at {start_index} and ending at {start_index + PIECE_LENGTH} ')
                    #print(f'looks like: {block}')
                    #index = int.from_bytes(message.payload[0])
                    #begin = int.from_bytes(message.payload[1])
                    #block = int.from_bytes(message.payload[2:])

                    #if we don't have this piece, request it completely
                    #262144 is the piece size, we ask for 2 ** 14 bytes per request
                    #that makes 16 total requests before we have the whole piece
                    #for i in range(0, math.ceil( PIECE_LENGTH / SUB_PIECE_SIZE)):
                    #    self.send_request_message(i, i * SUB_PIECE_SIZE, SUB_PIECE_SIZE)

                    #the length prefix seems to match my request perfectly, with the additional 9 bytes as per the protocol :)
                    #print(f'got piece msg of size {message.length_prefix}, which is {SUB_PIECE_SIZE - 13}')
                    #print(f'index of this piece is {index}')
                    #print(f'it starts at {begin}')
                    #print(f'and looks like {block}')
                case MessageType.CANCEL:
                    print('got cancel msg')
                case MessageType.PORT:
                    print('got port msg')

            print(f'Peer object has the following properties: {vars(self)}')
            if not self.peer_choked and  self.has_pieces:
                for piece in self.has_pieces:
                    if piece not in self.completed_pieces and piece not in self.requested_pieces:
                        print(f'requesting piece {piece} (not in {self.requested_pieces.keys()})')
                        num_subpieces = math.ceil(PIECE_LENGTH / SUB_PIECE_SIZE)
                        self.requested_pieces[piece] = [None for _ in range(num_subpieces)]
                        for i in range(0, num_subpieces):
                            self.send_request_message(piece, i * SUB_PIECE_SIZE, SUB_PIECE_SIZE)
                            print(f'self.requested_pieces[{piece}][{i % SUB_PIECE_SIZE}] = None')
                            sleep(.1)


    def send_message(self, message):
        print('sending message')
        if hasattr(self, 'socket_connection'):
            self.socket_connection.sendall(message)
        else:
            exit('something wrong, sending unchoke message on a non-existing socket?')

    #index is the piece index, not the subpiece index
    def send_request_message(self, index, begin, length):
        print(f'requesting piece of size {length}')
        request_message = b'\x00\x00\x00\x0D\x06' + struct.pack(">I",index) +struct.pack(">I",begin)+ struct.pack(">I", length)
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
            self.socket_connection.settimeout(BITTORRENT_TIMEOUT_SECONDS)
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
        global PIECE_LENGTH
        PIECE_LENGTH            = decoded[b'info'][b'piece length']

        total_pieces            = math.ceil(total_size / PIECE_LENGTH)
        #total pieces should equal the length of decoded[b'info'][b'pieces'] / 20, cause
        #all those hashes are 20 bytes each
        print(f"info keys: {decoded[b'info'].keys()}")
        print(f"root keys: {decoded.keys()}")
        print(f"total length: {decoded[b'info'][b'length']}")

        print(f"num pieces: {len(decoded[b'info'][b'pieces']) // 20}")


        print(f"piece length: {PIECE_LENGTH}")
        print(f"total pieces: {total_pieces}")

        return  decoded[b'announce'], hex_hash, decoded[b'port'] if b'port' in decoded.keys() else 6881, total_size

    '''
    gets the list of peers from the tracker/announce url
    '''
    def request_tracker(self, announce_url, info_hash,peer_id,port, size):

        #Get peers through http GET request
        uploaded = 0
        downloaded = 0
        left = size

        #build the url to which to send the request to, and add the required parameters
        request = f"{announce_url.decode('utf-8')}?info_hash={info_hash}&peer_id={peer_id}&port={port}&uploaded={uploaded}&downloaded={downloaded}&left={left}&event=started"
        response = requests.get(request)
        return response

    '''
    start downloading
    '''
    def download(self):
        announce_url, info_hash, port, total_size = self.bedecode_metainfo()

        #exit('making an exit')
        torrent_peers = []

        try:
            #raise ValueError('pls')
            torrent_peers = pickle.load(open("torrent_peers.pickle", 'rb'))
            print(f'loaded {len(torrent_peers)} peers from disk')
        except:
            tracker_response = self.request_tracker(announce_url, urllib.parse.quote(bytearray.fromhex(info_hash)), MY_PEER_ID, port, total_size)
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

        sleep(240)
        x = input('just waiting for you to type something')
        #assume we are done, close all the thread
        for thread in thread_list:
            thread.join()
        print('all threads joined')


t = TorrentClient(metainfo_file='./ubuntu.torrent', peer_id=MY_PEER_ID)
t.download()

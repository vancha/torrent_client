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

        self.length_prefix  = lenght_prefix
        self.message_id     = message_id
        self.payload        = payload
    
    def from_response(response):
        pass

class Peer:

    def __init__(self, ip, port, peer_id,info_hash):

        #all clients start out this way
        self.am_choking      = True
        self.am_interested   = False
        self.peer_choking    = True
        self.peer_interested = False
        
        #ip and port required for socket connection with peer
        self.ip             = ip
        self.peer_id        = peer_id
        self.port           = port
        #required for handshake with peer
        self.info_hash      = info_hash

    def send_handshake(self):
        if self.hasattr('socket_connection'):
            #this should be the 68 byte long handshake
            self.socket_connection.sendall(f"{pstrlen}{ipstr}{reserved}{info_hash}{peer_id}")
            #size of handshake for bittorrent protocol 1.0
            response = self.socket_connection.recv(68)
            print('handshake response: ',str(response))
        else:
            print('no connection, will not send handshake')


    def start_connection(self):
        try:
            self.socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_connection.connect((self.ip, self.port))
            #self.send_handshake()
            self.socket_connection.close()
            print(f'bruh {self.ip}:{self.port} this was so successful is unbelieve')
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
        info_hash               = urllib.parse.quote(info_hashbrown, safe='')#bytes(info_hashbrown, 'utf-8'), safe='')
        
        return  decoded[b'announce'], info_hash, decoded[b'port'] if b'port' in decoded.keys() else 6881, total_size

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
        tracker_response = self.request_tracker(announce_url, info_hash, "thurmanmermanddddddd", port, total_size)
        torrent_peers = []

        try:
            torrent_peers = pickle.load(open("torrent_peers.pickle", 'rb'))
            print('loaded peers from disk')
        except: 
            bdecoded_response = bencodepy.decode(tracker_response.content)
            for peer in bdecoded_response[b'peers']:
                torrent_peers.append(Peer(peer[b'ip'].decode('utf-8'),peer[b'port'],peer[b'peer id'], info_hash))#[peer[b'ip'], peer[b'peer id'], peer[b'port']])
            pickle.dump(torrent_peers, open('torrent_peers.pickle', 'wb'))
            print('requested new peers from tracker')

        print(f'peers: {torrent_peers}')
        
        #this is goign to be used to signal the threads to stop when required
        stop_event = threading.Event()

        #the function passed to every thread that handles peer connection
        def peer_connection(peer, event):
            peer.start_connection()
 
        #initial work to start multiple threads. After for loop, make sure every socket connection is done in it's own thread,
        # use `event = Event()` to ensure that threads can be stopped later.
        thread_list = []
        for peer in torrent_peers:
            thread_list.append(threading.Thread(target=peer_connection, args=(peer, stop_event)))

        for thread in thread_list:
            thread.start()

        sleep(10)
        
        for thread in thread_list:
            thread.join()
        print('all threads joined')
        '''
        #print(f"interval: {bdecoded_response[b'interval']}")
        #print(f"peers: {bdecoded_response[b'peers']}")'''



t = TorrentClient(metainfo_file='./ubuntu.torrent', peer_id="thurmanmermanddddddd")
t.download()

from enum import Enum
import requests
import bencodepy

import struct
#to turn int to 4 byte big endian: struct.pack('>I', your_int)

import hashlib
import urllib.parse

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

        #process response, return Message
        pass

class Peer:

    def __init__(self):

        #all clients start out this way
        am_choking      = True
        am_interested   = False
        peer_choking    = True
        peer_interested = False
    
    def connect(self):
        pass

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
        info_hashbrown          = hashlib.sha1(bencoded_info).hexdigest()
        info_hash               = bytes(info_hashbrown, 'utf-8')
        
        return  decoded[b'announce'], urllib.parse.quote(info_hash), decoded[b'port'] if b'port' in decoded.keys() else 6881, total_size

    def request_tracker(self, announce_url, info_hash,peer_id,port, size):#,uploaded,downloaded,left):
        #perform http get request
        uploaded = 0
        downloaded = 0
        left = size
        #urlencode the info hash
        request = f"{announce_url.decode('utf-8')}?info_hash={info_hash}&peer_id={peer_id}&port={port}&uploaded={uploaded}&downloaded={downloaded}&left={left}&event=started"
        response = requests.get(request)
        return response.content.decode('utf-8')

    def download(self):
        announce_url, info_hash, port, total_size = self.bedecode_metainfo()
        tracker_response = self.request_tracker(announce_url, info_hash, port, "thurmanmermanddddddd", total_size)
        print('tracker response: ',tracker_response)
        #print('info hash: ',info_hash)
        #print(f'announce url: {announce_url}')
        #response = self.request_tracker(announce_url, info_hash, "thurmanmermanddddddd",port,0,0,0)
        #print('response: ',response)


t = TorrentClient(metainfo_file='/home/vancha/Documents/rust/torrent_test/ubuntu.torrent', peer_id="thurmanmermanddddddd")
t.download()

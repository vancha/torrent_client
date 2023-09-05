from enum import Enum
import requests
import bencodepy

import struct
#to turn int to 4 byte big endian: struct.pack('>I', your_int)

import hashlib

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
        bencoded_info           = bencodepy.encode(info_value)
        info_hashbrown          = hashlib.sha1(bencoded_info).hexdigest()
        info_hash               = bytes(info_hashbrown, 'utf-8')
        
        #return important data
        #to fix this function, make sure info_hash is urlencoded with urllib.parse.urlencode()
        return  decoded[b'announce'], info_hash, decoded[b'port'] if b'port' in decoded.keys() else 6881

    def request_tracker(self, announce_url, info_hash,peer_id,port,uploaded,downloaded,left):
        #perform http get request
        #urlencode the info hash
        request = f"{announce_url}?info_hash={info_hash.decode('utf-8')}&peer_id={peer_id}&port={port}&uploaded={uploaded}&downloaded={downloaded}&left={left}&event=started"
        response = requests.get(request)
        print('request: ',request.decode('utf-8'));
        return resonse.content.decode('utf-8')

    def download(self):
        announce_url, info_hash, port = self.bedecode_metainfo()
        print('info hash: ',info_hash)

        #print(f'announce url: {announce_url}')
        #response = self.request_tracker(announce_url, info_hash, "thurmanmermanddddddd",port,0,0,0)
        #print('response: ',response)


t = TorrentClient(metainfo_file='/home/vancha/Documents/rust/torrent_test/ubuntu.torrent', peer_id="thurmanmermanddddddd")
t.download()

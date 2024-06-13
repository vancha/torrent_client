from    collections                     import OrderedDict
from    bencode_decoder.bencode_decoder import bdecoder
from    metainfofile                    import MetaInfoFile
from    tracker                         import Tracker
from    peer                            import Peer
#to generate the sha-1 info_hash from the info_dict
import  hashlib
#to perform http GET request
from    urllib          import request
#to perform urlencoding on for example the info_hash
from    urllib.parse    import quote
  

PEER_ID = "thurmanmermanddddddd"

#Decode metainfo file
mif = MetaInfoFile( "./ubun.torrent" )
#set up tracker using valuers from decoded metainfo file
tracker = Tracker( mif, PEER_ID )
#send the http "GET" request to the tracker to get list of peers


#attempts to get peers from tracker
response = tracker.get_peers()

#get peer descriptions from the response, just assume this was successful
peers = list(bdecoder.decode(response).values())[3]

#turn the list of peer descriptions to a list of actual peer objects
peers = list(map(lambda description: Peer(PEER_ID, description[b"ip"].decode('utf-8'), description[b"port"], mif), peers))

#connect to them
for peer in peers:
    peer.connect()

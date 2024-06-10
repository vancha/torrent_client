from    collections                     import OrderedDict
from    bencode_decoder.bencode_decoder import bdecoder
from    metainfofile                    import MetaInfoFile
from    tracker                         import Tracker
#to generate the sha-1 info_hash from the info_dict
import  hashlib
#to perform http GET request
from    urllib          import request
#to perform urlencoding on for example the info_hash
from    urllib.parse    import quote
import pprint


PEER_ID = "thurmanmermanddddddd"

#Decode metainfo file
mif = MetaInfoFile( "./ubun.torrent" )
#set up tracker using valuers from decoded metainfo file
tracker = Tracker( mif, PEER_ID )
#send the http "GET" request to the tracker to get list of peers



peers = tracker.get_peers()
print(pprint.pprint(bdecoder.decode(peers)))
#print(f'peers: {peers}')



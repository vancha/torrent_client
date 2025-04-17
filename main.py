from collections import OrderedDict
from bencode_decoder.bencode_decoder import bdecoder
from torrent_client import TorrentClient
from peer import Peer
from threading import Thread


# to generate the sha-1 info_hash from the info_dict
import hashlib
import time

# to perform http GET request
from urllib import request

# to perform urlencoding on for example the info_hash
from urllib.parse import quote

# set up tracker using valuers from decoded metainfo file
#tracker = Tracker(mif, PEER_ID)

# attempts to get peers from tracker
#response = tracker.get_peers()

# get peer descriptions from the response, just assume this was successful
#peers = list(bdecoder.decode(response).values())[3]
#print(f"peers: {peers}")

# turn the list of peer descriptions to a list of actual peer objects
#peers = list(
#    map(
#        lambda description: Peer(
#            PEER_ID, description[b"ip"].decode("utf-8"), description[b"port"], mif
#        ),
#        peers,
#    )
#)
client = TorrentClient()
while True:
    client.step()
    time.sleep(.01)


# connect to them
#for peer in peers:
    #peer.connect()
#    Thread(target = peer.connect).start()
    

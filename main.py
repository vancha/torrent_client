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
import socket
from ipaddress import ip_address, IPv4Address 
  
def is_ipv4(ip: str):
    if type(ip_address(ip)) is IPv4Address:
        return True
    else:
        return False

PEER_ID = "thurmanmermanddddddd"

#Decode metainfo file
mif = MetaInfoFile( "./ubun.torrent" )
#set up tracker using valuers from decoded metainfo file
tracker = Tracker( mif, PEER_ID )
#send the http "GET" request to the tracker to get list of peers


#attempts to get peers from tracker
response = tracker.get_peers()
#get peers from the response, just assume this was successful
peers = list(bdecoder.decode(response).values())[3]

for peer in peers:
    peer_id     = peer[b"peer id"]
    peer_ip     = peer[b"ip"].decode('utf-8')
    peer_port   = peer[b"port"]
    #maybe focus on ipv4 for now, forget v6
    if is_ipv4(peer_ip):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((peer_ip, peer_port))
                print(f'connected to {peer_ip}, now its time to perform the secret handshake')
            except TimeoutError:
                print('timeout')
            except InterruptedError:
                print('interrupted')
        print('done with the connection, i got nothing')



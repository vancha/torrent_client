import requests
from urllib.parse import urlencode
from constants import PEER_ID
from bencode_decoder.bencode_decoder import bdecoder
from peer import Peer


"""
represents the tracker and handles all communication with it
"""


class TrackerClient:
    def __init__(self, meta_info_object, port=6881): 
        self.port = port
        self.mif = meta_info_object

    '''
        returns a list of peers or None
        as a side effect, remembers the current time, so that if get_peers is called earlier than the allowed interval of the tracker, we can decide if we want to go through with the request
        @Todo: 
        
    '''
    def get_peers(self, uploaded=0, downloaded=0, left=0, event="started", numwant=30):
        # lets build the url first with all the parameters inserted
        urlencoded_info_hash = self.mif.get_urlencoded_info_hash()
        announce_url = self.mif.get_announce_url()
        url = f"{announce_url}?info_hash={urlencoded_info_hash}&peer_id={PEER_ID}&port={self.port}&uploaded={uploaded}&downloaded={downloaded}&left={left}&event={event}&numwant={numwant}"

        response = requests.get(url)


        if response.status_code == 200:
            print(f"received tracker response")
            peer_descriptions = list(bdecoder.decode(response.content).values())[3]
            peer_conversion_lambda = lambda peer_desc: Peer(PEER_ID, peer_desc[b"ip"].decode("utf-8"), peer_desc[b"port"], self.mif)
            res =  map(peer_conversion_lambda, peer_descriptions)
            return list(res)
        else:
            print(f"tracker did not return a correct response: {response.status_code }")
            #something went wrong, no peers to return
            return []

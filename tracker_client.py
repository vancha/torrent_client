import requests
from urllib.parse import urlencode
from constants import PEER_ID


"""
represents the tracker and handles all communication with it
"""


class TrackerClient:
    def __init__(self, meta_info_object, port=6881): 
        self.port = port
        self.urlencoded_info_hash = meta_info_object.get_urlencoded_info_hash()
        self.announce_url = meta_info_object.get_announce_url()

    '''
        returns a list of peers or None
        as a side effect, remembers the current time, so that if get_peers is called earlier than the allowed interval of the tracker, we can decide if we want to go through with the request
        @Todo: 
        
    '''
    def get_peers(self, uploaded=0, downloaded=0, left=0, event="started", numwant=30):
        # lets build the url first with all the parameters inserted
        url = f"{self.announce_url}?info_hash={self.urlencoded_info_hash}&peer_id={PEER_ID}&port={self.port}&uploaded={uploaded}&downloaded={downloaded}&left={left}&event={event}&numwant={numwant}"

        response = requests.get(url)

        if response.status_code != 200:
            raise Exception(
                "Something went wrong", "Could not get the list of peers from tracker"
            )
        else:
            return response.content

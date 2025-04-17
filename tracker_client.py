import requests
from urllib.parse import urlencode


"""
represents the tracker and handles all communication with it
"""


class TrackerClient:
    def __init__(self, meta_info_object, peer_id, port=6881):
        self.left = self.calculate_bytes_left()
        self.port = port
        self.peer_id = peer_id
        self.urlencoded_info_hash = meta_info_object.get_urlencoded_info_hash()
        self.announce_url = meta_info_object.get_announce_url()
    
    #def calculate_bytes_left(self):
    #    return meta_info_object.get_total_bytes()

    '''
        returns a list of peers or None
        as a side effect, remembers the current time, so that if get_peers is called earlier than the allowed interval of the tracker, we can decide if we want to go through with the request
        @Todo: 
        
    '''
    def get_peers(self, uploaded=0, downloaded=0, left=None, event="started", numwant=30):
        if not left:
            left = self.left
        # lets build the url first with all the parameters inserted
        url = f"{self.announce_url}?info_hash={self.urlencoded_info_hash}&peer_id={self.peer_id}&port={self.port}&uploaded={uploaded}&downloaded={downloaded}&left={left}&event={event}&numwant={numwant}"

        response = requests.get(url)

        if response.status_code != 200:
            raise Exception(
                "Something went wrong", "Could not get the list of peers from tracker"
            )
        else:
            return response.content

import requests
from urllib.parse import urlencode

class TrackerException(Exception):
    '''Exception raises when things to wrong'''
    pass

'''
represents a tracker
get_peers either returns a list of peers, or a trackerexception
'''
class Tracker:
    def __init__(self, meta_info_object, peer_id, port=6881):
        self.left                   = meta_info_object.get_total_bytes()
        self.port                   = port
        self.peer_id                = peer_id
        self.urlencoded_info_hash   = meta_info_object.get_urlencoded_info_hash()
        self.announce_url           = meta_info_object.get_announce_url()

    #can respond in "compact" mode regardless of the value set for compact
    def get_peers(self, uploaded=0, downloaded=0, left=None,  event="started"):
        if not left:
            left = self.left
        #lets build the url first with all the parameters inserted
        url = f"{self.announce_url}?info_hash={self.urlencoded_info_hash}&peer_id={self.peer_id}&port={self.port}&uploaded={uploaded}&downloaded={downloaded}&left={left}&event={event}"
        
        response = requests.get(url)

        if response.status_code != 200:
            raise TrackerException('Something went wrong','Could not get the list of peers from tracker')
        else:
            return response.content


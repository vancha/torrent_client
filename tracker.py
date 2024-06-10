import requests


class Tracker:
    def __init__(self, meta_info_object, peer_id, port=6881):
        self.left                   = meta_info_object.get_total_bytes()
        self.port                   = port
        self.peer_id                = peer_id
        self.urlencoded_info_hash   = meta_info_object.get_urlencoded_info_hash()
        self.announce_url           = meta_info_object.get_announce_url()

    def get_peers(self, uploaded=0, downloaded=0, left=None, compact=0, no_peer_id=0, event="started"):
        if not left:
            left = self.left
        #lets build the url first with all the parameters inserted
        if event:
            url = f"{self.announce_url}?info_hash={self.urlencoded_info_hash}&peer_id={self.peer_id}&port={self.port}&uploaded={uploaded}&downloaded={downloaded}&left={left}&event={event}"
        else:
            url = f"{self.announce_url}?info_hash={self.urlencoded_info_hash}&peer_id={self.peer_id}&port={self.port}&uploaded={uploaded}&downloaded={downloaded}&left={left}"
        response = requests.get(url)
        if response.status_code != 200:
            return -1
        else:
            return response.content

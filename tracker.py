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
            url = f"{self.announce_url}?info_hash={self.urlencoded_info_hash}&peer_id={self.peer_id}&port={self.port}&uploaded={uploaded}&downloaded={downloaded}&left={left}&compact={compact}&no_peer_id={no_peer_id}"
        print(f'url: {url}')
        response = requests.get(url)
        if response.status_code != 200:
            print(f'status code: {response.status_code}')
            return -1
        else:
            return response.content
        #print(f'reponse content is {response.content}')

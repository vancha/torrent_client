from tracker_client import TrackerClient


'''
@todo:
    everytime a piece is downloaded, send a have message to every peer
    everytime the program exits, send a stopped event to the tracker
'''

class TorrentClient:
    def __init__(self):
        #probably needs the tracker url
        self.tracker_client = TrackerClient()
        self.peer_manager   = PeerManager()
        self.piece_selector = PieceSelector()
        
        peers = self.tracker_client.get_peers()
        self.peer_manager.add_peers(new_peers)
        
        
    #performs all the steps required for downloading a file
    def step(self):
        #drops connection with peers that are either disconnected, timed out, or otherwise
        self.peer_manager.refresh_peers()
    
        #check if we have enough peers
        if len(self.peer_manager.peers) < MIN_PEERS:
            new_peers = self.tracker_client.get_peers()
            self.peer_manager.add_peers(new_peers)
        
        #tell the peer_manager to tell the peers which pieces to request
        self.piece_selector.request_piece_from_peers(self.peer_manager.get_peers())

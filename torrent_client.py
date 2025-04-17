from tracker_client import TrackerClient
from metainfo_file import MetainfoFile
from peer_manager import PeerManager
from piece_selector import PieceSelector
from constants import MIN_PEERS

'''
@todo:
    everytime a piece is downloaded, send a have message to every peer
    everytime the program exits, send a stopped event to the tracker
'''

class TorrentClient:
    def __init__(self):
        #probably needs the tracker url
        self.metainfo_file = MetainfoFile("./test.torrent")
        self.tracker_client = TrackerClient(self.metainfo_file)
        self.peer_manager   = PeerManager()
        self.piece_selector = PieceSelector()
        
    def calculate_remaining_bytes(self):
        pass
    
    #performs all the steps required for downloading a file
    def step(self):
        #check if we have enough peers
        if len(self.peer_manager.peers) < MIN_PEERS:
            print(f"requesting new peers because {len(self.peer_manager.peers)} < {MIN_PEERS}")
            new_peers = self.tracker_client.get_peers()
            self.peer_manager.add_peers(new_peers)

        #drops connection with peers that are either disconnected, timed out, or otherwise
        self.peer_manager.refresh_peers()
        
        #tell the peer_manager to tell the peers which pieces to request
        self.piece_selector.get_available_pieces(self.peer_manager.get_peers())
        self.piece_selector.request_piece_from_peers(self.peer_manager.get_peers())

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

    def clean_shutdown(self):
        self.peer_manager.cache_peers()
        self.piece_selector.cache_piece_data()

    #performs all the steps required for downloading a file
    def step(self):
        #check if we have enough peers
        if len(self.peer_manager.get_peers()) < MIN_PEERS:
            self.peer_manager.get_more_peers( self.tracker_client )

        #drops connection with peers that are either disconnected, timed out, or otherwise
        self.peer_manager.refresh_peers()
        
        #tell the peer_manager to tell the peers which pieces to request
        self.piece_selector.step(self.peer_manager.get_peers(), self.metainfo_file)
        #self.piece_selector.get_available_pieces(self.peer_manager.get_peers())
        #self.piece_selector.request_piece_from_peers(self.peer_manager.get_peers())

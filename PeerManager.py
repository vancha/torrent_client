class PeerManager:
    #initialize the peermanager with a bunch of (cached) peers
    def __init__(self):
        self.peers = []
    
    def add_peers(self, peers):
        for peer in peers:
            if peer not in self.peers:
                try:
                    if peer.connect():
                    self.peers.append(peer)
                except Exception:
                    pass
                
    
    def get_peers(self):
        return self.peers
    
    #removes the peers that are no longer active
    def clean_up_peers(self):
        self.peers = list(filter(lambda peer: peer.is_connected() and peer.is_not_timed_out(), self.peers))
    
    
    def get_available_pieces(self):
        pieces = []
        for peer in self.peers:
            pieces.append()
        
        
    #the meat and perderders, gets called periodically to ensure a valid state of peers
    def refresh_peers(self):
        self.clean_up_peers()
        for peer in self.peers:
            #lets the peers send and receive messages
            peer.step()
            #next part  needs to send timeout message to prevent getting disconnected
            peer.maintain_connection()
        

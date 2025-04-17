import pickle

class PeerManager:
    #initialize the peermanager with a bunch of (cached) peers
    def __init__(self):
        self.peers = []
        #with open('cached_peers.pkl', 'rb') as f:
        #    print(f"pickle: {pickle.load(f)}")

    def __del__(self):
        #with open('cached_peers.pkl', 'wb') as f:
        #    pickle.dump(self.peers, f)
        pass

    def add_peers(self, peers):
        for peer in peers:
            try:
                if peer.connect():
                    print(f"peer connected")
                    self.peers.append(peer)
            except Exception:
                pass
                
    
    def get_peers(self):
        return self.peers
    
    #removes the peers that are no longer active
    def clean_up_peers(self):
        print(f"peers before cleanup: {len(self.peers)}")
        self.peers = list(filter(lambda peer: peer.is_active(), self.peers))
        print(f"peers after cleanup: {len(self.peers)}")

    #the meat and perderders, gets called periodically to ensure a valid state of peers
    def refresh_peers(self):
        self.clean_up_peers()
        for peer in self.peers:
            #lets the peers send and receive messages
            peer.step()
            #next part  needs to send timeout message to prevent getting disconnected
            peer.maintain_connection()
        

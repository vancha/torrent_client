import pickle

class PeerManager:
    #initialize the peermanager with a bunch of (cached) peers
    def __init__(self):
        self.peers = set()
        peers = self.load_peers()
        self.add_peers(peers)

    def add_peers(self, peers):
        for peer in peers:
            if peer not in self.peers and peer.connect():
                self.peers.add(peer)
            #else:
            #    print(f"peer is in self.peers or did not connect")
                
    def cache_peers(self):
        #remove the unhashable socket connections
        for peer in self.peers:
            del peer.socket
        #pickle the peers
        with open('cached_peers.pkl', 'wb') as f:
            pickle.dump(self.peers, f)


    def load_peers(self):
        try:
            with open('cached_peers.pkl', 'rb') as f:
                return pickle.load(f)
        except Exception:
            return []

    def get_peers(self):
        return self.peers
    
    def get_more_peers(self, tracker_client):
        new_peers = tracker_client.get_peers()
        self.add_peers(new_peers)

    #removes the peers that are no longer active
    def clean_up_peers(self):
        self.peers = set(filter(lambda peer: peer.is_active(), self.peers))
        #for n,peer in enumerate(self.peers):
        #    print(f"{n+1} active peer: {peer.is_active()} ({peer.ip})")

    #the meat and perderders, gets called periodically to ensure a valid state of peers
    def refresh_peers(self):
        self.clean_up_peers()
        for peer in self.peers:
            peer.step()

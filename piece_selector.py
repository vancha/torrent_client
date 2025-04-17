class PieceSelector:
    def __init__(self):
        self.available_pieces = set()

    def get_available_pieces(self, peers):
        print(f"getting pieces from peers")
        for peer in peers:
            self.available_pieces.append(peer.get_available_pieces())
        print(f"available pieces: {self.available_pieces}")


    def request_piece_from_peers(self, peers):
        if self.available_pieces:
            print(f"requesting pieces from peers")
        else:
            print(f"There are currently no available pieces")
    

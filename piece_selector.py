class PieceSelector:
    def __init__(self):
        self.available_pieces = set()
        self.outstanding_requests = set()

    def get_available_pieces(self, peers):
        for peer in peers:
            for piece in peer.get_available_pieces():
                print(f"adding {piece} to available pieces")
                self.available_pieces.add(piece)


    def request_piece_from_peers(self, peers):
        for peer in peers:
            #for every piece that's not already being requested
            for piece in self.available_pieces ^ self.outstanding_requests:
                if piece in peer.get_available_pieces():
                    peer.send_request_message(piece)
                    self.outstanding_requests.add(piece)


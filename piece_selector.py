import time
import pickle
import os
import hashlib

class PieceSelector:
    def __init__(self):
        self.available_pieces               = set()
        self.outstanding_requests           = set()
        self.pieces_pending_verification    = set()
        self.completed_pieces               = set()

    
    #@todo: store data like which pieces are in the process of being verified
    def cache_piece_data(self):
        pass
    
    #combines the subpieces into one piece, moves it to the "finished_pieces" folder
    def verify_piece(self, piece_index, mif):
        sub_pieces = []
        for part in range(16):
            try:
                f = open(f'pieces/piece{piece_index}part{part}.part','rb')
                sub_pieces.append(f.read())
            except FileNotFoundError:
                #should not happen, this should only be called if all subpieces are present
                print(f"Deleting piece because it's not complete")
                self.delete_piece(piece_index)
                return

        complete_piece = b''.join(sub_pieces)
        piece_hash = hashlib.sha1(complete_piece)
        digest = piece_hash.digest()
        
        #verify
        if mif.piece_hash_in_bytes(piece_index) == digest:
            print(f"piece {piece_index} verified")
            self.move_piece(piece_index)
            self.pieces_pending_verification.remove(piece_index)
            self.available_pieces.remove(piece_index)
            self.outstanding_requests.remove(piece_index)
            self.completed_pieces.add(piece_index)
        else:
            print(f"Deleting piece because verification failed")
            self.delete_piece(piece_index)
            #request it again
            self.outstanding_requests.remove(piece_index)
             #takes all the parts, combines them, and moves them to the completed folder

    def move_piece(self, piece_index):
        sub_pieces = []
        for part in range(16):
            f = open(f'pieces/piece{piece_index}part{part}.part','rb')
            sub_pieces.append(f.read())  
        complete_piece = b''.join(sub_pieces)
        with open(f"./completed_pieces/{piece_index}.piece", "wb") as binary_file:
            # Write bytes to file
            binary_file.write(complete_piece)
        
        print(f"Deleting piece because it has been moved")
        self.delete_piece(piece_index)
        print(f"piece moved")
    
        #deletes the piece from disk, it's bad >:(
        
    def delete_piece(self, piece_index):
        for part in range(16):
            try:
                file = f'pieces/piece{piece_index}part{part}.part'
                os.remove(file)
            except Exception as e:
                print(f"failed deleting piece {e}")
                #we don't care about exception, if a piece is missing we won't be able to find it
                pass
    
    
            
    def verify_completed_pieces(self, mif):
        pieces_to_verify = []
        
        for piece in self.pieces_pending_verification:
            pieces_to_verify.append(piece)
            
        for piece in pieces_to_verify:
            self.verify_piece(piece, mif)
    
    def step(self, peers, metainfo_file):
        self.get_completed_pieces_from_peers(peers)
        self.verify_completed_pieces( metainfo_file )
        self.get_available_pieces_from_peers(peers)
        self.request_piece_from_peers(peers)
        
        
    def request_piece_from_peers(self, peers):
        for peer in peers:
            #for every piece that's not already being requested
            for piece in self.available_pieces ^ self.outstanding_requests :
                if piece in peer.get_available_pieces():
                    if piece not in self.completed_pieces:
                        peer.send_request_message(piece)
                        time.sleep(0.01)
                        self.outstanding_requests.add(piece)
                    else:
                        peer.remove_available_piece(piece)
        print(f"outstanding requests: {self.outstanding_requests}")
    
    #
    def get_completed_pieces_from_peers(self, peers):
        for peer in peers:
            for piece in peer.get_completed_pieces():
                self.pieces_pending_verification.add(piece)
            peer.clear_completed_pieces()
    
    def get_available_pieces_from_peers(self, peers):
        for peer in peers:
            for piece in set(peer.get_available_pieces()) ^ self.available_pieces:
                if piece not in self.completed_pieces:
                    self.available_pieces.add(piece)
                else:
                    peer.remove_available_piece(piece)
        
        print(f"available pieces: {list(self.available_pieces)}")
    

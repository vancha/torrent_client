from bencode_decoder.bencode_decoder import bdecoder
from urllib.parse import quote
import hashlib
import bencodepy
import time

class MetaInfoFile:
    def __init__(self, torrent_file_path):
        # should store decoded file as self.meta_info_dict
        self.meta_info_dict = bdecoder.decode_from_file(torrent_file_path)

    # number of bytes in each piece, as integer
    def get_piece_length(self):
        return self.meta_info_dict[b"info"][b'piece length']
        
    # length of the entire file to download in bytes, only for single file mode, will crash for multiple file mode!
    def get_total_bytes(self):
        return self.meta_info_dict[b"info"][b"length"]
    
    #20 byte SHA1 hashes of all pieces
    def get_pieces(self):
        return self.meta_info_dict[b"info"][b"pieces"]
    
    #the total number of pieces to download
    def get_number_of_pieces(self):
        pieces = self.get_pieces()
        return len(pieces) // 20
    
    #the announce url of the tracker
    def get_announce_url(self):
        return self.meta_info_dict[b"announce"].decode("utf-8")

    def _get_info_dict(self):
        return self.meta_info_dict[b"info"]

    # gets the byte encoded info_hash
    def get_info_hash(self):
        # get decoded info dict
        info_dict = self._get_info_dict()
        # we need the hash of the encoded version, encode it
        info_dict = bencodepy.encode(info_dict)  # bdecoder.encode(info_dict)
        return hashlib.sha1(info_dict).hexdigest()

    #needed for the peer handshake
    def get_info_hash_bytes(self):
        info_hash = self.get_info_hash()
        return bytearray.fromhex(info_hash)

    #the hash of an individual piece
    def piece_hash_in_bytes(self, piece_number):
        pieces = self.get_pieces()
        start = piece_number * 20;
        end = start + 20
        return pieces[start:end]


    # gets the urlencoded version of the byte encoded hash
    def get_urlencoded_info_hash(self):
        info_hash = self.get_info_hash()
        return quote(bytearray.fromhex(info_hash))

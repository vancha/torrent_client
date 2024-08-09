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
        return self.meta_info_dict[b"pieces"]

    def get_total_bytes(self):
        # @todo: this will crash for multiple file mode torrents
        return self.meta_info_dict[b"info"][b"length"]

    def get_announce_url(self):
        return self.meta_info_dict[b"announce"].decode("utf-8")

    # 20 byte sha1 hashes of all pieces, as bytestring
    def _get_info_dict(self):
        return self.meta_info_dict[b"info"]

    # gets the byte encoded info_hash
    def get_info_hash(self):
        # get decoded info dict
        info_dict = self._get_info_dict()
        # we need the hash of the encoded version, encode it
        info_dict = bencodepy.encode(info_dict)  # bdecoder.encode(info_dict)
        return hashlib.sha1(info_dict).hexdigest()

    def get_info_hash_bytes(self):
        info_hash = self.get_info_hash()
        return bytearray.fromhex(info_hash)

    #This is not the way to do it, hardcoded only works for this specific torrent file
    def piece_hash_in_bytes(self, piece_number):
        file_content    = open('ubun.torrent','rb').read()
        pieces          = file_content[354:]
        piece_start     = piece_number * 20
        piece_end       = piece_start + 20
        return pieces[piece_start:piece_end]

    def verify_piece(self, piece_number):
        #try to collect all parts of the piece here
        sub_pieces = []
        #load all parts of this piece from disk (0 through 15)
        for part in range(16):
            #we will *try* to load the part from the disk
            try:
                f = open(f'pieces/piece{piece_number}part{part}.part','rb')
                sub_pieces.append(f.read())
            #but if we fail, that means this piece is incomplete, we cannot verify
            except FileNotFoundError:
                return False

        complete_piece = b''.join(sub_pieces)
        piece_hash = hashlib.sha1(complete_piece)
        digest = piece_hash.digest()

        return self.piece_hash_in_bytes(piece_number) == digest

    # gets the urlencoded version of the byte encoded hash
    def get_urlencoded_info_hash(self):
        info_hash = self.get_info_hash()
        return quote(bytearray.fromhex(info_hash))
        # return quote(info_hash)

from    bencode_decoder.bencode_decoder import bdecoder
from    urllib.parse    import quote
import  hashlib
import bencodepy

class MetaInfoFile:
    def __init__(self, torrent_file_path):
        #should store decoded file as self.meta_info_dict
        self.meta_info_dict = bdecoder.decode_from_file(torrent_file_path)

    #number of bytes in each piece, as integer
    def get_piece_length(self):
        return self.meta_info_dict[b"pieces"]

    def get_total_bytes(self):
        #@todo: this will crash for multiple file mode torrents
        return self.meta_info_dict[b"info"][b"length"]

    def get_announce_url(self):
        return self.meta_info_dict[b"announce"].decode('utf-8')

    #20 byte sha1 hashes of all pieces, as bytestring
    def _get_info_dict(self):
        return self.meta_info_dict[b"info"]

    #gets the byte encoded info_hash
    def get_info_hash(self):
        #get decoded info dict
        info_dict = self._get_info_dict()
        #we need the hash of the encoded version, encode it
        info_dict = bencodepy.encode(info_dict)#bdecoder.encode(info_dict)
        return  hashlib.sha1(info_dict).hexdigest()
   
    def get_info_hash_bytes(self):
        info_hash = self.get_info_hash()
        return bytearray.fromhex(info_hash)

    #gets the urlencoded version of the byte encoded hash
    def get_urlencoded_info_hash(self):
        info_hash = self.get_info_hash()
        return quote(bytearray.fromhex(info_hash))
        # return quote(info_hash)

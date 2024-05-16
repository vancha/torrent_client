'''
Holds all the data we read from the metainfo file. 
Ever part of the program that needs data from this file, can just get them from this object.

this will also hold the info hash

'''
class MetaInfo:

    def __init__(self, meta_info_file_location):
        #quick check to see if the input file exists and is a file
        if os.path.exists(torrent_file_location) and os.path.isFile(torrent_file_location):
            #steps:
            #read the file
    

    def get_info_hash(self):
        return self.info_hash
    
    def get_announce_url(self):
        return self.announce_url

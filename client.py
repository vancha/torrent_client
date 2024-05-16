class Client:
    #takes location to a torrent file, attempts to parse it
    def __init__(self, torrent_file_location):
        #the parsed meta info file
        meta_info_file  = MetaInfo(torrent_file_location)
        #the tracker to get the peers from
        tracker         = Tracker()
        #gets the tracker response, holds the peer list if successful
        response        = tracker.get_response()

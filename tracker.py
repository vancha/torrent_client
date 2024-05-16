class Tracker:
    #requires:
    # announce_url:         the base url to reach this tracker
    # info_hash:            urlencoded 20 byte sha1 hash
    # peer id:              urlencoded 20 byte string
    # port:                 usually between 6881-6889,the port to connect to
    # total uploaded:       in bytes, as base 10 ascii
    # total downloaded:     in bytes, as base 10 ascii
    # total left:           in bytes, as base 10 ascii
    # compact:              indicates that our client accepts a compact response
    # no_peer_id:           ignored if compact is true, tells tracker to omit id's in peer list
    # event:                either started, completed, or stopped
    def __init__(self):
        pass

    #returns a response containing
    # failure reason:       a failure reason if unsuccessful
    # interval:             the number of seconds to wait between requests to this tracker
    # min_interval:         the minimum allowed announce interval
    # tracker_id:           string that should be sent back on subsequent announcements, should be stored
    # complete:             number of peers with the entire file (seeders)
    # incomplete:           number of peers with incomplete file (leechers)
    # peers:                a dictionary holding a peer id, ip, port. this part can be sent in binary orin dictionary form
    def get_response(self):
        pass

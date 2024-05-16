class Tracker:
    #requires:
    # - an announce_url     (the base url to reach this tracker)
    # - an info_hash        (urlencoded 20 byte sha1 hash)
    # - a peer id           (urlencoded 20 byte string)
    # - a port              (usually between 6881-6889,the port to connect to)
    # - total uploaded      (in bytes, as base 10 ascii)
    # - total downloaded    (in bytes, as base 10 ascii)
    # - total left          (in bytes, as base 10 ascii)
    # - compact             (indicates that our client accepts a compact response)
    # - no_peer_id          (ignored if compact is true, tells tracker to omit id's in peer list)
    # - event               (either started, completed, or stopped)
    def __init__(self):
        pass

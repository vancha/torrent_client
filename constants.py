from enum import Enum

MIN_PEERS   = 10
PEER_ID     = "thurmanmermanddddddd"

class MessageType(Enum):
    KEEPALIVE = -1  # Special case (no ID, length=0)
    CHOKE = 0
    UNCHOKE = 1
    INTERESTED = 2
    NOTINTERESTED = 3
    HAVE = 4
    BITFIELD = 5
    REQUEST = 6
    PIECE = 7
    CANCEL = 8
    PORT = 9

MESSAGES_WITHOUT_PAYLOAD    = [MessageType.KEEPALIVE, MessageType.CHOKE, MessageType.UNCHOKE, MessageType.INTERESTED, MessageType.NOTINTERESTED]
MESSAGES_WITHOUT_ID         = [MessageType.KEEPALIVE]

#constants related to generating a handshake
PSTR = b"BitTorrent protocol"
PSTRLEN = bytes([len(PSTR)])
RESERVED_BYTES = bytearray(8)

SUBPIECE_SIZE = 2**14

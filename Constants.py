
PEER_ID = "thurmanmermanddddddd"


class MessageType(Enum):
    KEEPALIVE = -1  # Special case (no ID, length=0)
    CHOKE = 0
    UNCHOKE = 1
    INTERESTED = 2
    NOTINTERESTED = 3
    HAVE = 4
    REQUEST = 6
    PIECE = 7
    CANCEL = 8
    PORT = 9

MESSAGES_WITHOUT_PAYLOAD    = [MessageType.KEEPALIVE, MessageType.CHOKE, MessageType.UNCHOKE, MessageType.INTERESTED, MessageType.NOTINTERESTED]
MESSAGES_WITHOUT_ID         = [MessageType.KEEPALIVE]

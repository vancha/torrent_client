from constants import MessageType, MESSAGES_WITHOUT_ID, MESSAGES_WITHOUT_PAYLOAD

class Message:
    '''
        Creates a new message
        Defaults to a "keepalive" message if no id and payload are provided
        This message can be generated from raw bytes, and turned in to one, for sending and receiving over the network

    '''
    def __init__(self, length_prefix, message_id=-1, message_payload=None):
        self.length_prefix = length_prefix

        #if no prefix, then message is a keepalive message
        self.message_id = message_id
        self.message_payload = message_payload


    #converts the message to bytes for sending over network
    def to_bytes(self):
        length_prefix   = self.length_prefix.to_bytes(4, byteorder='big')
        if not self.has_id():
            return length_prefix

        message_id      = self.message_id.to_bytes(1, byteorder='big')

        if not self.has_payload():
            return length_prefix + message_id

        #payload is probably still "as bytes", but if this breaks it might not be
        return length_prefix + message_id + self.message_payload

    def get_type(self):
        if not self.length_prefix:
            return MessageType(-1)
        else:
            return MessageType(self.message_id)

    def has_payload(self):
        return MessageType(self.message_id) in MESSAGES_WITHOUT_PAYLOAD

    def get_payload(self):
        print(f"requesting payload of message of type {MessageType(self.message_id)}")
        return self.message_payload

    def has_id(self):
        return MessageType(self.message_id) in MESSAGES_WITHOUT_ID

    #will only return something if message is a have message
    def get_piece_index(self):
        return None

    #Turns raw network bytes in to a message
    @staticmethod
    def from_bytes( raw_bytes ):
        # first get the length prefix, which is a 4-byte big-endian value
        length_prefix = int.from_bytes(raw_bytes[0:4], "big")

        if length_prefix == 0:
            return Message.create_keepalive_message()

        message_id = raw_bytes[4]
        if length_prefix == 1:
            return Message(length_prefix, message_id)

        payload  = raw_bytes[5:]
        if message_id == 4:
            print(f"created have message with payload: {payload}")
        return Message(length_prefix, message_id, payload)

    # convenience functions follow

    @staticmethod
    def create_keepalive_message():
        return Message(0,-1)

    @staticmethod
    def create_choke_message():
        return Message(1,0)

    @staticmethod
    def create_unchoke_message():
        return Message(1,1)

    @staticmethod
    def create_interested_message():
        return Message(1,2)

    @staticmethod
    def create_notinterested_message():
        return Message(1,3)
    
    @staticmethod
    def create_request_message(index, begin, length):
        index = index.to_bytes(4, byteorder='big')
        begin = begin.to_bytes(4, byteorder='big')
        length = length.to_bytes(4, byteorder='big')
        payload = index+begin+length

        return Message(13, 6, payload)

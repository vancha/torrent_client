from ipaddress import ip_address, IPv4Address
import socket
from struct import unpack


def is_ipv4(ip: str):
    if type(ip_address(ip)) is IPv4Address:
        return True
    else:
        return False


message_ids = {
    "choke": 0,
    "unchoke": 1,
    "interested": 2,
    "not interested": 3,
    "have": 4,
    "bitfield": 5,
    "request": 6,
    "piece": 7,
    "cancel": 8,
    "port": 9,
}

"""
This represents a peer in the torrent network.
"""


class Peer:
    """
    takes three arguments:
        - client_id, which is the (unique) id of the client we use to connect to the peer
        - ip, the ip address of the peer we want to connect to
        - port, the port we need to connect to
        - mif, the metainfo file object that lets us get the info_hash
    """

    def __init__(self, client_id, ip, port, mif):
        self.client_id = client_id
        self.ip = ip
        self.port = port
        self.info_hash = mif.get_info_hash_bytes()

        # also set the initial state of this peer
        self.am_choking = True
        self.am_interested = False
        self.peer_choking = True
        self.peer_interested = False

    """
    Performs the handshake, if this returns False, the connection with the peer failed
    """

    def secret_handshake(self):
        pstr = b"BitTorrent protocol"
        pstrlen = bytes([len(pstr)])
        reserved = bytearray(8)

        # this makes a bytearray in the format of a torrent handshake
        handshake = (
            pstrlen + pstr + reserved + self.info_hash + self.client_id.encode("utf-8")
        )

        try:
            self.socket.sendall(handshake)

            # receive their response, this should look just like our handshake!
            shake_response = self.socket.recv(68)

            # to verify this repsonse is valid, compare their info hash with ours
            start_idx = len(pstrlen) + len(pstr) + len(reserved)
            end_idx = start_idx + len(self.info_hash)
            their_hash = shake_response[start_idx:end_idx]

            # if they don't match, we should drop the connection
            if not their_hash == self.info_hash:
                # alright close the socket T.T we failed
                return Fale
            # if they do, we are succesfully connected!
            else:
                return True
        except Exception as e:
            print(f"could not handshake peer because of {e}")

    # get a message from the socket, and parse it
    # a message starts with a 4 byte length prefix
    # followed by an id that corresponds to the type of message
    # whatever is left of the message is part of the payload
    def receive_message(self):
        print("waiting for message from peer")
        # first get the length prefix, which is a 4-byte big-endian value
        socket_data = self.socket.recv(4)
        length_prefix = int.from_bytes(socket_data, "big")

        # then receive exactly that many bytes
        message = self.socket.recv(length_prefix)

        # then get the message id, a single decimal byte
        message_id = message[0]

        # the payload should be whatevers left in the response, can be nothing
        message_payload = message[1:]

        message = {
            "length_prefix": length_prefix,
            "id": message_id,
            "payload": message_payload,
        }
        return message

    def initiate_peer_wire_protocol(self):
        # do the thing
        try:
            while True:
                # continually parse messages
                message = self.receive_message()
                if message["length_prefix"] == 0:
                    print("received keepalive message")
                    continue
                if message["id"] == message_ids["choke"]:
                    print("received choke message")
                    self.peer_choking = True
                elif message["id"] == message_ids["unchoke"]:
                    print("received unchoke message")
                    self.peer_choking = False
                elif message["id"] == message_ids["interested"]:
                    print("received interested message")
                    self.peer_interested = True
                elif message["id"] == message_ids["not intrested"]:
                    self.peer_interested = False
                    print("received not interested message")
                elif message["id"] == message_ids["have"]:
                    print("received have message")
                elif message["id"] == message_ids["bitfield"]:
                    print("received bitfield message")
                elif message["id"] == message_ids["request"]:
                    print("received request message")
                elif message["id"] == message_ids["piece"]:
                    print("received piece message")
                elif message["id"] == message_ids["cancel"]:
                    print("received cancel message")
                elif message["id"] == message_ids["port"]:
                    print("received port message")
                else:
                    print("received message without id")

        except KeyboardInterrupt:
            print(f"Keyboardinterrupt received, quit listening")

    def connect(self):
        # maybe focus on ipv4 for now, forget v6
        if is_ipv4(self.ip):
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.ip, self.port))
                if self.secret_handshake():
                    print("handshake performed, connected to peer")
                    self.initiate_peer_wire_protocol()
                print("done listening, closing socket")
                self.socket.close()
            except Exception as e:
                print(f"Error conecting to peer: {e}")
        # else:
        #    print(f'will not connect, is ipv6')

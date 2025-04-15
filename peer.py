from ipaddress import ip_address, IPv4Address
import socket
import struct
from struct import unpack
import time

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

messages = {
    message_ids["choke"]        : b"\x00\x00\x00\x01\x00",
    message_ids["unchoke"]      : b"\x00\x00\x00\x01\x01",
    message_ids["interested"]   : b"\x00\x00\x00\x01\x02",
    message_ids["request"]      : b"\x00\x00\x00\x0d\x06",
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
        self.mif = mif
        #self.info_hash = mif.get_info_hash_bytes()

        # also set the initial state of this peer
        self.am_choking = True
        self.am_interested = False
        self.peer_choking = True
        self.peer_interested = False

    """
    Performs the handshake, if this returns False, the connection with the peer failed
    """
    def send_message(self, message):
        self.socket.send(message)


    def secret_handshake(self):
        pstr = b"BitTorrent protocol"
        pstrlen = bytes([len(pstr)])
        reserved = bytearray(8)

        # this makes a bytearray in the format of a torrent handshake
        handshake = (
            pstrlen + pstr + reserved + self.mif.get_info_hash_bytes() + self.client_id.encode("utf-8")
        )

        try:
            self.socket.sendall(handshake)

            # receive their response, this should look just like our handshake!
            shake_response = self.socket.recv(68)

            # to verify this repsonse is valid, compare their info hash with ours
            start_idx = len(pstrlen) + len(pstr) + len(reserved)
            end_idx = start_idx + len(self.mif.get_info_hash_bytes())#self.info_hash)
            their_hash = shake_response[start_idx:end_idx]

            # if they don't match, we should drop the connection
            if not their_hash == self.mif.get_info_hash_bytes():#self.info_hash:
                # alright close the socket T.T we failed
                return False
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
        # first get the length prefix, which is a 4-byte big-endian value
        socket_data = self.socket.recv(4)
        length_prefix = int.from_bytes(socket_data, "big")
        if length_prefix == 0:
            return { "length_prefix": 0, "id": None, "payload": None}
        # then receive exactly that many bytes
        message = self.socket.recv(length_prefix)

        #now we will have to do some mandatory error handling or end up confused for over a year checking all possible torrent
        #resources and wonder wtf went wrong only to find out that http://www.kristenwidman.com/blog/71/how-to-write-a-bittorrent-client-part-2/ mentions that there is no guarantee that messages will come in discrete packets containing only a single entire message and implementation does not account for that and it fails and everything is horrible pls note this
        incomplete_message = False
        while  len(message) < length_prefix:
            incomplete_message = True
            remaining_bytes = length_prefix - len(message)
            message += self.socket.recv(remaining_bytes)

            #exit(f"Error, we did not receive as many bytes as requested!: {message}")
        # then get the message id, a single decimal byte

        if len(message) < 1:
            exit(f"Error, cannot get payload of this message!")
        message_id = message[0]

        # the payload should be whatevers left in the response, can be nothing
        message_payload = message[1:]


        message = {
            "length_prefix": length_prefix,
            "id": message_id,
            "payload": message_payload,
        }
        return message

    def all_subpieces_received(self, piece_index):
        for part in range(16):
            #we will *try* to load the part from the disk
            try:
                f = open(f'pieces/piece{piece_index}part{part}.part','rb')
            #but if we fail, that means this piece is incomplete, we cannot verify
            except FileNotFoundError:
                return False
        return True
                                
    def initiate_peer_wire_protocol(self):
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
                    time.sleep(.01)
                    self.send_message(messages[message_ids["interested"]])
                    time.sleep(.01)
                    self.send_message(messages[message_ids["unchoke"]])
                elif message["id"] == message_ids["interested"]:
                    print("received interested message")
                    self.peer_interested = True
                elif message["id"] == message_ids["not interested"]:
                    self.peer_interested = False
                    print("received not interested message")
                elif message["id"] == message_ids["have"]:
                    piece_index = struct.unpack('!I', message["payload"])
                    print(f"received have message for index {piece_index}")
                    time.sleep(.01)
                    #lets define a request message in response to this have message:
                    #we will request the same piece that the peer tells us it has
                    index   = (piece_index[0]).to_bytes(4, byteorder='big')#message["payload"]
                    #some math is required here. The torrent file says that the length of each block is 262144 bytes
                    #we can only request a maximum of 2 ** 14 bytes at a time according to the specification (16384 bytes)
                    #that means that we need to send at least 16 requests to get the entire block
                    #starting at index 0
                    for idx in range(16):
                        begin   = ( idx * (2**14)).to_bytes(4, byteorder='big') #b"\x00\x00\x00\x00"
                        #request part of a block that's 2 ** 14 bytes long
                        length  = (2**14).to_bytes(4, byteorder='big')
                        #to get this whole block, we need 16 of the following messages, that all have a different value for begin
                        have_message = messages[message_ids["request"]] + index + begin + length
                        print(f'sent request message: {have_message}')
                        self.send_message(have_message)
                        #time.sleep(.01)
                elif message["id"] == message_ids["bitfield"]:
                    print("received bitfield message")
                elif message["id"] == message_ids["request"]:
                    print("received request message")
                elif message["id"] == message_ids["piece"]:
                    piece_index = struct.unpack('!I', message["payload"][0:4])[0]
                    begin = struct.unpack('!I', message["payload"][4:8])[0]
                    block = message["payload"][8:]
                    part = begin // 2 ** 14
                    with open(f"./pieces/piece{piece_index}part{part}.part", "wb") as binary_file:
                        # Write bytes to file
                        binary_file.write(block)
                    if self.all_subpieces_received(piece_index):
                        if self.mif.verify_piece(piece_index):
                            self.set_piece_as_verified(piece_index)

                elif message["id"] == message_ids["cancel"]:
                    print("received cancel message")
                elif message["id"] == message_ids["port"]:
                    print("received port message")
                else:
                    print("received message without id")

        except KeyboardInterrupt:
            print(f"Keyboardinterrupt received, quit listening")

    #adds a piece_nr to the json file that stores all completed pieces
    #can remove the piece and parts files, write the contents of the full piece to the output file
    def set_piece_as_verified(self, piece_nr):
        print(f"Completely downloaded piece {piece_nr}, writing it to output file now!")

    def connect(self):
        try:
            #should handle both ipv4 and ipv6
            self.socket = socket.create_connection((self.ip, self.port))
            if self.secret_handshake():
                self.initiate_peer_wire_protocol()
            self.socket.close()
        except Exception as e:
            print(f"Error conecting to peer: {e}")


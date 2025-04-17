from ipaddress import ip_address, IPv4Address
import socket
import struct
import hashlib
from struct import unpack
import time
import os

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

        # also set the initial state of this peer
        self.am_choking = True
        self.am_interested = False
        self.peer_choking = True
        self.peer_interested = False
        
        #to decide if we need to send a keepalive message, track when this peer last received one of our messages
        self.last_contacted = None
        #these are the pieces that have succesfully been downloaded
        self.completed_pieces = []
        #these are the pieces that are available to download
        self.bitfield = None

    """
    Performs the handshake, if this returns False, the connection with the peer failed
    """
    def send_message(self, message):
        self.socket.send(message)

    def secret_handshake_successful(self):
        pstr = b"BitTorrent protocol"
        pstrlen = bytes([len(pstr)])
        reserved = bytearray(8)

        # this makes a bytearray in the format of a torrent handshake
        handshake = (
            pstrlen + pstr + reserved + self.mif.get_info_hash_bytes() + self.client_id.encode("utf-8")
        )

        try:
            self.socket.sendall(handshake)
            handshake_response = self.socket.recv(68)

            # to verify this response is valid, compare their info hash with ours
            start_idx = len(pstrlen) + len(pstr) + len(reserved)
            end_idx = start_idx + len(self.mif.get_info_hash_bytes())#self.info_hash)
            their_hash = handshake_response[start_idx:end_idx]

            # if they don't match, we should drop the connection
            if not their_hash == self.mif.get_info_hash_bytes():#self.info_hash:
                return False
            # if they do, we are succesfully connected!
            else:
                return True
        except Exception as e:
            print(f"could not handshake peer because of {e}")

    # receive message from the remote peer
    def receive_message(self):
        length_prefix = int.from_bytes(self.socket.recv(4), "big")
        message_bytes = self.socket.recv(length_prefix)
        while  len(message) < length_prefix:
            remaining_bytes = length_prefix - len(message_bytes)
            message_bytes += self.socket.recv(remaining_bytes)

        return  Message.from_bytes(message_bytes)
        

    def all_subpieces_received(self, piece_index):
        for part in range(16):
            try:
                f = open(f'pieces/piece{piece_index}part{part}.part','rb')
            #but if we fail, that means this piece is incomplete, we cannot verify
            except FileNotFoundError:
                return False
        return True
        
    #deletes the piece from disk, it's bad >:(
    def delete_piece(self, piece_index):
        for part in range(16):
            try:
                file = f'pieces/piece{piece_index}part{part}.part'
                os.remove(file)
            except Exception as e:
                print(f"failed deleting piece {e}")
                #we don't care about exception, if a piece is missing we won't be able to find it
                pass
    
    #takes all the parts, combines them, and moves them to the completed folder
    def move_piece(self, piece_index):
        sub_pieces = []
        for part in range(16):
            f = open(f'pieces/piece{piece_index}part{part}.part','rb')
            sub_pieces.append(f.read())  
        complete_piece = b''.join(sub_pieces)
        with open(f"./completed_pieces/{piece_index}.piece", "wb") as binary_file:
            # Write bytes to file
            binary_file.write(complete_piece)
        self.delete_piece(piece_index)
        print(f"piece moved")
    
    
    #combines the subpieces into one piece, moves it to the "finished_pieces" folder
    def verify_piece(self, piece_index):
        sub_pieces = []
        for part in range(16):
            try:
                f = open(f'pieces/piece{piece_index}part{part}.part','rb')
                sub_pieces.append(f.read())
            except FileNotFoundError:
                #should not happen, this should only be called if all subpieces are present
                self.delete_piece(piece_index)
                return
        
        complete_piece = b''.join(sub_pieces)
        piece_hash = hashlib.sha1(complete_piece)
        digest = piece_hash.digest()
        #verify
        if self.mif.piece_hash_in_bytes(piece_index) == digest:
            self.move_piece(piece_index)
            self.completed_pieces.append(piece_index)
        else:
            self.delete_piece(piece_index)
    
    def handle_keepalive_message(self):
        print(f"received keepalive message")
        
    def handle_choke_message(self):
        self.peer_choking = True
    
    def handle_unchoke_message(self):
        print("received unchoke message")
        self.peer_choking = False
        time.sleep(.01)
        self.send_message(messages[message_ids["interested"]])
        time.sleep(.01)
        self.send_message(messages[message_ids["unchoke"]])
    
    def handle_interested_message(self):
        print("received interested message")
        self.peer_interested = True
    
    def handle_notinterested_message(self):
        self.peer_interested = False
        print("received not interested message")
    
    def handle_have_message(self, message):
        piece_index = struct.unpack('!I', message["payload"])
        time.sleep(.001)
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
            self.send_message(have_message)
            #time.sleep(.01)
            
    def handle_bitfield_message(self, message):
        print(f"received le bitfield")
    
    def handle_request_message(self):
        print("received request message")
    
    def handle_piece_message(self, message):
        piece_index = struct.unpack('!I', message["payload"][0:4])[0]
        begin = struct.unpack('!I', message["payload"][4:8])[0]
        block = message["payload"][8:]
        part = begin // 2 ** 14
        with open(f"./pieces/piece{piece_index}part{part}.part", "wb") as binary_file:
            binary_file.write(block)
        if self.all_subpieces_received(piece_index):
            self.verify_piece(piece_index)

    def handle_cancel_message(self):
         print("received cancel message")
    
    def handle_port_message(self, message):
        print("received port message")
        
    def handle_unknown_message(self, message):
        exit("SOEMTHING WENT WRONG HANDLING AN UNKNOWN MESSAGE")
    
    def parse_message(self, message):
        match message.message_type:
            case MessageType.KEEPALIVE:
                self.handle_keepalive_message()
            case MessageType.CHOKE:
                self.handle_choke_message()
            case MessageType.UNCHOKE:
                self.handle_unchoke_message()
            case  MessageType.INTERESTED:
                self.handle_interested_message()
            case  MessageType.NOTINTERESTED:
                self.handle_notinterested_message()
            case  MessageType.HAVE:
                self.handle_have_message(message)
            case  MessageType.BITFIELD:
                self.handle_bitfield_message(message)
            case  MessageType.REQUEST:
                self.handle_request_message()
            case  MessageType.PIECE:
                self.handle_piece_message(message)
            case  MessageType.CANCEL:
                self.handle_cancel_message()
            case  MessageType.PORT:
                self.handle_port_message(message)
            case _:
                self.handle_unknown_message(message)
        
    def step(self):
        #receive message
        message = self.receive_message()
        #parse_message
        self.parse_message(message)

    #sends a keepalive if required
    def maintain_connection(self):
        print(f"maintain_connection not implemented yet")

    def connect(self):
        try:
            #should handle both ipv4 and ipv6
            self.socket = socket.create_connection((self.ip, self.port))
            if self.secret_handshake_successful():
                self.last_contacted = datetime.now()
            return True
        except Exception as e:
            return False


    def is_connected(self):
        pass
        
    

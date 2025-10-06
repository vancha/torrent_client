import socket
import struct
import hashlib
from struct import unpack
import time
import os
from message import Message
from constants import MessageType, PSTR, PSTRLEN, RESERVED_BYTES, SUBPIECE_SIZE

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
        
        #should be true when connected
        self.active = False

        #to decide if we need to send a keepalive message, track when this peer last received one of our messages
        self.last_contacted = None
        #these are the pieces that have succesfully been downloaded
        self.completed_pieces = set()
        #these are the pieces that are available to download
        self.bitfield = set()


    def __eq__(self, other):
        return isinstance(other, Peer) and self.ip == other.ip and self.port == other.port

    def __hash__(self):
        return hash((self.ip, self.port))


    """
    Performs the handshake, if this returns False, the connection with the peer failed
    """
    def send_message(self, message):
        try:
            byte_message = message.to_bytes()
            self.socket.send(byte_message)
        except BrokenPipeError:
            print(f"Peer disconnected")
            self.active = False

    def send_request_message(self, piece_index):
        index   = (piece_index).to_bytes(4, byteorder='big')

        for subpiece_index in range(16):
            begin   = subpiece_index * SUBPIECE_SIZE
            length  = SUBPIECE_SIZE
            request_message = Message.create_request_message(piece_index, begin, length)
            time.sleep(0.01)
            self.send_message(request_message)

    #checks the bitfield to see which pieces are available and returns them
    def get_available_pieces(self):
        return list(self.bitfield)

    def remove_available_piece(self, piece_index):
        self.bitfield.remove(piece_index)

    def get_completed_pieces(self):
        return list(self.completed_pieces)

    def clear_completed_pieces(self):
        self.completed_pieces = set()

    def generate_handshake(self):
        return PSTRLEN + PSTR + RESERVED_BYTES + self.mif.get_info_hash_bytes() + self.client_id.encode("utf-8")

    def secret_handshake_successful(self):
        # this makes a bytearray in the format of a torrent handshake
        handshake = self.generate_handshake()
        try:
            self.socket.sendall(handshake)
            handshake_response = self.socket.recv(68)
            hash_start_idx = len(PSTRLEN) + len(PSTR) + len(RESERVED_BYTES)
            hash_end_idx = hash_start_idx + len(self.mif.get_info_hash_bytes())#self.info_hash)
            their_hash = handshake_response[hash_start_idx:hash_end_idx]

            # if they don't match, we should drop the connection
            return their_hash == self.mif.get_info_hash_bytes()
        except Exception as e:
            return False

    # receive message from the remote peer
    def receive_message(self):
        try:
            prefix_bytes = self.socket.recv(4)
            #if prefix_bytes == b'':
            #    print(f"PEER DISCONNECTED? ({self.ip})")
            #    self.active = False
            #    return Message.create_keepalive_message()
            time.sleep(0.01)
            length_prefix = int.from_bytes(prefix_bytes, "big")
            message_bytes = self.socket.recv(length_prefix)
            while  len(message_bytes) < length_prefix:
                remaining_bytes = length_prefix - len(message_bytes)
                message_bytes += self.socket.recv(remaining_bytes)
            all_bytes = prefix_bytes + message_bytes
            return  Message.from_bytes(all_bytes)
        except socket.timeout:
            print(f"SOCKET TIMED OUT")

    def all_subpieces_received(self, piece_index):
        for part in range(16):
            try:
                f = open(f'pieces/piece{piece_index}part{part}.part','rb')
            #but if we fail, that means this piece is incomplete, we cannot verify
            except FileNotFoundError:
                return False
        return True
    
    def handle_keepalive_message(self):
        print(f"received keepalive message")
        
    def handle_choke_message(self):
        print(f"received choke message")
        self.peer_choking = True
    
    def handle_unchoke_message(self):
        print("received unchoke message")
        self.peer_choking = False
        time.sleep(.01)
        self.send_message(Message.create_interested_message())
        time.sleep(.01)
        self.send_message(Message.create_unchoke_message())
    
    def handle_interested_message(self):
        print("received interested message")
        self.peer_interested = True
    
    def handle_notinterested_message(self):
        self.peer_interested = False
        print("received not interested message")
    
    #stores the piece in the bitfield
    def handle_have_message(self, message):
        piece_index = struct.unpack('!I', message.get_payload())[0]
        self.bitfield.add(piece_index)

    def handle_bitfield_message(self, message):
        print(f"received le bitfield: {message.payload}")
    
    def handle_request_message(self):
        print("received request message")
    
    def handle_piece_message(self, message):
        #print(f"AAAAAAAAAAAAAAAAAAA")
        begin = struct.unpack('!I', message.get_payload()[4:8])[0]
        block = message.get_payload()[8:]
        part = begin // SUBPIECE_SIZE
        with open(f"./pieces/piece{message.get_piece_index()}part{part}.part", "wb") as binary_file:
            binary_file.write(block)
        if self.all_subpieces_received(message.get_piece_index()):
            self.completed_pieces.add(message.get_piece_index())

    def handle_cancel_message(self):
         print("received cancel message")
    
    def handle_port_message(self, message):
        print("received port message")
        
    def handle_unknown_message(self, message):
        exit("something went wrong handling an unknown message")
    
    def parse_message(self, message):
        match message.get_type():
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
        try:
            message = self.receive_message()
        except TimeoutError:
            message = None
        if message:
            print(f"received message")
            self.parse_message(message)

    def connect(self):
        try:
            self.socket = socket.create_connection((self.ip, self.port))
            self.socket.settimeout(.5)
            print(f"attempting to connect to ({self.ip}, {self.port})")
            if self.secret_handshake_successful():
                self.active = True
                print(f"shook hands with peer")
                return True
            print(f'failed connecting to peer')
            return False
        except Exception as e:
            return False

    def is_active(self):
        return self.active

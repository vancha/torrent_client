from ipaddress import ip_address, IPv4Address
import socket
from struct import unpack

def is_ipv4(ip: str):
    if type(ip_address(ip)) is IPv4Address:
        return True
    else:
        return False

class Peer:
    def __init__(self, client_id, ip, port, mif):
        self.client_id  = client_id
        self.ip         = ip
        self.port       = port
        self.info_hash  = mif.get_info_hash_bytes()
    
    #return true on success, false on failure
    def secret_handshake(self):
        pstr        = b"BitTorrent protocol"
        pstrlen     = bytes([len(pstr)])
        reserved    = bytearray(8)
        
        #it's called peer id, but it's actually the id of our own client
        peer_id     = self.client_id.encode('utf-8')

        #this makes a bytearray in the format of a torrent handshake
        handshake = pstrlen + pstr + reserved + self.info_hash + peer_id

        try:
            #send our handshake
            self.socket.sendall(handshake)
        
            #receive their response, this should look just like our handshake!
            shake_response      = self.socket.recv(68)
            
            #to verify this repsonse is valid, compare their info hash with ours
            start_idx           = len(pstrlen)+len(pstr)+len(reserved)
            end_idx             = start_idx + len(self.info_hash)
            their_hash          = shake_response[start_idx:end_idx]
            
            #if they don't match, we should drop the connection
            if not their_hash == self.info_hash:
                #alright close the socket T.T we failed
                return Fale
            #if they do, we are succesfully connected!
            else:
                return True 
        except Exception as e:
            print(f'could not handshake peer because of {e}')



    def connect(self):
        #maybe focus on ipv4 for now, forget v6
        if is_ipv4(self.ip):
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.ip, self.port))
                print(f'connected to {self.ip}, now its time to perform the secret handshake')
                if not self.secret_handshake():
                    print('Handshake failed, closing socket')
                    self.socket.close()
                else:
                    print('hand shook. we done diddly did it')
            except Exception as e:
                print(f'Error conecting to peer: {e}')
            print('done with the connection, i got nothing')
        else:
            print(f'will not connect, is ipv6')

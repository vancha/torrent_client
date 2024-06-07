#used to see what the next byte in the torrent file is
from more_itertools import peekable

'''
A python class that can decode a torrent file
Call bdecoder.decode( torrent_file_location )  to use it.
'''
class bdecoder:
    '''
    Assumes the next(byte_iterator) returns the start of a string
    Moves forward in the iterator and returns the string
    '''
    def decode_byte_string(byte_iterator):
        #byte strings are length prefixed, get the length first
        length = ''

        while chr(byte_iterator.peek()).isnumeric():
            length += chr(next(byte_iterator))

        #byte strings are suffixed with a :, skip over that before returning
        next(byte_iterator)
        result = []
        for _ in range(int(length)):
            result.append(next(byte_iterator))
        return bytes(bytearray(result))

    '''
    Assumes the next(byte_iterator) returns the start of an integer
    Moves forward in the iterator and returns the integer
    '''
    def decode_integer(byte_iterator):
        #skip over the 'i'
        next(byte_iterator)
        values = ''

        while not chr(byte_iterator.peek()) == 'e':#.isnumeric():
            values += chr(next(byte_iterator))

        #skip over the 'e'
        next(byte_iterator)
        return int(values)

    '''
    Assumes the next(byte_iterator) returns the start of a list
    Moves forward in the iterator and returns the list
    '''
    def decode_list( byte_iterator):
        #skip over the 'l'
        next(byte_iterator)

        result = []
        while not chr(byte_iterator.peek()) == 'e':
            result.append(bdecoder.decode_next(byte_iterator))

        #skip over the 'e'
        next(byte_iterator)
        return result

    '''
    Deduces the type of the next object in the iterator and returns it
    '''
    def decode_next(byte_iterator):
        val = chr(byte_iterator.peek())

        if val == 'd':
            return bdecoder.decode_dict(byte_iterator)
        elif val == 'l':
            return bdecoder.decode_list(byte_iterator)
        elif val == 'i':
            return bdecoder.decode_integer(byte_iterator)
        else:
            return bdecoder.decode_byte_string(byte_iterator)

    '''
    Assumes the next(byte_iterator) returns the start of a dictionary
    Moves forward in the iterator and returns the dictionary
    '''
    def decode_dict(byte_iterator):
        #skip over the initial 'd'
        next(byte_iterator)

        result  = OrderedDict()
        while not chr(byte_iterator.peek()) == "e":
            field_name =  bdecoder.decode_byte_string(byte_iterator)
            field_value = bdecoder.decode_next(byte_iterator)
            result[field_name] = field_value

        #skip over the 'e'
        next(byte_iterator)
        return result

    '''
    Takes the torrent file, and attempts to parse it.
    returns the parsed value
    '''
    def decode_from_file(torrent_file):
        file  = open(torrent_file, "rb").read()
        return bdecoder.decode(file)
        #byte_iterator  = peekable(file)
        #return bdecoder.decode_next(byte_iterator)

    def decode(byte_object):
        byte_iterator = peekable(byte_object)
        return bdecoder.decode_next(byte_iterator)

    '''
    this is supposed to encode an object:
    '''
    def encode(obj):
        return bdecoder.encode_next(obj)

    def encode_next(obj):
        #print(f'received object of type {type(obj)}')
        t = type(obj)
        if t in [dict, OrderedDict]:
            return bdecoder.encode_dict(obj)
        elif t == bytes:
            return bdecoder.encode_byte_string(obj)
        elif t == list:
            return bdecoder.encode_list(obj)
        elif t == int:
            return bdecoder.encode_int(obj)
        else:
            raise Error('error, wrong type')

    def encode_int(obj):
        val = b"i" +  bytes(str(obj),'utf-8') + b"e"
        return val

    def encode_list(obj):
        encoded_list = bytearray(b"l")
        for element in obj:
            encoded_list += bdecoder.encode_next(element)
        encoded_list += b"e"
        return encoded_list

    def encode_byte_string(key):
        rawlen = len(key)
        return str(rawlen).encode('utf-8') + b":" +  key

    def encode_dict(obj):
        encoded_dict = bytearray(b"d")
        for key in obj.keys():
            encoded_dict += bdecoder.encode_next(key)
            encoded_dict += bdecoder.encode_next(obj[key])
        encoded_dict += b"e"
        return encoded_dict

'''
Example usage:
    decoded_file = bdecoder.decode("./example.torrent")
    print(decoded_file["info"])
'''

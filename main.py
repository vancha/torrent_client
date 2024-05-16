from more_itertools import peekable

class bdecoder:

    def decode_byte_string(self, byte_iterator):
        #byte strings are prefixed with a length
        length = ''
        
        while chr(byte_iterator.peek()).isnumeric():
            length += chr(next(byte_iterator))
        
        #also skip the double colon that's present after every string length
        next(byte_iterator)
        value = ""
        for _ in range(int(length)):
            value += chr(next(byte_iterator))
        return value

    def decode_integer(self, byte_iterator):
        #skip over the 'i'
        next(byte_iterator)
        values = ''
         
        while not chr(byte_iterator.peek()) == 'e':#.isnumeric():
            values += chr(next(byte_iterator))
        
        #skip over the 'e'
        next(byte_iterator)
        return int(values)

    def decode_list(self, byte_iterator):
        #skip over the 'l'
        next(byte_iterator)

        result = []
        while not chr(byte_iterator.peek()) == 'e':
            result.append(self.decode_next(byte_iterator))

        #skip over the 'e'
        next(byte_iterator)
        return result

    def decode_next(self, byte_iterator):
        val = chr(byte_iterator.peek())

        if val == 'd':
            return self.decode_dict(byte_iterator)
        elif val == 'l':
            return self.decode_list(byte_iterator)
        elif val == 'i':
            return self.decode_integer(byte_iterator)
        else:
            return self.decode_byte_string(byte_iterator)

    def decode_dict(self, byte_iterator):
        #skip over the initial 'd'
        next(byte_iterator)

        result  = {}
        while not chr(byte_iterator.peek()) == "e":
            field_name =  self.decode_byte_string(byte_iterator)
            field_value = self.decode_next(byte_iterator)
            result[field_name] = field_value

        #skip over the 'e'
        next(byte_iterator)
        return result

    
    def decode(self, torrent_file):
        file  = open(torrent_file, "rb").read()
        byte_iterator  = peekable(file)
        results = []
        return self.decode_next(byte_iterator)
    
x = bdecoder()

decoded_dict = x.decode("./ubuntu.torrent")
print(decoded_dict["announce-list"])

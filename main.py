from more_itertools import peekable

class bdecoder:

    def decode_byte_string(self, byte_iterator):
        #byte strings are prefixed with a length
        length = []
        
        while True:
            #get the whole number that represents the length
            if chr(byte_iterator.peek()).isnumeric():
                length.append(chr(byte_iterator.peek()))
                next(byte_iterator)
            else:
                #also skip the double colon that's present after every string length
                next(byte_iterator)
                break
        value = ""
        for _ in range(int(''.join(length))):
            value = value + chr(byte_iterator.peek())
            next(byte_iterator)
        print(f'decoded string: {value}')
        return value


    def decode_integer(self, byte_iterator):
        pass

    def decode_list(self, byte_iterator):
        result = []
        val = chr(byte_iterator.peek())
        while not val == 'e':
            result.append(self.decode_next(byte_iterator))
        next(byte_iterator)
        return result

    def decode_next(self, byte_iterator):
        val = chr(byte_iterator.peek())
        if val == 'd':
            next(byte_iterator)
            print('decoding dict because val is {val}')
            return self.decode_dict(byte_iterator)
        elif val == 'l':
            #pass by the initial l
            next(byte_iterator)
            print(f'decoding list because val is {val}')
            return self.decode_list(byte_iterator)
        elif val == 'i':
            print(f'decoding int because val is {val}')
            return self.decode_integer(byte_iterator)
        else:
            print(f'decoding byte string because val is {val}')
            return self.decode_byte_string(byte_iterator)

    def decode_dict(self, byte_iterator):
        result  = {}
        print('attempting to decode dict')
        val = chr(byte_iterator.peek())

        while not val == "e":
            field_name =  self.decode_byte_string(byte_iterator)
            print(f'field name: {field_name}')
            field_value = self.decode_next(byte_iterator)
            print(f'field value: {field_value}')
            result[field_name] = field_value
        next(byte_iterator)
        return result

    
    def decode(self, torrent_file):
        file  = open(torrent_file, "rb").read()
        byte_iterator  = peekable(file)
        results = []
        try:
            while True:
                results.append(self.decode_next(byte_iterator))
                '''
                #dictionary
                if chr(byte_iterator.peek()) == 'd':
                    #skip the 'd'
                    next(byte_iterator)
                    results.append(self.decode_dict(byte_iterator))
                    print(f"result: {results}")
                    break
                #integer
                elif chr(byte_iterator.peek()) == 'i':
                    results.append(self.decode_integer(byte_iterator))
                #list
                elif chr(byte_iterator.peek()) == 'l':
                    results.append(self.decode_list(byte_iterator))
                #bytestring
                else:
                    results.append(self.decode_byte_string(byte_iterator))
                break
                '''
        except:
            print('reached end of file')
            return results


x = bdecoder()

print(x.decode("./ubuntu.torrent"))

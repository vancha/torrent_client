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
        #skip over the 'i'
        next(byte_iterator)
        values = ''
         
        while chr(byte_iterator.peek()).isnumeric():
            val = chr(byte_iterator.next())
            print(f'adding {val} to int')
            values = values + val
        print(f'done parsing int')
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
        print(f'decoded list: {result}')
        return result

    def decode_next(self, byte_iterator):
        print(f'in decode_next')
        val = chr(byte_iterator.peek())
        if val == 'd':
            dct =  self.decode_dict(byte_iterator)
            print('decoding dict because val is {val}')
        elif val == 'l':
            lst = self.decode_list(byte_iterator)
            print(f'decoded list: {lst}')
            return lst
        elif val == 'i':
            integer = self.decode_integer(byte_iterator)
            print(f'decoded int:{integer}')
            return integer
        else:
            print(f'decoding byte string because val is {val}')
            return self.decode_byte_string(byte_iterator)

    def decode_dict(self, byte_iterator):
        #skip over the 'd'
        next(byte_iterator)
        result  = {}
        while not chr(byte_iterator.peek()) == "e":
            field_name =  self.decode_byte_string(byte_iterator)
            print(f'field name: {field_name}')
            field_value = self.decode_next(byte_iterator)
            print(f'field value: {field_value}')
            result[field_name] = field_value
        #skip over the 'e'
        next(byte_iterator)
        return result

    
    def decode(self, torrent_file):
        file  = open(torrent_file, "rb").read()
        byte_iterator  = peekable(file)
        results = []
        try:
            while True:
                results.append(self.decode_next(byte_iterator))
        except StopIteration:
            print('reached end of file')
            return results


x = bdecoder()

print(x.decode("./ubuntu.torrent"))

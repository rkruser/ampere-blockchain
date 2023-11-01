from functools import wraps
import struct
import warnings

# convention: types always end with ".X.Y" where X and Y and version and sub-version.
# Version specs by themselves are "X.Y" strings

ENDIAN_FORMAT_CHAR = '>' #big-endian

# "name": (struct format code, number of bytes, is_integer, is_signed, min_val, max_val)
FixedBuiltinNumericalTypeNames = {
    'uint_8': ('B', 1, True, False, 0, 2**8-1),
    'uint_16': ('H', 2, True, False, 0, 2**16-1),
    'uint_32': ('I', 4, True, False, 0, 2**32-1),
    'uint_64': ('Q', 8, True, False, 0, 2**64-1),
    'int_8': ('b', 1, True, True, -2**7, 2**7-1),
    'int_16': ('h', 2, True, True, -2**15, 2**15-1),
    'int_32': ('i', 4, True, True, -2**31, 2**31-1),
    'int_64': ('q', 8, True, True, -2**63, 2**63-1),
    'float_32': ('f', 4, False, True, None, None),
    'float_64': ('d', 8, False, True, None, None)
}
LengthBitNumberToStructFormat = {
    8: 'B',
    16: 'H',
    32: 'I',
    64: 'Q'
}

def isBuiltinType(type_name):
    if type_name in FixedBuiltinNumericalTypeNames:
        return True
    split_name = type_name.split('_')
    if len(split_name) == 3:
        prefix, rootname, length_info_bitnum = split_name
        if (prefix != 'variable') or (rootname not in ['string', 'bytes']) or (int(length_info_bitnum) not in LengthBitNumberToStructFormat):
            return False
        return True
    if len(split_name) == 2:
        rootname, bytenum = split_name
        bytenum = int(bytenum)
        if (rootname not in ['string', 'bytes']):
            return False
        return True
    return False

def isVariableLength(type_name):
    return type_name.startswith('variable')

class TypeRegistry:
    def __init__(self):
        self.types = {}

    def register_type(self, type_parser):
        self.types[type_parser.type_name()] = type_parser
        return type_parser
    
    def get_type(self, type_name):
        if type_name in self.types:
            return self.types[type_name]
        elif isBuiltinType(type_name):
            if isVariableLength(type_name):
                return self.register_type(VariableLengthBuiltinType(type_name))
            else:
                return self.register_type(FixedLengthBuiltinType(type_name))
        return self.types[type_name]

Types = TypeRegistry()


class TypeParser:
    def __init__(self, name, is_builtin):
        self.name = name
        self.builtin = is_builtin

    '''
    Return true if type is builtin (e.g., lowercase by convention). Return false if compound type.
    '''
    def is_builtin(self):
        return self.builtin
    
    def type_name(self):
        return self.name

    def byte_length(self, bytestream=None):
        raise NotImplementedError
    '''
    Takes a bytestream and returns a tuple of (success_flag, parsed_dictionary, remainder)
    '''
    def parse_bytes(bytestream):
        raise NotImplementedError

    '''
    Take a dictionary of values and serialize them into bytes, invoking the write_bytes method of any subparsers necessary
    '''
    def write_bytes(data_dictionary):
        raise NotImplementedError

    '''
    - Check that all ints are in the correct ranges
    - Check that all version constraints are met (e.g., parent version constrains allowed child versions)
    '''
    def validate_type(data_dictionary):
        raise NotImplementedError


def bytes_to_ascii(bytestream):
    return bytestream.decode('ascii')

def ascii_to_bytes(stringstream):
    return stringstream.encode('ascii')

def identity(bytestream):
    return bytestream

class FixedLengthBuiltinType(TypeParser):
    def __init__(self, name):
        super().__init__(name, True)
        self.encode_func = identity
        self.decode_func = identity
        self.is_string = False
        if name in FixedBuiltinNumericalTypeNames:
            self.is_number = True
            struct_format, num_bytes, is_integer, is_signed, min_val, max_val = FixedBuiltinNumericalTypeNames[name]
            self.struct_format = struct_format
            self.num_bytes = num_bytes
            self.is_integer = is_integer
            self.is_signed = is_signed
            self.min_val = min_val
            self.max_val = max_val
        else:
            self.is_number = False
            self.is_integer = False
            self.is_signed = False
            self.min_val = None
            self.max_val = None
            bytenum = int(name.split('_')[-1])
            self.struct_format = f'{bytenum}s'
            self.num_bytes = bytenum
            if 'string' in name:
                self.is_string = True
                self.encode_func = bytes_to_ascii
                self.decode_func = ascii_to_bytes
            elif 'bytes' not in name:
                raise ValueError(f'Invalid builtin type name: {name}')
        self.struct_format = ENDIAN_FORMAT_CHAR + self.struct_format # Make big-endian

    def byte_length(self, bytestream=None):
        return self.num_bytes
    
    def parse_bytes(self, bytestream):
        if len(bytestream) < self.num_bytes:
            return (False, None, bytestream)
        parsed_value = struct.unpack(self.struct_format, bytestream[:self.num_bytes])[0]
        return (True, self.encode_func(parsed_value), bytestream[self.num_bytes:])

    def write_bytes(self, value):
        return struct.pack(self.struct_format, self.decode_func(value))
    
    def validate_type(self, value):
        if self.is_number:
            if self.is_integer:
                if (not isinstance(value, int)) or (value < self.min_val) or (value > self.max_val):
                    return False
            else:
                if (not isinstance(value, float)):
                    return False
        else:
            if (self.is_string and (not isinstance(value, str))) or (not self.is_string and not isinstance(value, bytes)):
                return False
            if (len(value) != self.num_bytes):
                return False
        return True

class VariableLengthBuiltinType(TypeParser):
    def __init__(self, name):
        super().__init__(name, True)
        _, rootname, length_info_bitnum = name.split('_')
        self.rootname = rootname
        self.encode_func = identity
        self.decode_func = identity
        self.is_string = False
        if self.rootname == 'string':
            self.is_string = True
            self.encode_func = bytes_to_ascii
            self.decode_func = ascii_to_bytes
        self.length_info_bitnum = int(length_info_bitnum)
        self.struct_format = ENDIAN_FORMAT_CHAR+LengthBitNumberToStructFormat[self.length_info_bitnum]
        self.length_info_bytenum = self.length_info_bitnum // 8

    def byte_length(self, bytestream=None):
        if bytestream is None:
            warnings.warn('byte_length method of variable length object called without bytestream; returning byte number of length field only')
            return self.length_info_bytenum
        length = struct.unpack(self.struct_format, bytestream[:self.length_info_bytenum])[0]
        return length + self.length_info_bytenum
    
    def parse_bytes(self, bytestream):
        if len(bytestream) < self.length_info_bytenum:
            return (False, None, bytestream)
        length = struct.unpack(self.struct_format, bytestream[:self.length_info_bytenum])[0]
        endpoint = self.length_info_bytenum + length
        if len(bytestream) < endpoint:
            return (False, None, bytestream)
        return (True, self.encode_func(bytestream[self.length_info_bytenum:endpoint]), bytestream[endpoint:])
    
    def write_bytes(self, value):
        length = len(value)
        return struct.pack(self.struct_format, length) + self.decode_func(value)
    
    def validate_type(self, value):
        if (self.is_string) and (not isinstance(value, str)):
            return False
        elif (not self.is_string) and (not isinstance(value, bytes)):
            return False
        return True


class CompoundType(TypeParser):
    def __init__(self, name, fields):
        super().__init__(name, False)
        # Then stuff with fields



# Later, implement some means of condensing all the parse logic to direct references to other types
# i.e., after initial config intake, go from a bunch of strings to a bunch of references to TypeParser objects
# method of TypeRegistry I suppose
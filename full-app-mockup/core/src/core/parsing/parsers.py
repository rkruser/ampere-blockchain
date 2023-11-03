from functools import wraps
import struct
import warnings

# convention: types always end with ".X.Y" where X and Y and version and sub-version.
# Version specs by themselves are "X.Y" strings


# Consider wrapping all created objects in a class

class BasicTypeInfo:
    def __init__(self, struct_format, num_bytes, is_integer, is_signed, min_val, max_val):
        self.struct_format = struct_format
        self.num_bytes = num_bytes
        self.is_integer = is_integer
        self.is_signed = is_signed
        self.min_val = min_val
        self.max_val = max_val
    def get_tuple(self):
        return (self.struct_format, self.num_bytes, self.is_integer, self.is_signed, self.min_val, self.max_val)


class INFO:
    ENDIAN_FORMAT_CHAR = '>' #big-endian
    FixedBuiltinTypeInfo = {
        'uint_8': BasicTypeInfo('B', 1, True, False, 0, 2**8-1),
        'uint_16': BasicTypeInfo('H', 2, True, False, 0, 2**16-1),
        'uint_32': BasicTypeInfo('I', 4, True, False, 0, 2**32-1),
        'uint_64': BasicTypeInfo('Q', 8, True, False, 0, 2**64-1),
        'int_8': BasicTypeInfo('b', 1, True, True, -2**7, 2**7-1),
        'int_16': BasicTypeInfo('h', 2, True, True, -2**15, 2**15-1),
        'int_32': BasicTypeInfo('i', 4, True, True, -2**31, 2**31-1),
        'int_64': BasicTypeInfo('q', 8, True, True, -2**63, 2**63-1),
        'float_32': BasicTypeInfo('f', 4, False, True, None, None),
        'float_64': BasicTypeInfo('d', 8, False, True, None, None)
    }
    LengthBitsFormat = {
        8: 'B',
        16: 'H',
        32: 'I',
        64: 'Q'
    }
    Types = None

def isBuiltinType(type_name):
    if type_name == 'dynamic':
        return True
    elif type_name in INFO.FixedBuiltinTypeInfo:
        return True
    split_name = type_name.split('_')
    if len(split_name) == 3:
        prefix, rootname, length_info_bitnum = split_name
        try:
            length_info_bitnum = int(length_info_bitnum)
        except ValueError:
            return False
        if (prefix != 'variable') or (rootname not in ['string', 'bytes']) or (length_info_bitnum not in INFO.LengthBitsFormat):
            return False
        return True
    if len(split_name) == 2:
        rootname, bytenum = split_name
        try:
            bytenum = int(bytenum)
        except ValueError:
            return False
        if (rootname not in ['string', 'bytes']):
            return False
        return True
    return False

def isVariableLength(type_name):
    return type_name.startswith('variable')

class TypeRegistry:
    def __init__(self):
        self.types = {}
        self.rootname_versions = {}
        # Should initialize with all builtin types

    def register_type(self, type_parser):
        self.types[type_parser.type_name()] = type_parser
        if type_parser.type_rootname() not in self.rootname_versions:
            self.rootname_versions[type_parser.type_rootname()] = []
        self.rootname_versions[type_parser.type_rootname()].append(type_parser.type_version())
        return type_parser
    
    def get_latest_version_name(self, rootname):
        if rootname not in self.rootname_versions:
            return None
        if len(self.rootname_versions[rootname]) == 0:
            return None
        return join_typename(rootname, max(self.rootname_versions[rootname]))
    
    def get_latest_version(self, rootname):
        latest_version_name = self.get_latest_version_name(rootname)
        if latest_version_name is None:
            return None
        return self.get_type(latest_version_name)

    def get_type(self, type_name):
        if type_name in self.types:
            return self.types[type_name]
        elif isBuiltinType(type_name):
            if type_name == 'dynamic':
                return self.register_type(DynamicType())
            elif isVariableLength(type_name):
                return self.register_type(VariableLengthBuiltinType(type_name))
            else:
                return self.register_type(FixedLengthBuiltinType(type_name))
        return None
    
    def resolve_parsers(self):
        for type_parser in self.types.values():
            type_parser.resolve_parsers()


INFO.Types = TypeRegistry()


def join_typename(rootname, version):
    if version is None:
        return rootname
    return f'{rootname}.v.{version[0]}.{version[1]}'

def split_typename(type_name):
    split_name = type_name.split('.')
    if len(split_name) == 4:
        if split_name[1] != 'v':
            raise ValueError(f'Invalid type name {type_name}. Types must have either no version or a version of the form "[NAME].v.X.Y"')
        return (split_name[0], tuple(int(split_name[2]), int(split_name[3])))
    elif len(split_name) == 1:
        return (type_name, None)
    else:
        raise ValueError(f'Invalid type name {type_name}. Types must have either no version or a version of the form "[NAME].v.X.Y"')

class TypeParser:
    def __init__(self, name, is_builtin):
        self.name = name
        self.builtin = is_builtin
        self.rootname, self.version = split_typename(self.name)

    '''
    Return true if type is builtin (e.g., lowercase by convention). Return false if compound type.
    '''
    def is_builtin(self):
        return self.builtin
    
    def type_name(self):
        return self.name
    
    def type_rootname(self):
        return self.rootname

    def type_version(self):
        return self.version

    def resolve_parsers(self):
        pass

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


class DynamicType(TypeParser):
    # Can only be used to parse compound types that prepend their type name to the bytestream
    def __init__(self, type_registry=INFO.Types):
        super().__init__('dynamic', True)
        self.type_name_parser = TypeReference('variable_string_8', type_registry=type_registry)
        self.type_registry = type_registry

    def resolve_parsers(self):
        self.type_name_parser = self.type_name_parser.get_type_parser()

    def get_dynamic_parser(self, bytestream):
        success_flag, cast_type_name, _ = self.type_name_parser.parse_bytes(bytestream)
        if not success_flag:
            return (False, None, None)
        dynamic_parser = self.type_registry.get_type(cast_type_name)
        if dynamic_parser is None:
            return (False, None, None)
        return (True, cast_type_name, dynamic_parser)

    def byte_length(self, bytestream=None):
        if bytestream is None:
            warnings.warn('byte_length method of dynamic type called without bytestream; returning byte number of type_name length field only')
            return 1
        success_flag, cast_type_name, dynamic_parser = self.get_dynamic_parser(bytestream)
        if not success_flag:
            raise ValueError(f'Could not load dynamic type parser for type name {cast_type_name}')
        return dynamic_parser.byte_length(bytestream=bytestream)

    def parse_bytes(self, bytestream):
        success_flag, _, dynamic_parser = self.get_dynamic_parser(bytestream)
        if not success_flag:
            return (False, None, bytestream)
        success_flag, parsed_value, remainder = dynamic_parser.parse_bytes(bytestream) #Use full bytestream here because the cast type will re-read its own type name
        if not success_flag:
            return (False, None, bytestream)
        return (True, parsed_value, remainder)

    def write_bytes(self, value_dict):
        dynamic_parser = self.type_registry.get_type(value_dict['_type'])
        if dynamic_parser is None:
            raise ValueError(f'Could not load dynamic type parser for type name {value_dict["_type"]}')
        return dynamic_parser.write_bytes(value_dict)

    def validate_type(self, value_dict):
        if not isinstance(value_dict, dict):
            return False
        if '_type' not in value_dict:
            return False
        dynamic_parser = self.type_registry.get_type(value_dict['_type'])
        if dynamic_parser is None:
            return False
        return dynamic_parser.validate_type(value_dict)



def bytes_to_ascii(bytestream):
    return bytestream.decode('ascii')

def ascii_to_bytes(stringstream):
    return stringstream.encode('ascii')

def identity(bytestream):
    return bytestream

class FixedLengthBuiltinType(TypeParser):
    # TODO: greatly improve the logic of this initializer
    def __init__(self, name):
        super().__init__(name, True)
        self.encode_func = identity
        self.decode_func = identity
        self.is_string = False
        if name in INFO.FixedBuiltinTypeInfo:
            self.is_number = True
            self.struct_format, self.num_bytes, 
            self.is_integer, self.is_signed, 
            self.min_val, self.max_val = INFO.FixedBuiltinTypeInfo[name].get_tuple()
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
        self.struct_format = INFO.ENDIAN_FORMAT_CHAR + self.struct_format # Make big-endian

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
        self.struct_format = INFO.ENDIAN_FORMAT_CHAR+INFO.LengthBitsFormat[self.length_info_bitnum]
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
        length = len(value) #struct.pack does the bounds checking
        return struct.pack(self.struct_format, length) + self.decode_func(value)
    
    def validate_type(self, value):
        if (self.is_string) and (not isinstance(value, str)):
            return False
        elif (not self.is_string) and (not isinstance(value, bytes)):
            return False
        return True


class TypeReference(TypeParser):
    def __init__(self, name, type_registry=INFO.Types):
        super().__init__(name, False)
        self.type_registry = type_registry

    def get_type_parser(self):
        type_parser = self.type_registry.get_type(self.name)
        if type_parser is None:
            raise ValueError(f'Type {self.name} not found in type registry')
        return type_parser

    def byte_length(self, bytestream=None):
        type_parser = self.get_type_parser()
        return type_parser.byte_length(bytestream=bytestream)

    def parse_bytes(self, bytestream):
        type_parser = self.get_type_parser()
        return type_parser.parse_bytes(bytestream)

    def write_bytes(self, value):
        type_parser = self.get_type_parser()
        return type_parser.write_bytes(value)

    def validate_type(self, value):
        type_parser = self.get_type_parser()
        return type_parser.validate_type(value)


class CompoundType(TypeParser):
    def __init__(self, name, fields, prepend_type_name=False, type_registry=INFO.Types, defer_inner_casts=False):
        super().__init__(name, False)
        self.type_registry = type_registry
        self.defer_inner_casts = defer_inner_casts
        self.fields = fields
        self.prepend_type_name = prepend_type_name

        if self.prepend_type_name:
            self.field_names = ['_type']
            self.type_names = ['variable_string_8']
        else:
            self.field_names = []
            self.type_names = []

        self.field_names += [field['name'] for field in self.fields]
        self.type_names += [field['type'] for field in self.fields]
        
        self.parsers = [TypeReference(type_name, type_registry=self.type_registry) for type_name in self.type_names]

        self.inner_parsers = {}
        for field in self.fields:
            if 'inner_type' in field:
                self.inner_parsers[field['name']] = TypeReference(field['inner_type'],
                                                                   type_registry=self.type_registry)

    '''
    This is separated out because during __init__, not all types may be registered yet.
    Resolving parsers is optional but may improve performance and catch errors earlier.
    '''
    def resolve_parsers(self):
        new_parsers = [parser_reference.get_type_parser() for parser_reference in self.parsers]
        self.parsers = new_parsers

        new_inner_parsers = { inner_field: inner_parser_reference.get_type_parser() for inner_field, inner_parser_reference in self.inner_parsers }
        self.inner_parsers = new_inner_parsers

    def byte_length(self, bytestream=None):
        return sum([parser.byte_length(bytestream=bytestream) for parser in self.parsers])

    def perform_inner_casts(self, parsed_dict):
        for field_name, inner_parser in self.inner_parsers:
            if field_name in parsed_dict:
                parsed_dict[field_name] = inner_parser.parse_bytes(parsed_dict[field_name])
            else:
                raise ValueError(f'Field {field_name} not found in dictionary')
        return parsed_dict

    def parse_bytes(self, bytestream):
        parsed_dict = {}
        for field_name, parser in zip(self.field_names, self.parsers):
            success_flag, parsed_value, bytestream = parser.parse_bytes(bytestream)
            if not success_flag:
                return (False, None, bytestream)
            parsed_dict[field_name] = parsed_value
        if not self.defer_inner_casts:
            parsed_dict = self.perform_inner_casts(parsed_dict)
        if self.prepend_type_name:
            if parsed_dict['_type'] != self.name:
                raise TypeError(f'Expected type {self.name} but got type {parsed_dict["_type"]}')
        return (True, parsed_dict, bytestream)

    def write_bytes(self, value_dict):
        bytestream = b''
        if self.prepend_type_name:
            value_dict['_type'] = self.name #overwrite pre-existing type name if it exists
        for field_name, parser in zip(self.field_names, self.parsers):
            field_value = value_dict[field_name]
            if (field_name in self.inner_parsers) and (isinstance(field_value, dict)):
                field_value = self.inner_parsers[field_name].write_bytes(field_value)
            bytestream += parser.write_bytes(field_value)
        return bytestream

    def validate_type(self, value_dict, verify_inner_types=True):
        if not isinstance(value_dict, dict):
            return False
        field_names = self.field_names
        if self.prepend_type_name:
            field_names = field_names[1:]
        if not set(field_names).issubset(value_dict.keys()):
            return False
        for field_name, parser in zip(field_names, self.parsers):
            field_value = value_dict[field_name]
            if isinstance(field_value, dict) or (verify_inner_types and (field_name in self.inner_parsers)):
                if field_name in self.inner_parsers:
                    if not self.inner_parsers[field_name].validate_type(field_value):
                        return False
                else:
                    return False
            elif not parser.validate_type(value_dict[field_name]):
                return False
        return True


'''
TODO:
 - Make it so that get_type() returns the latest version of a type if no version is specified
 - Handle version end strings in the compound type parser somehow
 - Test everything with functions that create basic messages
 - *Test that read and write are perfect inverses, and test that hashing is consistent

Note: entry point for parsing a new message is either the dynamic parser or the latest OUTER_MESSAGE parser or something
'''



def test_1():
    for typename in INFO.FixedBuiltinTypeInfo:
        print(typename, isBuiltinType(typename))
    names = [
        'dynamic',
        'string_4',
        'bytes_9',
        'string_120',
        'bytes_24',
        'variable_bytes_8',
        'variable_bytes_16',
        'variable_bytes_32',
        'variable_bytes_64',
        'variable_bytes_20',
        'variable_string_8',
        'variable_string_16',
        'variable_string_32',
        'variable_string_64',
        'variable_string_10',
        'asdf',
        'MOOP_19.v.1.0'
    ]
    for name in names:
        print(name, isBuiltinType(name))


if __name__ == '__main__':
    # Test code
    test_1()
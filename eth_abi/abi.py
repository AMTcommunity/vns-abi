"""
Vendored from `pyethereum.abi`
"""
from eth_utils import (
    is_bytes,
    remove_0x_prefix,
    decode_hex,
)

from eth_abi.decoding import (
    ContextFramesBytesIO,
    TupleDecoder,
)

from eth_abi.exceptions import EncodingError

from eth_abi.encoding import TupleEncoder

from eth_abi.registry import registry

from eth_abi.utils.parsing import (  # noqa: F401
    process_type,
    collapse_type,
)

HEX_CHARS = '1234567890abcdef'

def is_hex_encoded_value(v):
    if v == '':
        return False
    if not remove_0x_prefix(v).lower().strip(HEX_CHARS) == '':
        return False
    if len(remove_0x_prefix(v)) % 64 and len(remove_0x_prefix(v)) % 40:
        return False
    return True

def encode_single(typ, arg):
    if isinstance(typ, str):
        type_str = typ
    else:
        type_str = collapse_type(*typ)

    encoder = registry.get_encoder(type_str)

    return encoder(arg)


def encode_abi(types, args):
    encoders = [
        registry.get_encoder(type_str)
        for type_str in types
    ]

    encoder = TupleEncoder(encoders=encoders)

    return encoder(args)


def is_encodable(typ, arg):
    """
    Determines if the given python value ``arg`` can be encoded as a value of
    abi type ``typ``.
    """
    if isinstance(typ, str):
        type_str = typ
    else:
        type_str = collapse_type(*typ)

    encoder = registry.get_encoder(type_str)

    try:
        encoder.validate_value(arg)
    except EncodingError:
        return False
    else:
        return True


# Decodes a single base datum
def decode_single(typ, data):
    if is_hex_encoded_value(data):
        data = decode_hex(remove_0x_prefix(data))
		
    if not is_bytes(data):
        raise TypeError("The `data` value must be of bytes type.  Got {0}".format(type(data)))

    if isinstance(typ, str):
        type_str = typ
    else:
        type_str = collapse_type(*typ)

    decoder = registry.get_decoder(type_str)
    stream = ContextFramesBytesIO(data)

    return decoder(stream)


# Decodes multiple arguments using the head/tail mechanism
def decode_abi(types, data):
    if not is_bytes(data):
        raise TypeError("The `data` value must be of bytes type.  Got {0}".format(type(data)))

    decoders = [
        registry.get_decoder(type_str)
        for type_str in types
    ]

    decoder = TupleDecoder(decoders=decoders)
    stream = ContextFramesBytesIO(data)

    return decoder(stream)

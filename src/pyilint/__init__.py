# -*- coding: UTF-8 -*-
# BSD 3-Clause License
#
# Copyright (c) 2021, InterlockLedger
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import io
from typing import Tuple

# LInt base value. All values larger then or equal to will use more
# than 1 byte to be encoded.
ILINT_BASE = 0xF8

# Maximum value for an unsigned 8-bit integer (2**8 - 1).
MAX_UINT8 = 2**8 - 1

# Maximum value for an unsigned 64-bit integer (2**64 - 1).
MAX_UINT64 = 2**64 - 1


def assert_uint64_bounds(v: int):
    if v < 0:
        raise ValueError('v cannot be negative.')
    elif v > MAX_UINT64:
        raise ValueError('v cannont be larger than 18446744073709551615.')


def assert_uint8_bounds(v: int):
    if v < 0:
        raise ValueError('The value cannot be negative.')
    elif v > MAX_UINT8:
        raise ValueError('The value be larger than 255.')


def ilint_size(v: int) -> int:
    """
    Returns the size of the given value encoded as an **ILInt** in bytes.
    It may raise `ValueError` if `v` is negative or larger than
    18446744073709551615.

    Parameters:
    - `v`: The value to be encoded.

    """
    assert_uint64_bounds(v)
    if v < ILINT_BASE:
        return 1
    elif v <= (0xFF + ILINT_BASE):
        return 2
    elif v <= (0xFFFF + ILINT_BASE):
        return 3
    elif v <= (0xFFFFFF + ILINT_BASE):
        return 4
    elif v <= (0xFFFFFFFF + ILINT_BASE):
        return 5
    elif v <= (0xFFFFFFFFFF + ILINT_BASE):
        return 6
    elif v <= (0xFFFFFFFFFFFF + ILINT_BASE):
        return 7
    elif v <= (0xFFFFFFFFFFFFFF + ILINT_BASE):
        return 8
    else:
        return 9


def ilint_size_from_header(h: int) -> int:
    """
    Returns the size of the **ILInt** in bytes according to the value of the header
    (including the header itself).
    It may raise `ValueError` if `v` is negative or larger than 256.

    Parameters:
    - `h`: The value of the header.

    """
    assert_uint8_bounds(h)
    if h < ILINT_BASE:
        return 1
    else:
        return h - ILINT_BASE + 2


def ilint_encode(v: int, buff: bytearray) -> int:
    """
    Encodes `v` as **ILInt** and append the result to `buff`.

    Parameters:
    - `v`: The 64-bit value to encode;
    - `buff`: The buffer that will receive the value;

    Returns:
    - The number of bytes added.
    """
    size = ilint_size(v)
    if v < ILINT_BASE:
        buff.append(v)
    else:
        buff.append(ILINT_BASE + (size - 2))
        v = v - ILINT_BASE
        buff += v.to_bytes(size - 1, byteorder='big', signed=False)
    return size


def ilint_encode_to_stream(v: int, outp: io.IOBase) -> int:
    """
    Encodes `v` as **ILInt** and write it to `outp`.

    Parameters:
    - `v`: The 64-bit value to encode;
    - `outp`: An `io.IOBase` instance. It must be capable of writing bytes like objects into it;

    Returns:
    - The number of bytes written.
    """
    buff = bytearray()
    size = ilint_encode(v, buff)
    outp.write(buff)
    return size


def ilint_decode_multibyte_core(header: int, size: int, body: bytes) -> Tuple[int, int]:
    """
    Decodes the **ILInt** from the triplet header, size and body. It is a low
    level operation that takes the header, the size of the **ILInt** and the 
    **ILInt** data without the header and decodes it. 

    It was exposed in order to allow fast implementation of decoders under special
    conditions. For this reason, this function has the following restrictions:

    - `size` must be 2 to 9;
    - The value of `size` must be the result of `ilint_size_from_header(header)` but
      it is not verified inside this function;

    Any attempt to call this method with parameters that don't match the previous
    restrictions will result in an undefined behavior. Thus, if you are not sure
    why this method exists, prefer `ilint_decode()` or 
    `ilint_decode_from_stream()` instead.

    It may raise `ValueError` if the **ILInt** data is invalid.

    Parameters:
    - `header`: The byte that is the header of the **ILInt**;
    - `size`: The expected size of the ILInt in bytes;
    - `body`: The rest of the **ILInt** data without the header;

    Retunrs:
    - A tuple with the value read and the number of bytes used.

    New since version 0.2.0.
    """
    if len(body) != size - 1:
        raise ValueError('Premature end of ILInt')
    if len(body) > 1 and body[0] == 0:
        raise ValueError('Invalid ILInt encoding.')
    v = int.from_bytes(body, byteorder='big', signed=False)
    v += ILINT_BASE
    if v > MAX_UINT64:
        raise ValueError('ILInt overflow.')
    return (v, size)


def ilint_decode(buff: bytes) -> Tuple[int, int]:
    """
    Decodes the **ILInt** from a buffer of bytes. It may raise a `ValueError`
    if the format cannot be read.

    Retunrs:
    - A tuple with the value read and the number of bytes used.
    """
    if not buff:
        raise ValueError('buff must have at least 1 byte.')
    header = buff[0]
    if header < ILINT_BASE:
        return (header, 1)
    else:
        size = ilint_size_from_header(header)
        return ilint_decode_multibyte_core(header, size, buff[1:size])


def ilint_decode_from_stream(inp: io.IOBase) -> Tuple[int, int]:
    """
    Reads an **ILInt** value from `inp`. It may raise a `ValueError`
    if an ILInt could not be read.

    Retunrs:
    - A tuple with the value read and the number of bytes used.
    """
    buff = inp.read(1)
    if not buff:
        raise ValueError('Unable to read the header.')
    header = buff[0]
    if header < ILINT_BASE:
        return (header, 1)
    else:
        size = ilint_size_from_header(header)
        body = inp.read(size - 1)
        return ilint_decode_multibyte_core(header, size, body)

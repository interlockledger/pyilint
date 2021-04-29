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
import unittest
import random
from . import *

# ------------------------------------------------------------------------------
# Samples copied from https://github.com/interlockledger/rust-il2-ilint/blob/master/src/tests.rs


class SampleILInt:
    def __init__(self, value: int, encoded: str) -> None:
        self.value = value
        self.encoded = bytes.fromhex(encoded)


SAMPLE_VALUES = [
    SampleILInt(0xF7, 'F7'),
    SampleILInt(0xF8, 'F800'),
    SampleILInt(0x021B, 'F90123'),
    SampleILInt(0x01243D, 'FA012345'),
    SampleILInt(0x0123465F, 'FB01234567'),
    SampleILInt(0x0123456881, 'FC0123456789'),
    SampleILInt(0x012345678AA3, 'FD0123456789AB'),
    SampleILInt(0x123456789ACC5, 'FE0123456789ABCD'),
    SampleILInt(0x123456789ABCEE7, 'FF0123456789ABCDEF'),
    SampleILInt(0xFFFFFFFFFFFFFFFF, 'FFFFFFFFFFFFFFFF07')]

BAD_ENCODINGS = [
    bytes.fromhex('F90000'),
    bytes.fromhex('FA000000'),
    bytes.fromhex(
        'FB00000000'),
    bytes.fromhex(
        'FC0000000000'),
    bytes.fromhex(
        'FD000000000000'),
    bytes.fromhex(
        'FE00000000000000'),
    bytes.fromhex(
        'FF0000000000000000'),
    bytes.fromhex(
        'FFFFFFFFFFFFFFFF08'),
    bytes.fromhex(
        'FFFFFFFFFFFFFFFFFF'),
]


class TestILInt(unittest.TestCase):

    def test_constants(self):

        self.assertEqual(ILINT_BASE, 0xF8)
        self.assertEqual(MAX_UINT8, 255)
        self.assertEqual(MAX_UINT64, 18446744073709551615)

    def test_assert_uint64_bounds(self):

        self.assertRaises(ValueError, assert_uint64_bounds, -1)
        assert_uint64_bounds(0)
        assert_uint64_bounds(1)
        assert_uint64_bounds(18446744073709551615)
        self.assertRaises(ValueError, assert_uint64_bounds,
                          18446744073709551616)

    def test_assert_uint8_bounds(self):

        self.assertRaises(ValueError, assert_uint8_bounds, -1)
        assert_uint8_bounds(0)
        assert_uint8_bounds(1)
        assert_uint8_bounds(255)
        self.assertRaises(ValueError, assert_uint8_bounds, 256)

    def test_ilint_size(self):

        for v in range(0, ILINT_BASE):
            self.assertEqual(ilint_size(v), 1)
        self.assertEqual(ilint_size(ILINT_BASE), 2)
        self.assertEqual(ilint_size(ILINT_BASE + 0xFF), 2)
        self.assertEqual(ilint_size(ILINT_BASE + 0x100), 3)
        self.assertEqual(ilint_size(ILINT_BASE + 0xFFFF), 3)
        self.assertEqual(ilint_size(ILINT_BASE + 0x10000), 4)
        self.assertEqual(ilint_size(ILINT_BASE + 0xFFFFFF), 4)
        self.assertEqual(ilint_size(ILINT_BASE + 0x1000000), 5)
        self.assertEqual(ilint_size(ILINT_BASE + 0xFFFFFFFF), 5)
        self.assertEqual(ilint_size(ILINT_BASE + 0x100000000), 6)
        self.assertEqual(ilint_size(ILINT_BASE + 0xFFFFFFFFFF), 6)
        self.assertEqual(ilint_size(ILINT_BASE + 0x10000000000), 7)
        self.assertEqual(ilint_size(ILINT_BASE + 0xFFFFFFFFFFFF), 7)
        self.assertEqual(ilint_size(ILINT_BASE + 0x1000000000000), 8)
        self.assertEqual(ilint_size(ILINT_BASE + 0xFFFFFFFFFFFFFF), 8)
        self.assertEqual(ilint_size(ILINT_BASE + 0x100000000000000), 9)
        self.assertEqual(ilint_size(0xFFFFFFFFFFFFFFFF), 9)
        self.assertRaises(ValueError, ilint_size, -1)
        self.assertRaises(ValueError, ilint_size, 18446744073709551616)

    def test_ilint_size_from_header(self):
        for h in range(0, ILINT_BASE):
            self.assertEqual(ilint_size_from_header(h), 1)
        self.assertEqual(ilint_size_from_header(ILINT_BASE), 2)
        self.assertEqual(ilint_size_from_header(ILINT_BASE + 1), 3)
        self.assertEqual(ilint_size_from_header(ILINT_BASE + 2), 4)
        self.assertEqual(ilint_size_from_header(ILINT_BASE + 3), 5)
        self.assertEqual(ilint_size_from_header(ILINT_BASE + 4), 6)
        self.assertEqual(ilint_size_from_header(ILINT_BASE + 5), 7)
        self.assertEqual(ilint_size_from_header(ILINT_BASE + 6), 8)
        self.assertEqual(ilint_size_from_header(ILINT_BASE + 7), 9)
        self.assertRaises(ValueError, ilint_size_from_header, -1)
        self.assertRaises(ValueError, ilint_size_from_header, 256)

    def test_ilint_encode(self):

        for s in SAMPLE_VALUES:
            buff = bytearray()
            size = ilint_encode(s.value, buff)
            self.assertEqual(len(s.encoded), size)
            self.assertEqual(len(buff), size)
            self.assertEqual(s.encoded, buff)

        for s in SAMPLE_VALUES:
            buff = bytearray()
            buff.append(0xFF)
            size = ilint_encode(s.value, buff)
            self.assertEqual(len(s.encoded), size)
            self.assertEqual(len(buff), size + 1)
            self.assertEqual(s.encoded, buff[1:])

        buff = bytearray()
        self.assertRaises(ValueError, ilint_encode, -1, buff)
        self.assertRaises(ValueError, ilint_encode, 2**64, buff)

    def test_ilint_encode_to_stream(self):

        for s in SAMPLE_VALUES:
            outp = io.BytesIO()
            size = ilint_encode_to_stream(s.value, outp)
            self.assertEqual(len(s.encoded), size)
            self.assertEqual(len(s.encoded), outp.tell())
            outp.seek(0)
            buff = outp.read()
            self.assertEqual(len(buff), size)
            self.assertEqual(s.encoded, buff)

        for s in SAMPLE_VALUES:
            outp = io.BytesIO()
            outp.write(b'\xFF')
            size = ilint_encode_to_stream(s.value, outp)
            self.assertEqual(len(s.encoded) + 1, outp.tell())
            self.assertEqual(len(s.encoded), size)
            outp.seek(1)
            buff = outp.read()
            self.assertEqual(len(buff), size)
            self.assertEqual(s.encoded, buff)

        outp = io.BytesIO()
        self.assertRaises(ValueError, ilint_encode_to_stream, -1, outp)
        self.assertRaises(ValueError, ilint_encode_to_stream, 2**64, outp)

    def test_ilint_decode(self):

        for s in SAMPLE_VALUES:
            buff = bytearray(s.encoded)
            value, size = ilint_decode(buff)
            self.assertEqual(s.value, value)
            self.assertEqual(len(s.encoded), size)

        for s in SAMPLE_VALUES:
            buff = bytearray(s.encoded)
            buff.append(1)
            value, size = ilint_decode(buff)
            self.assertEqual(s.value, value)
            self.assertEqual(len(s.encoded), size)

        for s in SAMPLE_VALUES:
            buff = bytearray(s.encoded[:-1])
            self.assertRaises(ValueError, ilint_decode, buff)

        for bad in BAD_ENCODINGS:
            self.assertRaises(ValueError, ilint_decode, bad)

    def test_ilint_decode_from_stream(self):

        for s in SAMPLE_VALUES:
            inp = io.BytesIO(s.encoded)
            value, size = ilint_decode_from_stream(inp)
            self.assertEqual(s.value, value)
            self.assertEqual(len(s.encoded), size)

        for s in SAMPLE_VALUES:
            inp = io.BytesIO(s.encoded + b'1')
            value, size = ilint_decode_from_stream(inp)
            self.assertEqual(s.value, value)
            self.assertEqual(len(s.encoded), size)

        for s in SAMPLE_VALUES:
            inp = io.BytesIO(s.encoded[:-1])
            self.assertRaises(ValueError, ilint_decode_from_stream, inp)

        for bad in BAD_ENCODINGS:
            self.assertRaises(ValueError, ilint_decode_from_stream,
                              io.BytesIO(bad))

    def test_ilint_encode_decode(self):

        for _ in range(1024):
            v = random.randrange(0, MAX_UINT64)
            buff = bytearray()
            size = ilint_encode(v, buff)
            self.assertEqual(ilint_size(v), size)
            dec, dec_size = ilint_decode(buff)
            self.assertEqual(ilint_size(v), dec_size)
            self.assertEqual(v, dec)

        for _ in range(1024):
            v = random.randrange(0, MAX_UINT64)
            stream = io.BytesIO()
            size = ilint_encode_to_stream(v, stream)
            self.assertEqual(ilint_size(v), size)
            stream.seek(0)
            dec, dec_size = ilint_decode_from_stream(stream)
            self.assertEqual(ilint_size(v), dec_size)
            self.assertEqual(v, dec)

    def test_ilint_decode_multibyte_core(self):

        for s in SAMPLE_VALUES[1:]:
            if len(s.encoded) > 1:
                header = s.encoded[0]
                size = ilint_size_from_header(header)
                body = s.encoded[1:]
                value, dec_size = ilint_decode_multibyte_core(
                    header, size, body)
                self.assertEqual(s.value, value)
                self.assertEqual(size, dec_size)

        for s in SAMPLE_VALUES[1:]:
            if len(s.encoded) > 1:
                header = s.encoded[0]
                size = ilint_size_from_header(header)
                body = s.encoded[1:-1]
                self.assertRaises(ValueError, ilint_decode_multibyte_core,
                                  header, size, body)

        for bad in BAD_ENCODINGS:
            header = bad[0]
            size = ilint_size_from_header(header)
            body = bad[1:]
            self.assertRaises(ValueError, ilint_decode_multibyte_core,
                              header, size, body)

# Copyright © 2015 Léo Flaventin Hauchecorne
# 
# This file is part of lightprotobuf.
# 
# lightprotobuf is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# lightprotobuf is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with lightprotobuf.  If not, see <http://www.gnu.org/licenses/>

import unittest
from lightprotobuf import *
from io import *
from inspect import isclass
from enum import IntEnum

class TestUVarint(unittest.TestCase):
	C = UVarint
	alltests = [
			(0, b'\x00'),
			(1, b'\x01'),
			(127, b'\x7F'),
			(128, b'\x80\x01'),
			(129, b'\x81\x01'),
			(0xAAAAAAAA, b'\xAA\xD5\xAA\xD5\x0A'),
			(0xAAAAAAAAAAAAAAAAAAAA, b'\xAA\xD5\xAA\xD5\xAA\xD5\xAA\xD5\xAA\xD5\xAA\x05'),
		]
	enc = []
	dec = []
	from_to_py = [
			(0, 0),
			(42, 42),
			(1337421337421337, 1337421337421337),
		]
	from_py = [
			(75.0, 75),
			('truc', ValueError),
			(-45, NumberOverflowException),
		]
	to_py = []
	def test_encode(self):
		for v, r in self.alltests + self.enc:
			with self.subTest(VALUE=v):
				if r is None:
					self.C.encode(v)
				elif isclass(r) and issubclass(r, Exception):
					with self.assertRaises(r):
						self.C.encode(v)
				else:
					self.assertEqual(self.C.encode(v), r)
	
	def test_decode(self):
		for v, r in self.alltests + self.dec:
			if v is None:
				with self.subTest(INPUT=r):
					self.C.decode(r)
			elif isclass(v) and issubclass(v, Exception):
				with self.subTest(INPUT=r):
					with self.assertRaises(v):
						self.C.decode(r)
			else:
				with self.subTest(VALUE=v):
					self.assertEqual(self.C.decode(r), v)

	def test_to_stream(self):
		for v, r in self.alltests + self.enc:
			with self.subTest(VALUE=v):
				if r is None:
					b = BytesIO()
					self.C.to_stream(b, v)
				elif isclass(r) and issubclass(r, Exception):
					with self.assertRaises(r):
						b = BytesIO()
						self.C.to_stream(b, v)
				else:
					b = BytesIO()
					self.C.to_stream(b, v)
					self.assertEqual(b.getbuffer(), r)
	
	def test_from_stream(self):
		for v, r in self.alltests + self.dec:
			if v is None:
				with self.subTest(INPUT=r):
					b = BytesIO(r)
					self.C.from_stream(b)
			elif isclass(v) and issubclass(v, Exception):
				with self.subTest(INPUT=r):
					with self.assertRaises(v):
						b = BytesIO(r)
						self.C.from_stream(b)
			else:
				with self.subTest(VALUE=v):
					b = BytesIO(r)
					self.assertEqual(self.C.from_stream(b), v)
	
	def test_from_py(self):
		for v, r in self.from_to_py + self.from_py:
			with self.subTest(VALUE=v):
				if isclass(r) and issubclass(r, Exception):
					with self.assertRaises(r):
						self.C.from_py(v)
				else:
					self.assertEqual(self.C.from_py(v), r)
	
	def test_to_py(self):
		for v, r in self.from_to_py + self.to_py:
			with self.subTest(VALUE=r):
				if isclass(v) and issubclass(v, Exception):
					with self.assertRaises(v):
						self.C.to_py(r)
				else:
					self.assertEqual(self.C.to_py(r), v)
	
		

class TestVarint_positive(TestUVarint):
	C = Varint
	alltests = [
			(0, b'\x00'),
			(1, b'\x01'),
			(127, b'\x7F'),
			(128, b'\x80\x01'),
			(129, b'\x81\x01'),
			(0xAAAAAAAA, b'\xAA\xD5\xAA\xD5\x0A'),
		]
	enc = [
			(0xAAAAAAAAAAAAAAAAAAAA, AssertionError)
		]
	dec = [
			(NumberOverflowException, b'\xAA\xD5\xAA\xD5\xAA\xD5\xAA\xD5\xAA\xD5\xAA\x05')
		]
	from_to_py = [
			(0, 0),
			(42, 42),
			(1337, 1337),
			(2**63-1, 2**63-1),
		]
	from_py = [
			(75.0, 75),
			('truc', ValueError),
			(2**63, NumberOverflowException)
		]
	to_py = []

class TestVarint_negative(TestUVarint):
	C = Varint
	alltests = [
			(-1, b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x01'),
			(-2**63, b'\x80\x80\x80\x80\x80\x80\x80\x80\x80\x01'),
			(-42, b'\xD6\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x01'),
		]
	enc = [
			((-2**63)-1, AssertionError)
		]
	from_to_py = [
			(-1, -1),
			(-45, -45),
			(-2**63, -2**63),
		]
	from_py = [
			(-75.0, -75),
			((-2**63) -1, NumberOverflowException),
		]
	to_py = []

class TestZZVarint(TestUVarint):
	C = ZZVarint
	alltests = [
			(0, b'\x00'),
			(-1, b'\x01'),
			(1, b'\x02'),
			(-2, b'\x03'),
			(2, b'\x04'),
			(2147483647, b'\xFE\xFF\xFF\xFF\x0F'),
			(-2147483648, b'\xFF\xFF\xFF\xFF\x0F'),
		]
	from_to_py = [
			(0, 0),
			(42, 42),
			(-42, -42),
			(1337, 1337),
			(-1337, -1337),
			(2**63-1, 2**63-1),
			(-2**63, -2**63),
		]
	from_py = [
			(2**63, NumberOverflowException),
			((-2**63)-1, NumberOverflowException),
		]
	to_py = []


class TestBytes(unittest.TestCase):
	C = Bytes
	alltests = [
			( b'', b'\x00' ),
			( b'test', b'\04test' ),
			( b'A very long\x00test with null byte inside'*10,
				b'\xFC\x02'+b'A very long\x00test with null byte inside'*10 ),
		]
	enc = []
	dec = []
	from_to_py = [
			( b'Some bytes', 'Some bytes' ),
		]
	from_py = [
			( 'A string', TypeError),
		]
	to_py = []
	def test_to_stream(self):
		for v, r in self.alltests + self.enc:
			with self.subTest(VALUE=v):
				if r is None:
					b = BytesIO()
					self.C.to_stream(b, v)
				else:
					b = BytesIO()
					self.C.to_stream(b, v)
					self.assertEqual(b.getbuffer(), r)
	
	def test_from_stream(self):
		for v, r in self.alltests + self.dec:
			if v is None:
				with self.subTest(INPUT=r):
					b = BytesIO(r)
					self.C.from_stream(b)
			else:
				with self.subTest(VALUE=v):
					b = BytesIO(r)
					self.assertEqual(self.C.from_stream(b), v)

class TestString(TestBytes):
	C = String
	alltests =  [
			( '', b'\x00' ),
			( 'test', b'\04test' ),
			( 'A very long\x00test with null byte inside'*10,
				b'\xFC\x02'+b'A very long\x00test with null byte inside'*10 ),
		]
	from_to_py = [
			( 'A string', 'A string' ),
		]
	from_py = [
			( b'bytes', TypeError),
		]
	to_py = []

class TestFixed64(TestUVarint):
	C = Fixed64
	alltests = [
			(0,                  b'\x00\x00\x00\x00\x00\x00\x00\x00'),
			(0xFFFFFFFFFFFFFFFF, b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'),
			(0x123456789ABCDEF0, b'\xF0\xDE\xBC\x9A\x78\x56\x34\x12'),
		]
	from_to_py = [
			(0, 0),
			(42, 42),
			(1337, 1337),
			(2**64-1, 2**64-1),
		]
	from_py = [
			(2**64, ValueError),
			(-1, ValueError),
		]
	to_py = []

class TestFixed32(TestUVarint):
	C = Fixed32
	alltests = [
			(0,          b'\x00\x00\x00\x00'),
			(0xFFFFFFFF, b'\xFF\xFF\xFF\xFF'),
			(0x9ABCDEF0, b'\xF0\xDE\xBC\x9A'),
		]
	from_to_py = [
			(0, 0),
			(42, 42),
			(1337, 1337),
			(2**32-1, 2**32-1),
		]
	from_py = [
			(2**32, ValueError),
			(-1, ValueError),
		]
	to_py = []

class TestSFixed64(TestUVarint):
	C = SFixed64
	alltests = [
			(0,                   b'\x00\x00\x00\x00\x00\x00\x00\x00'),
			(0x7FFFFFFFFFFFFFFF,  b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x7F'),
			(0x123456789ABCDEF0,  b'\xF0\xDE\xBC\x9A\x78\x56\x34\x12'),
			(-0x8000000000000000, b'\x00\x00\x00\x00\x00\x00\x00\x80'),
			(-1,                  b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'),
			(-3,                  b'\xFD\xFF\xFF\xFF\xFF\xFF\xFF\xFF'),
		]
	from_to_py = [
			(0, 0),
			(42, 42),
			(-42, -42),
			(1337, 1337),
			(-1337, -1337),
			(2**63-1, 2**63-1),
			(-2**63, -2**63),
		]
	from_py = [
			(2**63, ValueError),
			((-2**63)-1, ValueError),
		]
	to_py = []

class TestSFixed32(TestUVarint):
	C = SFixed32
	alltests = [
			(0,           b'\x00\x00\x00\x00'),
			(0x7FFFFFFF,  b'\xFF\xFF\xFF\x7F'),
			(0x12345678,  b'\x78\x56\x34\x12'),
			(-0x80000000, b'\x00\x00\x00\x80'),
			(-1,          b'\xFF\xFF\xFF\xFF'),
			(-3,          b'\xFD\xFF\xFF\xFF'),
		]
	from_to_py = [
			(0, 0),
			(42, 42),
			(-42, -42),
			(1337, 1337),
			(-1337, -1337),
			(2**31-1, 2**31-1),
			(-2**31, -2**31),
		]
	from_py = [
			(2**31, ValueError),
			((-2**31)-1, ValueError),
		]
	to_py = []

class TestFloat(TestUVarint):
	C = Float
	alltests = [
			(42.41999816894531,   b'\x14\xAE\x29\x42'),
			(1337.4200439453125,  b'\x71\x2D\xA7\x44'),
		]
	from_py = [
			( 'test', Exception),
		]
	to_py = []

class TestDouble(TestUVarint):
	C = Double
	alltests = [
			(42.42,   b'\xF6\x28\x5C\x8F\xC2\x35\x45\x40'),
			(1337.42, b'\x48\xE1\x7A\x14\xAE\xE5\x94\x40'),
		]
	from_py = [
			( 'test', Exception),
		]
	to_py = []

class TestEnum(TestUVarint):
	class SimpleEnum(IntEnum):
		foo = 2
		bar = 3
		babar = -1
	
	C = type(SimpleEnum.__name__+'Field', (EnumFieldType,), dict(enum = SimpleEnum))
	alltests = [
			(SimpleEnum.foo, b'\x02'),
			(SimpleEnum.bar, b'\x03'),
			(SimpleEnum.babar, b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x01'),
		]
	from_to_py = []
	from_py = [
			(2, TypeError),
			(-1, TypeError),
			(5, TypeError)
		]
	to_py = [
			(Exception, b'\x04'),
		]


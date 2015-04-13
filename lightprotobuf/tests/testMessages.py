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

class TestMessage(unittest.TestCase):
	def test_empty(self):
		class Empty(Message):
			pass
		s = Empty()
		b = io.BytesIO()
		Empty.to_stream(b, s)
		self.assertEqual(bytes(b.getbuffer()), b'\x00')
		b = io.BytesIO()
		Empty.to_stream_root(b, s)
		self.assertEqual(b.getbuffer(), b'')
		s = Empty.from_stream_root(io.BytesIO(b'\x07'))
		s = Empty.from_stream(io.BytesIO(b'\x00'))
	
	def test_simple(self):
		class Simple(Message):
			test = Field(2, Int32)
		s = Simple()
		s.test = 0x82
		b = io.BytesIO()
		Simple.to_stream(b, s)
		self.assertEqual(bytes(b.getbuffer()), b'\x03\x10\x82\x01')
		b = io.BytesIO()
		Simple.to_stream_root(b, s)
		self.assertEqual(b.getbuffer(), b'\x10\x82\x01')
		s = Simple.from_stream_root(io.BytesIO(b'\x10\x82\x01\x07'))
		self.assertEqual(s.test, 0x82)
		s = Simple.from_stream(io.BytesIO(b'\x03\x10\x82\x01'))
		self.assertEqual(s.test, 0x82)


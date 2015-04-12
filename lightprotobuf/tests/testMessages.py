

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
	
		


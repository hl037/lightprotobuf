

import unittest
from lightprotobuf import *
from io import *
from inspect import isclass

class Repeated(Message):
	r = Field(1, Int32, Field.REPEATED)

class TestReapeated(unittest.TestCase):
	def test_list_append(self):
		m = Repeated()
		nb = [1,2,3,4]
		for i in nb:
			m.r.append(i)
		l = list(m.r)
		self.assertEqual(l, nb)
	
	def test_list_swap(self):
		m = Repeated()
		nb = [1,2,3,4]
		m.r = nb
		l = list(m.r)
		self.assertEqual(l, nb)
	
	def test_list_errors(self):
		nb1 = [1,2,"t"]
		nb2 = ["t",2,1]
		with self.assertRaises(Exception):
			m = Repeated()
			for i in nb1:
				m.r.append(i)
		with self.assertRaises(Exception):
			m = Repeated()
			for i in nb2:
				m.r.append(i)
		with self.assertRaises(Exception):
			m = Repeated()
			m.r = nb1
		with self.assertRaises(Exception):
			m = Repeated()
			m.r = nb2
	
	def test_encode(self):
		m = Repeated()
		nb = [1,2,3,150]
		m.r = nb
		b = io.BytesIO()
		Repeated.to_stream(b, m)
		self.assertEqual(bytes(b.getbuffer()), b'\x09\x08\x01\x08\x02\x08\x03\x08\x96\x01')
	
	def test_decode(self):
		nb = [1,2,3,150]
		b = io.BytesIO(b'\x09\x08\x01\x08\x02\x08\x03\x08\x96\x01')
		m = Repeated.from_stream(b)
		self.assertEqual(list(m.r), nb)


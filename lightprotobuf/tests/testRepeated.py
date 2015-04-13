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
		# 09 bytes following
		# 08 = 1 << 3 | 0
		# varints etc.
	
	def test_encode_packed(self):
		class Repeated(Message):
			r = Field(1, Int32, Field.REPEATED, packed="True")
		m = Repeated()
		nb = [1,2,3,150]
		m.r = nb
		b = io.BytesIO()
		Repeated.to_stream(b, m)
		self.assertEqual(bytes(b.getbuffer()), b'\x07\x0A\x05\x01\x02\x03\x96\x01')
		# 07 bytes following
		# 0A = 1 << 3 | 2
		# 05 bytes following
		# concatened varints etc.

	def test_decode(self):
		nb = [1,2,3,150]
		b = io.BytesIO(b'\x09\x08\x01\x08\x02\x08\x03\x08\x96\x01')
		m = Repeated.from_stream(b)
		self.assertEqual(list(m.r), nb)

	def test_decode_packed(self):
		class Repeated(Message):
			r = Field(1, Int32, Field.REPEATED, packed="True")
		nb = [1,2,3,150]
		b = io.BytesIO(b'\x07\x0A\x05\x01\x02\x03\x96\x01')
		m = Repeated.from_stream(b)
		self.assertEqual(list(m.r), nb)

	def test_decode_mixed(self):
		class Repeated(Message):
			r = Field(1, Int32, Field.REPEATED, packed="True")
		nb = [1,150,1,2,3,150]
		b = io.BytesIO(b'\x0C\x08\x01\x08\x96\x01\x0A\x05\x01\x02\x03\x96\x01')
		m = Repeated.from_stream(b)
		self.assertEqual(list(m.r), nb)
		# 0C (12) bytes following
		# 08 = 1 << 3 | 0
		# varints etc.
		# 0A = 1 << 3 | 2
		# 05 bytes following
		# concatened varints etc.


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

import struct
import io
from enum import IntEnum

mask_64      = 0xffffffffffffffff
mask_63      = 0x7fffffffffffffff
mid_64       = 0x8000000000000000
mask_32      = 0xffffffff
mask_31      = 0x7fffffff
mid_32       = 0x80000000
mid_8        = 0x80
mask_3       = 0x7

class FieldNotOptional(RuntimeError):
	pass

class NumberOverflowException(ValueError):
	pass

def compl2_64(value):
	"""
	return the 2's complement of value in 64b.
	"""
	return ((value ^ mask_64) + 1)

def compl2_32(value):
	"""
	return the 2's complement of value in 32b.
	"""
	return ((value ^ mask_32) + 1)

def max_for_length(nbbits):
	return 1 << nbbits

class DataType:
	typeid = 0
	@classmethod
	def to_py(cls, value):
		return value
	@classmethod
	def from_py(cls, value):
		return value


###############################################################################
															 # Varint related #
###############################################################################


class UVarint(DataType):
	typeid = 0
	length = 0
	@classmethod
	def assert_not_overflow(cls, value):
		if value < 0 or (cls.length and value >= max_for_length(cls.length * 8)):
			raise NumberOverflowException('{1} not in range [{0}, {2}['.format(
				0,
				value,
				max_for_length(cls.length * 8)))
	
	@classmethod
	def encode(cls, value):
		assert(value >= 0)
		if cls.length:
			assert(value < max_for_length(cls.length * 8))
		if value == 0:
			return bytearray([0])
		b = bytearray()
		while value != 0:
			b.append(128 | (value % 128))
			value = value // 128
		b[-1] = b[-1] & 127
		return b
	
	@classmethod
	def decode(cls, data):
		value = 0
		i = 0
		for b in data:
			value += (b % 128) << (i * 7)
			i += 1
		cls.assert_not_overflow(value)
		return value
	
	@classmethod
	def to_stream(cls, stream, value):
		bs = cls.encode(value)
		if stream.write(bs) != len(bs):
			raise IOError('Bytes not written')
	
	@classmethod
	def from_stream(cls, stream):
		bs = bytearray()
		b = stream.read(1)
		if len(b) != 1:
			raise IOError('Unexpected read bytes length ({})'.format(len(b)))
		bs.append(b[0])
		while b[0] & mid_8:
			b = stream.read(1)
			if len(b) != 1:
				raise IOError('Unexpected read bytes length')
			bs.append(b[0])
		return cls.decode(bs)
	
	@classmethod
	def to_py(cls, value):
		return value
	
	@classmethod
	def from_py(cls, value):
		value = int(value)
		cls.assert_not_overflow(value)
		return value



class Varint(UVarint):
	typeid = 0
	length = 8
	@classmethod
	def assert_not_overflow(cls, value):
		pass
	@classmethod
	def assert_not_negative_overflow(cls, value):
		m = max_for_length(cls.length * 8 -1)
		if( -m > value or value >= m):
			raise NumberOverflowException('{1} not in range [{0}, {2}['.format(
				-m,
				value,
				m))
		
	@classmethod
	def encode(cls, value):
		if cls.length :
			m = max_for_length(cls.length * 8 -1)
			assert(-m <= value and value < m)
		if value < 0:
			# Always encoded as 64b value
			value = compl2_64((-value) & mask_64)
		else :
			value = value & mask_63
		return super().encode(value)
	
	@classmethod
	def decode(cls, data):
		# To remove extra bits
		value = super().decode(data)
		if value >= mid_64:
			value = -compl2_64(value)
		cls.assert_not_negative_overflow(value)
		return value
	def from_py(cls, value):
		value = int(value)
		cls.assert_not_overflow(value)
		return value
	
	@classmethod
	def from_py(cls, value):
		value = int(value)
		cls.assert_not_negative_overflow(value)
		return value



class ZZVarint(Varint):
	typeid = 0
	@classmethod
	def encode(cls, value):
		if value < 0:
			value = value * (-2) - 1
		else:
			value = value * 2
		return super().encode(value)
	
	@classmethod
	def decode(cls, data):
		value = super().decode(data)
		if value % 2 == 1:
			value = (value + 1) // (-2)
		else:
			value = value // 2
		return value

###############################################################################

class Bool(UVarint):
	length = 1
	@classmethod
	def assert_not_overflow(cls, value):
		pass
	@classmethod
	def to_py(cls, value):
		return bool(value)
	@classmethod
	def from_py(cls, value):
		return 1 if value else 0

class UInt32(UVarint):
	length = 4

class UInt64(UVarint):
	length = 8

class Int32(Varint):
	length = 4

class Int64(Varint):
	length = 8

class SInt32(ZZVarint): 
	length = 4

class SInt64(ZZVarint):
	length = 8
		

###############################################################################
															 # Bytes-related #
###############################################################################


class Bytes(DataType):
	typeid = 2
	@classmethod
	def to_stream(cls, stream, value):
		l = len(value)
		UVarint.to_stream(stream, l)
		if stream.write(value) != l:
			raise IOError('Bytes not written')
	@classmethod
	def from_stream(cls, stream):
		l = UVarint.from_stream(stream)
		bs = bytes()
		while len(bs) < l:
			bs = bs + stream.read(l - len(bs))
		return bs
	@classmethod
	def from_py(cls, value):
		return bytes(value)

class String(Bytes):
	@classmethod
	def to_stream(cls, stream, value):
		super().to_stream(stream, value.encode('UTF-8'))
	@classmethod
	def from_stream(cls, stream):
		return super().from_stream(stream).decode('UTF-8')
	@classmethod
	def from_py(cls, value):
		return str(value)


###############################################################################
														 # Fixed Byte length #
###############################################################################


class Fixed(Bytes):
	@classmethod
	def to_stream(cls, stream, value):
		bs = cls.encode(value)
		if len(bs) != cls.length:
			raise IndexError('Encoded length not matching class length')
		if stream.write(bs) != len(bs):
			raise IOError('Bytes not written')
	@classmethod
	def from_stream(cls, stream):
		bs = bytes()
		while len(bs) < cls.length:
			bs = bs + stream.read(cls.length - len(bs))
		return cls.decode(bs)

class F64:
	typeid = 1
	length = 8

class F32:
	typeid = 5
	length = 4

class PackedNumber:
	fmt = ''
	@classmethod
	def encode(cls, value):
		try:
			return struct.pack(cls.fmt, value)
		except:
			raise TypeError
	@classmethod
	def decode(cls, data):
		return struct.unpack(cls.fmt, data)[0]

###############################################################################

class Fixed64(F64, Fixed):
	@classmethod
	def encode(cls, value):
		lo = value & mask_32
		hi = value >> 32
		try:
			return struct.pack('<II', lo, hi)
		except:
			raise TypeError
	@classmethod
	def decode(cls, data):
		lo, hi = struct.unpack('<II', data)
		return lo + (hi << 32)
	@classmethod
	def from_py(cls, value):
		value = int(value)
		if value < 0 or value >= 2**(cls.length*8):
			raise NumberOverflowException('{1} not in range [{0}, {2}['.format(
				0,
				value,
				2**(cls.length*8)))
		return value

class SFixed64(F64, Fixed):
	@classmethod
	def encode(cls, value):
		if value < 0:
			value = compl2_64(-value)
		return Fixed64.encode(value)
	@classmethod
	def decode(cls, data):
		value = Fixed64.decode(data)
		if value >= mid_64:
			value = -compl2_64(value)
		return value
	@classmethod
	def from_py(cls, value):
		value = int(value)
		m = 2**(cls.length*8-1)
		if value < -m or value >= m:
			raise NumberOverflowException('{1} not in range [{0}, {2}['.format(
				-m,
				value,
				m))
		return value

class Double(F64, PackedNumber, Fixed):
	fmt = '<d'
	@classmethod
	def from_py(cls, value):
		return float(value)

class Float(F32, PackedNumber, Fixed):
	fmt = '<f'
	@classmethod
	def from_py(cls, value):
		return float(value)

class Fixed32(F32, PackedNumber, Fixed):
	fmt = '<I'
	@classmethod
	def from_py(cls, value):
		value = int(value)
		if value < 0 or value >= 2**(cls.length*8):
			raise NumberOverflowException('{1} not in range [{0}, {2}['.format(
				0, 
				value,
				2**(cls.length*8)))
		return value

class SFixed32(Fixed32):
	@classmethod
	def encode(cls, value):
		if value < 0:
			value = compl2_32(-value)
		return Fixed32.encode(value)
	@classmethod
	def decode(cls, data):
		value = Fixed32.decode(data)
		if value >= mid_32:
			value = -compl2_32(value)
		return value
	@classmethod
	def from_py(cls, value):
		value = int(value)
		m = 2**(cls.length*8-1)
		if value < -m or value >= m:
			raise NumberOverflowException('{1} not in range [{0}, {2}['.format(
				-m,
				value,
				m))
		return value


default_types = {
		0 : UVarint,
		1 : Fixed64,
		2 : Bytes,
		5 : Fixed32,
	}


class EnumFieldType(Varint):
	enum = IntEnum(value='EmptyEnum', names = dict())
	@classmethod
	def decode(cls, data):
		value = Varint.decode(data)
		cls.enum(value)
		return value
	@classmethod
	def to_py(cls, value):
		return cls.enum(value)
	@classmethod
	def from_py(cls, value):
		if not value in cls.enum:
			raise TypeError('{} is not a {} value'.format(repr(value), cls.enum.__name__))
		return int(value)


class InvalidFieldRuleException(Exception):
	pass


class Array:
	def __init__(self, tag):
		self.list = []
		self.tag = tag
		self.field = tag.field
		self.packed = self.field.attributes.get("packed", "false")
		self.packed = True if self.packed.lower() == "true" else False
	
	def __len__(self):
		return self.list.__len__()
	
	def __length_hint__(self):
		return self.list.__length_hint__()
	
	def __getitem__(self, key):
		return self.field.datatype.to_py(self.list.__getitem__(key))
	
	def __missing__(self, key):
		return self.list.__missing__(key)
	
	def __setitem__(self, key, value):
		return self.list.__setitem__(key, self.field.datatype.from_py(value))
	
	def __delitem__(self, key):
		return self.list.__delitem__(key)
	
	def __iter__(self):
		return self.list.__iter__()
	
	def __reversed__(self):
		return self.list.__reversed__(self)
	
	def __contains__(self,item):
		return self.list.__contains__(self.field.datatype.from_py(item))
	
	def swap(self, l):
		checked = [ self.field.datatype.from_py(x) for x in l ]
		l = self.get_as_list()
		self.list = checked
		return l
	
	def get_as_list(self):
		return [ self.field.datatype.to_py(x) for x in self.list ]
	
	def append(self, value):
		return self.list.append(self.field.datatype.from_py(value))
	
	def from_stream(self, stream, index=None):
		if self.packed and (index is None or index != self.field.index()):
			array = Bytes.from_stream(stream)
			length = len(array)
			b = io.BytesIO(array)
			while b.tell() < length:
				self.list.append(self.field.datatype.from_stream(b))
		else:
			self.list.append(self.field.datatype.from_stream(stream))
	
	def to_stream(self, stream):
		if self.packed:
			b = io.BytesIO()
			for i in self.list:
				self.field.datatype.to_stream(b, i)
			UVarint.to_stream(stream, self.field.tag << 3 | Bytes.typeid)
			Bytes.to_stream(stream, b.getvalue())
		else:
			for i in self.list:
				UVarint.to_stream(stream, self.field.index())
				self.field.datatype.to_stream(stream, i)


class Field:
	REQUIRED = 0
	OPTIONAL = 1
	REPEATED = 2
	def __init__(self, tag, datatype, rule=0, **attributes):
		if rule not in [ Field.REQUIRED, Field.OPTIONAL, Field.REPEATED ]:
			raise InvalidFiledRuleException
		self.tag = tag
		if issubclass(datatype, IntEnum):
			self.datatype = type(datatype.__name__+'Field', (EnumFieldType,), dict(enum = datatype))
		elif issubclass(datatype, DataType):
			self.datatype = datatype
		else:
			raise TypeError('Datatype should be either an IntEnum or a subclass of DataType')
		self.rule = rule
		self.attributes = attributes
	
	def __get__(self, instance, owner):
		if instance is None:
			return self
		return instance._tags[self.tag].getValue()
	
	def __set__(self, instance, value):
		instance._tags[self.tag].setValue(value)
	
	def index(self):
		return self.tag << 3 | self.datatype.typeid
	


class Tag:
	def __init__(self, field):
		self.field = field
		if field.rule == field.REPEATED:
			self.value = Array(self)
		else:
			self.value = None
	
	def getValue(self):
		if self.field.rule is Field.REPEATED:
			return self.value
		else:
			return self.field.datatype.to_py(self.value)
	
	def setValue(self, value):
		if self.field.rule is Field.REPEATED:
			self.value.swap(value)
		else:
			self.value = self.field.datatype.from_py(value)


class MessageMeta(type):
	def __init__(cls, name, bases, attrs):
		cls.fields = dict()
		for k, v in attrs.items():
			if isinstance(v, Field):
				cls.fields[k] = v
				v.name = k
		return super(MessageMeta, cls).__init__(name, bases, attrs)


class Message(DataType, metaclass = MessageMeta):
	typeid = 2
	def __init__(self):
		self._tags = dict()
		for field in self.fields.values():
			self._tags[field.tag] = Tag(field)
	
	@classmethod
	def from_stream_root(cls, stream):
		index = UVarint.from_stream(stream)
		self = cls()
		while index != mask_3:
			tag, typeid = index >> 3, index & mask_3
			if tag not in self._tags:
				default_types[typeid].from_stream(stream)
			else:
				F = self._tags[tag].field
				if F.rule is Field.REPEATED:
					self._tags[tag].value.from_stream(stream, index)
				else:
					T = F.datatype
					if F.datatype.typeid != typeid:
						default_types[typeid].from_stream(stream)
					else:
						self._tags[tag].value = T.from_stream(stream)
			index = UVarint.from_stream(stream)
		return self
	
	@classmethod
	def from_stream(cls, stream):
		b = Bytes.from_stream(stream) + bytes([mask_3])
		return cls.from_stream_root(io.BytesIO(b))
	
	@classmethod
	def to_stream_root(cls, stream, value):
		for i, tag in value._tags.items():
			F = tag.field
			T = F.datatype
			if F.rule == Field.REPEATED:
				tag.value.to_stream(stream)
			elif tag.value is not None:
				UVarint.to_stream(stream, F.index())
				T.to_stream(stream, tag.value)
			elif F.rule is Field.REQUIRED:
				raise FieldNotOptional('Field {} in {} is not optional'.format(F.name, cls.__name__))
	
	@classmethod
	def to_stream(cls, stream, value):
		b = io.BytesIO()
		cls.to_stream_root(b, value)
		Bytes.to_stream(stream, b.getvalue())


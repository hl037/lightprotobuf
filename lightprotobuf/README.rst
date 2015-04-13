lightprotobuf
=======================

Introduction
------------

lightprotobuf is a full Python 3 implementation of the Protocol Buffers as described by Google.

Documentation
=============

The main class to use is lightprotobuf.Message

It must be the base class of every messages you define. The rest follows the .proto design:

This message::

   enum FooEnum {
      FIELD = 5;
      FIELD2 = 6;
   }
   
   message FooMsg {
      required int32 foo_field = 1;
      optional FooEnum foo_enum = 2;
      enum BarEnum {
         FIELD = 5;
         BAR = 6;
      }
      required BarEnum bar_enum = 3;
      repeated string foo_rep = 4;
      repeated int32 foo_pak = 5 [packed=true];
   }
   
   message BarMsg {
      required FooMsg.BarEnum bar_enum = 1;
   }


Is translated in python to::

   from enum import IntEnum
   from lightprotobuf import *
   class FooEnum(IntEnum):
   	FIELD = 5
   	FIELD2 = 6
   
   class FooMsg(Message):
   	class BarEnum(IntEnum):
   		FIELD = 5
   		BAR = 6
   	foo_field = Field(1, Int32, Field.REQUIRED, **{})
   	bar_enum = Field(3, BarEnum, Field.REQUIRED, **{})
   	foo_enum = Field(2, FooEnum, Field.OPTIONAL, **{})
   
   class BarMsg(Message):
   	bar_enum = Field(1, FooMsg.BarEnum, Field.REQUIRED, **{})


As you can see, the fields follow this template ::

   <name> = Field(<tag number>, <type>, Field.<REQUIRED|OPTIONEL|REPEATED>, **{<options as a dict (optional)>}

Enums are python's ``enum.IntEnum``

Nested types are real python nested types referenced just like in .proto

API
---

The fields are actually transformed as attributes via descriptors. So you can access fields easily::

    m = FooMsg()
    m.foo_field = 5
    m.foo_field # returns 5
    m.foo_enum = 5 # Error because it expects a FooEnum object
    m.foo_enum = FooEnum.FIELD # OK
    m.bar_enum = FooMsg.BarEnum.BAR # OK

Repeated fields atc like a list::

    m.foo_rep = ["a string", "another"] # OK
    li = m.foo_rep # Get a reference to the list
    li.append("a string") # OK, append the string
    li.append(b'a bytes') # TypeError because there is a check to avoid mistakes


Note : packed fields are able to decode either data packed either multiple occurence of the field e.g. the test case::

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


To encode a message, lightprotobuf uses stream objects : each DataType has a ``to_stream`` and ``from_stream`` class method. Just to call it from a message to encode/decode a message::

   import io
   s = io.BytesIO()
   Message.to_stream(s, m)
   s.getvalue() # b'\x06\x08\x05\x10\x05\x18\x06'

   m = FooMsg()
   s = io.BytesIO(b'\x06\x08\x05\x10\x05\x18\x06')
   m = Message.from_stream(s)
   
_Note_ : if required field is missing, it raises a FieldNotOptional exception

Release Notes
=============

1.0.b3
------

- WARNING : module moved at top-level. Use `import lightprotobuf` rather than `from lightprotobuf import lightprotobuf`
- Add support for repeated fields, packed and not packed

1.0.b2
------

- Remove DESCRIPTION.rst because duplicate of README.rst
  

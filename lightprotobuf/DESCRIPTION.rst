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
   }
   
   message BarMsg {
      required FooMsg.BarEnum bar_enum = 1;
   }


Is translated in python with::

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

As you can see, the fields follows this template ::

   <name> = Field(<tag number>, <type>, Field.<REQUIRED|OPTIONEL|REPEATED>, **{<options as a dict (optional)>}

Enums are python's ``enum.IntEnum``

Nested type are reals python nested types referenced just like in .proto

Interface
---------

The fields are actually transformed as attribute via descriptors. So you can access fields easily::

    m = FooMsg()
    m.foo_field = 5
    m.foo_field # returns 5
    m.foo_enum = 5 # Error because it expects a FooEnum object
    m.foo_enum = FooEnum.FIELD # OK
    m.bar_enum = FooMsg.BarEnum.BAR # OK

Repeated fields expect iterables.

To encode a message, lightprotobuf uses stream objects : each DataType has a ``to_stream`` and ``from_stream`` class method. Just to call it from a message to encode/decode a message::

   import io
   s = io.BytesIO()
   Message.to_stream(s, m)
   s.getvalue() # b'\x06\x08\x05\x10\x05\x18\x06'

   m = FooMsg()
   s = io.BytesIO(b'\x06\x08\x05\x10\x05\x18\x06')
   m = Message.from_stream(s)
   
_Note_ : if required field is missing, it raises a FieldNotOptional exception



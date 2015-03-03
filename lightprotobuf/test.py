
from lightprotobuf import *
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

m = FooMsg()
m.foo_field = 5
m.foo_enum = FooEnum(5)
m.bar_enum = FooMsg.BarEnum.BAR


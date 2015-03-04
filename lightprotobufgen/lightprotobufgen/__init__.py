# Copyright © 2015 Léo Flaventin Hauchecorne
# 
# This file is part of lightprotobuf.
# 
# lightprotobuf is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# lightprotobuf is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with lightprotobuf.  If not, see <http://www.gnu.org/licenses/>


from antlr4 import *

try:
	from lightprotobufgen.protobufListener import protobufListener as BaseProtobufListener
	from lightprotobufgen.protobufLexer import protobufLexer as ProtobufLexer
	from lightprotobufgen.protobufParser import protobufParser as ProtobufParser
	from lightprotobufgen.lightprotobufgen import ProtobufListener, main, _main
except ImportError:
	from protobufListener import protobufListener as BaseProtobufListener
	from protobufLexer import protobufLexer as ProtobufLexer
	from protobufParser import protobufParser as ProtobufParser
	from lightprotobufgen import ProtobufListener, main, _main

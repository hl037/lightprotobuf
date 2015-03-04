#!/bin/python
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
from .protobufListener import protobufListener as BaseListener
from .protobufLexer import protobufLexer as Lexer
from .protobufParser import protobufParser as Parser
import sys
import logging
import functools
import itertools

logging.basicConfig(level=30)
log = logging.getLogger(__name__)
log.setLevel(0)

modifiers = {
		'required': 'Field.REQUIRED',
		'optional': 'Field.OPTIONAL',
		'repeated': 'Field.REPEATED',
	}

class BaseType:
	def __init__(self, name):
		self.name = name
		self.path = name

class Message:
	def __init__(self):
		self.fields = dict()
		self.types = dict()
	def toString(self, indent = ''):
		return '{0}class {1}(Message):\n{2}{3}'.format(
				indent,
				self.name,
				''.join(x.toString(indent+'\t') for x in self.types.values()),
				''.join(x.toString(indent+'\t') for x in self.fields.values())
			)

class Field:
	def __init__(self):
		self.opt = dict()
	def toString(self, indent = ''):
		return '{}{} = Field({}, {}, {}, **{})\n'.format(
				indent,
				self.name,
				self.tag,
				ProtobufListener.getScopedPath(self.parent, self.type),
				self.modifier,
				self.opt.__str__()
			)

class EnumVar:
	def toString(self, indent = ''):
		return '{}{} = {}\n'.format(
				indent,
				self.name,
				self.value
			)

class EnumType:
	def __init__(self):
		self.vars = []
		self.opt = dict()
	def toString(self, indent = ''):
		return '{0}class {1}(IntEnum):\n{2}'.format(
				indent,
				self.name,
				''.join(x.toString(indent+'\t') for x in self.vars)
			)

class OptionBody:
	pass

class FieldOption:
	pass

class ExistingError(RuntimeError):
	pass

class ProtobufListener(BaseListener):
	def __init__(self):
		self.stack = [None]
		self.types = {
				'double' : BaseType('Double'),
				 'float' : BaseType('Float'),
				 'int32' : BaseType('Int32'),
				 'int64' : BaseType('Int64'),
				'uint32' : BaseType('UInt32'),
				'uint64' : BaseType('UInt64'),
				'sint32' : BaseType('SInt32'),
				'sint64' : BaseType('SInt64'),
			 'fixed32' : BaseType('Fixed32'),
			 'fixed64' : BaseType('Fixed64'),
			'sfixed32' : BaseType('SFixed32'),
			'sfixed64' : BaseType('SFixed64'),
					'bool' : BaseType('Bool'),
				'string' : BaseType('String'),
				 'bytes' : BaseType('Bytes')
			}
		self.userTypes = []
	def getType(self, name):
		i = -1
		item = self.get(i)
		while item is not None:
			if isinstance(item, Message):
				if name in item.types:
					return item.types[name]
			i = i-1
			item = self.get(i)
		if name in self.types:
			return self.types[name]
		else:
			return None
	
	def regType(self, type):
		i = -1
		item = self.get(i)
		n = type.name
		while item is not None:
			if isinstance(item, Message):
				if n in item.types:
					raise ExistingError('{} already defined in {}'.format(n, item.path))
				else:
					item.types[n] = type
				n = item.name + '.' + n
			i = i-1
			item = self.get(i)
		if n in self.types:
			raise ExistingError('{} already defined in global scope'.format(n))
		else:
			self.types[n] = type
		type.path = n
		if type.path == type.name:
			self.userTypes.append(type)
	
	@staticmethod
	def getScopedPath(tscope, t):
		i = 1
		cut = 0
		for c1, c2 in zip(tscope.path+'.', t.path+'.'):
			if c1 != c2:
				break
			if c1 == '.':
				cut = i
			i = i + 1
		return t.path[cut:]
	
	def get(self, i):
		return self.stack[i]
	
	def push(self, val):
		self.stack.append(val)
	
	def pop(self):
		return self.stack.pop()
	
	def enterProto_rule(self, ctx):
		log.info('Enter protobuf : %s', ctx.getText())
	
	def enterImport_rule(self, ctx):
		raise NotImplementedError("imports are not supported yet")

	def enterExtend_rule(self, ctx):
		raise NotImplementedError("extends are not supported yet")

	def enterEnum_rule(self, ctx):
		toks = ctx.getTokens(Parser.IDENT)
		e = EnumType()
		e.name = str(toks[0])
		p = self.get(-1)
		if self.getType(e.name) is not None :
			raise ExistingError('{} names an existing type'.format(m.name))
		log.info('Enter enum %s', e.name)
		self.push(e)
	
	def exitEnum_rule(self, ctx):
		e = self.pop()
		self.regType(e)
		log.info('Leaving message %s', e.name)
	
	def enterEnumField_rule(self, ctx):
		v = EnumVar()
		v.name = ctx.getTokens(Parser.IDENT)[0]
		v.value = ctx.getTokens(Parser.INT_LIT)[0]
		log.info('Enter enum field %s', v.name)
		e = self.get(-1)
		e.vars.append(v)

	def enterPasckage_rule(self, ctx):
		pass
	
	def enterMessage_rule(self, ctx):
		toks = ctx.getTokens(Parser.IDENT)
		m = Message()
		m.name = str(toks[0])
		p = self.get(-1)
		if self.getType(m.name) is not None :
			raise ExistingError('{} names an existing type'.format(m.name))
		log.info('Enter message %s', m.name)
		self.push(m)
	
	def exitMessage_rule(self, ctx):
		m = self.pop()
		self.regType(m)
		log.info('Leaving message %s', m.name)
	
	def enterMessageBody_rule(self, ctx):
		log.info('Enter message body %s', self.stack[-1].name)
	
	def enterGroup_rule(self, ctx):
		raise DeprecationWarning('Groups are deprecated')
	
	def enterField_rule(self, ctx):
		f = Field()
		f.name = ctx.getTokens(Parser.IDENT)[0]
		f.tag = ctx.getTokens(Parser.INT_LIT)[0]
		log.info('Enter field %s', f.name)
		m = self.get(-1)
		m.fields[f.name] = f
		f.parent = m
		self.push(f)
	
	def exitField_rule(self, ctx):
		self.pop()
	
	def enterModifier_rule(self, ctx):
		f = self.get(-1)
		f.modifier = modifiers[ctx.getText()]
		log.info('Enter modifier %s for field %s', f.modifier, f.name)
	
	def enterType_rule(self, ctx):
		f = self.get(-1)
		f.type = self.getType(ctx.getText())
		log.info('Enter type %s for field %s', f.type.name, f.name)
	
	def enterOptionBody_rule(self, ctx):
		self.push(OptionBody())
		log.info('Enter option body: %s', ctx.getText())
	
	def exitOptionBody_rule(self, ctx):
		opt = self.pop()
		f = self.get(-1)
		f.opt[opt.dotIdent] = opt.constant
	
	def enterDotIdent_rule(self, ctx):
		self.get(-1).dotIdent = ctx.getText()
		log.info('Enter dotIdent: %s', ctx.getText())
	
	def enterConstant_rule(self, ctx):
		self.get(-1).constant = ctx.getText()
		log.info('Enter Constant: %s', ctx.getText())


def main(argv):
	input = FileStream(argv[1])
	lexer = Lexer(input)
	stream = CommonTokenStream(lexer)
	parser = Parser(stream)
	tree = parser.proto_rule()
	walker = ParseTreeWalker()
	listener = ProtobufListener()
	walker.walk(listener, tree)
	
	print('from enum import IntEnum')
	print('from lightprotobuf import *')
	print()
	for m in listener.userTypes:
		print(m.toString())

def _main():
	main(sys.argv)

if __name__ == '__main__':
	_main()


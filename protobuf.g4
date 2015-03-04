grammar protobuf;

proto_rule  : ( message_rule | extend_rule | enum_rule | import_rule | package_rule | option_rule | ';' )* EOF;

import_rule : 'import' STR_LIT ';' ;

package_rule : 'package' IDENT ';' ;

option_rule : 'option' optionBody_rule ';' ;

optionBody_rule : dotIdent_rule '=' constant_rule ; //semantically, dotIdent_rule is not a type. 

message_rule : 'message' IDENT messageBody_rule ;

extend_rule : 'extend' dotIdent_rule messageBody_rule ;

enum_rule : 'enum' IDENT '{' ( option_rule | enumField_rule | ';' )* '}' ;

enumField_rule : IDENT '=' INT_LIT ';' ;

service_rule : 'service' IDENT '{' ( option_rule | rpc_rule | ';' )* '}' ;

rpc_rule : 'rpc' IDENT '(' dotIdent_rule ')' 'returns' '(' dotIdent_rule ')' ';' ;

messageBody_rule : '{' ( field_rule | enum_rule | message_rule | extend_rule | extensions_rule | group_rule | option_rule | ':' )* '}' ;

group_rule : modifier_rule 'group' CAMEL_IDENT '=' INT_LIT messageBody_rule ;

field_rule : modifier_rule type_rule IDENT '=' INT_LIT ( '[' optionBody_rule ( ',' optionBody_rule )* ']' )? ';' ;

extensions_rule : 'extensions' INT_LIT 'to' ( INT_LIT | 'max' ) ';' ;

modifier_rule : 'required' | 'optional' | 'repeated' ;

type_rule : 'double' | 'float' | 'int32' | 'int64' | 'uint32' | 'uint64'
       | 'sint32' | 'sint64' | 'fixed32' | 'fixed64' | 'sfixed32' | 'sfixed64'
       | 'bool' | 'string' | 'bytes' | dotIdent_rule ;

dotIdent_rule : IDENT ('.' IDENT)* ;

constant_rule : IDENT | INT_LIT | FLOAT_LIT | STR_LIT | BOOL_LIT ;

IDENT : [A-Za-z_][A-Za-z0-9_]* ;

CAMEL_IDENT : [A-Z][A-Za-z0-9_]* ;

INT_LIT : DEC_INT | HEX_INT | OCT_INT ;

DEC_INT : [0-9]+ ;

HEX_INT : '0'[xX]([A-Fa-f0-9])+ ;

OCT_INT : '0'[0-7]+ ;

FLOAT_LIT : [0-9]+('.'[0-9]+)?([Ee][\\+-]?[0-9]+)? ;

BOOL_LIT : 'true' | 'false' ;

STR_LIT : QUOTE ( HEX_ESCAPE | OCT_ESCAPE | CHAR_ESCAPE | [^\0\n] )* QUOTE ;

QUOTE : ["'] ;

HEX_ESCAPE : '\\'[Xx][A-Fa-f0-9][A-Fa-f0-9]?;

OCT_ESCAPE : '\\0'?[0-7]{1,3} ;

CHAR_ESCAPE : '\\'[abfnrtv\\?'"] ;

WS: [ \t\r\n]+ -> skip;


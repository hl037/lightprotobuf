
MKFILE_PATH = $(abspath $(lastword $(MAKEFILE_LIST)))
CDIR = $(patsubst %/,%,$(dir $(MKFILE_PATH)))
GEN_PATH = $(CDIR)/lightprotobufgen/lightprotobufgen

FILES = Parser Listener Lexer
GEN = $(foreach i,$(FILES), $(GEN_PATH)/protobuf$(i).py)
R = $(foreach i,$(FILES), $(GEN_PATH)/%$(i).py)

.PHONY: all

all: $(GEN)

$(R) : %.g4
	mkdir -p $(GEN_PATH)
	antlr4 -Dlanguage=Python3 -o $(GEN_PATH) $<
	rm $(GEN_PATH)/*.tokens

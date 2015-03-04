lightProtobuf
=============

light protobuf is a lightweigth and full Python 3 implementation of google's Protocol buffers.

It is two projects : `lightprotobuf` that is the standalone library to encode/decode protobuf messages, and `lightprotobufgen` that is a .proto parser.

As of today, the `lightprotobuf` library is almost fully tested and working. It supports all type defiend in the protocol and any kind message can be described as python class and enum.
The only missing feature (and will be added in next release) is the default value.

However, the `lightprotobufgen` tool is under development and doesn't cover the whole specification of `*.proto` files. However, you can use it yet on single file message (see the lightprotobufgen directory for more explanations.)

The both package are available from pip for installation ::

   pip install lightprotobuf
   pip install lightprotobufgen

*NOTE* that lightprotobufgen depends on antlr>=4.5 framework


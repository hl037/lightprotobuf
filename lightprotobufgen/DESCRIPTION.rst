lightprotobufgen
================

Introduction
------------

lightprotobufgen is a commandline tool based on antlr4.5 to generate `lightprotobuf` compatible messages from a `*.proto` file.

usage ::

   lightprotobufgen <file.proto>

The script output on stdout it's result

Current limitations
-------------------

The tool is still in developpment and some features of official .proto format are not implemented yet :
   - import : imports statments generates an exception. you still can merge manually different files
   - global options : the global options are not supported yet
   - unique enum : will be implemented in next release
   - extends : Message extend are not implemented since it's mostly usefull with imports and they are not supported yet
   - packages : Like google official implementation, it won't be implemented because python use the file paths as modules/package

The 1.0 release will implement the full .proto specifications.

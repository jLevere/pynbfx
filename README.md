# pynbfx
Python support for [MC-NBFX]: .NET Binary Format: XML Data Structure


## Status:

This is an ongoing hobby project. Only deserialization (parsing) is implemented at the moment, and it is not fully complete. Most things work, but some combinations of nested data structures occasionally exhibit bugs. Additionally, some rarely used data types have not been implemented yet.

Parser combinators lend themselves well to, well, parsing.  And not so much serialization.

**Deserialization:** 90% completed

**Serialization:** 0% completed


## Overview 

This library provides a comprehensive solution for converting XML documents to NBFX and vice versa. By using Python's built-in XML AST structure `ElementTree` as its internal representation, it provides an efficient and clean method of interacting with NBFX data.


## Background

[MC-NBFX] (*.NET Binary Format: XML Data Structure*) is Microsoft's binary serialization protocol for XML documents, primarily used in SOAP-based web services like Active Directory Web Services (ADWS).

### Protocol Architecture

The Microsoft XML binary stack consists of three layered specifications:

1. **[MC-NBFX]** - Base encoding format
2. **[MC-NBFS]** (*.NET Binary Format: SOAP Data Structure*) - Adds static dictionary compression
3. **[MC-NBFSE]** (*.NET Binary Format: SOAP Extension*) - Implements dynamic dictionary synchronization

This library implments [MC-NBFX] and [MC-NBFS] which is somewhat difficult to seperate from [MC-NBFX].

### Key Features

**Record-Based Structure**  
NBFX uses a Type-Length-Value (TLV) structure with 57+ record types for XML components.

The major groups of Record types are:
- `Element` Records
- `Attribute` Records
- `Text` Records

`Text` records contain the actual data such as strings and integers and other values.  `Elements` make up the main structure of the document representing XML elements in every way, having childeren and attributes.  The values of `Elements` and `Attributes` are encoded as `Text` records.

## Parsing

The concept of monadic parser combinators is used extensively in the parsing and serialization library. In functional languages, parser combinators treat each parser as a first-class value, allowing them to be composed in complex ways without sacrificing readability or maintainability.

Even though python is not exactly a functional language, these concepts provide a stable and easy-to-debug method for constructing parsers. By building parsers that encapsulate specific parsing behaviors, they can be easily isolated and tested.

This version has little to no backtracking.


# mkcas

This is a simple tool to make CAS files to be used in different MSX emulators.

It supports the following block types:

 * binary: binary executable data, include loading and execution addresses.
 * basic: tokenized BASIC code.
 * ascii: ASCII text, can be BASIC for example. In case of BASIC code, the CR
   LF is expected as end of line.
 * custom-header: no block type, header with loading address and block length
   followed by the data.
 * custom: no block type, data stored "as-is".

Use `-h` flag to get command line help.

## Requirements

 * Python 3

## The CAS Format

This is a description of the format based on information I've found online, so
is not "official" but my understanding of it.

The file is a sequence of blocks.

Each block starts with the block ID sequence, followed by a header.

### Definitions

Block ID sequence: 0x1f 0xa6 0xde 0xba 0xcc 0x13 0x7d 0x74

Type of block (10 times):

 * 0xd0: binary
 * 0xd3: basic
 * 0xea: ASCII

The filename 6 chars, space padded.

### Binary

Starts with the block ID, followed by the block type and the filename.

Then the block ID is repeated, followed by 3 words (little endian):

 * Starting address: where the file will be loaded in RAM
 * Ending address: starting address + file length - 1
 * Execution address: where to execute the file (if 0, use starting address)

Finally comes the file data.

### Basic

Starts with the block ID, followed by the block type and the filename.

Then the block ID is repeated, followed by tokenized basic data.

### ASCII

Starts with the block ID, followed by the block type and the filename.

The ASCII data is split in 256 bytes chunks, padded with 0x1a. If the ASCII
file size in multiple of 256, needs an extra chunk filled with the padding
character.

The block ID is added before each chunk.


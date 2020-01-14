#!/usr/bin/env python3
#
# Copyright (C) 2020 by Juan J. Martinez <jjm@usebox.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
__version__ = "1.1"

import os
from argparse import ArgumentParser

DEF_ADDR = 0x4000
TYPES = ("binary", "basic", "ascii", "custom-header", "custom")
TYPE_BLOCK = {
    "binary": bytes((0xd0 for _ in range(10))),
    "basic": bytes((0xd3 for _ in range(10))),
    "ascii": bytes((0xea for _ in range(10))),
}

BLOCK_ID = bytes((0x1f, 0xa6, 0xde, 0xba, 0xcc, 0x13, 0x7d, 0x74))


def write_word(fd, word):
    fd.write(bytes((word & 0xff, word >> 8)))


def auto_int(value):
    return int(value, 0)


def main():

    parser = ArgumentParser(description="Make a CAS file for the MSX",
                            epilog="Copyright (C) 2020 Juan J Martinez <jjm@usebox.net>",
                            )

    parser.add_argument("--version", action="version",
                        version="%(prog)s " + __version__)
    parser.add_argument("-a", "--add", dest="add", action="store_true",
                        help="append to the existing CAS file instead of creating a new one")
    parser.add_argument("--name", dest="name", default=None, type=str,
                        help="name to use for the file (limit 6 chars, defaults to the file name)")
    parser.add_argument("--addr", dest="addr", default=DEF_ADDR, type=auto_int,
                        help="address to load if binary file (default: 0x%04x)" % DEF_ADDR)
    parser.add_argument("--exec", dest="exec", default=DEF_ADDR, type=auto_int,
                        help="address to exec if binary file (default: 0x%04x)" % DEF_ADDR)

    parser.add_argument("output", help="target .CAS file")
    parser.add_argument("type", help="file type", choices=TYPES)
    parser.add_argument("file", help="input file")

    args = parser.parse_args()

    if args.add:
        flags = "ab"
    else:
        flags = "wb"

    with open(args.output, flags) as out:

        if args.name:
            name = args.name
        else:
            name = os.path.basename(args.file)

        with open(args.file, "rb") as inf:
            data = inf.read()

        out.write(BLOCK_ID)

        if args.type == "ascii":

            out.write(TYPE_BLOCK[args.type])
            out.write(name[:6].ljust(6).encode("ascii"))

            for b in range(0, len(data), 256):
                out.write(BLOCK_ID)
                out.write(data[b:b+256])

            padding = 256 - (len(data) % 256)
            if padding == 256:
                out.write(BLOCK_ID)
            out.write(bytes((0x1a for _ in range(padding))))

        elif args.type == "basic":

            out.write(TYPE_BLOCK[args.type])
            out.write(name[:6].ljust(6).encode("ascii"))
            out.write(BLOCK_ID)
            out.write(data)

        elif args.type == "binary":

            addr = args.addr
            exec_addr = args.exec
            end_addr = addr + len(data) - 1

            if end_addr > 0xffff:
                parser.error("Binary doesn't fit in memory")

            out.write(TYPE_BLOCK[args.type])
            out.write(name[:6].ljust(6).encode("ascii"))

            out.write(BLOCK_ID)
            write_word(out, addr)
            write_word(out, end_addr)
            write_word(out, exec_addr)

            out.write(data)

        elif args.type == "custom-header":

            addr = args.addr
            length = len(data)

            write_word(out, addr)
            write_word(out, length)
            out.write(data)

        else:
            # custom
            out.write(data)


if __name__ == "__main__":
    main()

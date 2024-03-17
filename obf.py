#!/usr/bin/env python3

import argparse
import sys
import os
import time
import zlib
import base64
import marshal

def encode_mzb(x: str) -> str:
    output = x.encode()
    output = marshal.dumps(output)
    output = zlib.compress(output)
    output = base64.b85encode(output)
    output = output[::-1]

    output = "_1nf3r10r_ = lambda __1nf3r10r__ : __import__('marshal').loads(__import__('zlib').decompress(__import__('base64').b85decode(__1nf3r10r__[::-1])));eval(\"exec((_1nf3r10r_)({}))\")".format(output)

    return output

def encode_zb(x: str) -> str:
    output = x.encode()
    output = zlib.compress(output)
    output = base64.b64encode(output) 
    output = output[::-1]

    output = "_ = lambda __ : __import__('zlib').decompress(__import__('base64').b64decode(__[::-1]));exec((_)({}))".format(output)

    return output

def encode_exec(x: str) -> str:
    output = x.encode()
    output = zlib.compress(output)
    output = base64.b64encode(output)
    output = output[::-1]

    output = "exec((_)({}))".format(output)

    return output

def iteration(x: str, current_iter: int, debug: bool, debug_dir: str | None, max_iter: int) -> str:
    if current_iter > max_iter:
        return x

    if current_iter < max_iter - 11:
        f = encode_exec
    elif current_iter == max_iter - 10:
        f = encode_zb
    else:
        f = encode_mzb

    time_start = time.time_ns()
    encoded = f(x)
    time_stop = time.time_ns()

    elapsed_ms = (time_stop - time_start) // 1_000_000
    if debug:
        print("Iteration {}: {}, took {} ms".format(current_iter, f.__name__, elapsed_ms), file=sys.stderr)

    if debug_dir:
        debug_file = open(os.path.join(debug_dir, str(current_iter) + ".py"), "w")
        debug_file.write(encoded)
        debug_file.close()

    return iteration(encoded, current_iter + 1, debug, debug_dir, max_iter)

def cli(input_filename: str, output_filename: str, debug: bool, debug_dir: str | None, max_iter: int):
    input_file = sys.stdin
    if input_filename not in ["-", "stdin"]:
        input_file = open(input_filename, "r")

    input_source = input_file.read()
    input_file.close()

    ds = iteration(input_source, 1, debug, debug_dir, max_iter)

    output_file = sys.stdout
    if output_filename != "stdout":
        output_file = open(output_filename, "w")

    output_file.write(ds)

    if output_filename != "stdout":
        output_file.close()

def gui(debug: bool):
    print("Work in progress!", file=sys.stderr)
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A script to obfuscate Python scripts")
    parser.add_argument("input", type=str, nargs="?", default="stdin", help="Input filename")
    parser.add_argument("-o", "--output", type=str, default="stdout", help="Output filename (if not existent, will create)")
    parser.add_argument("-i", "--max-iter", type=int, default=400, help="Max iterations")
    parser.add_argument("--gui", action="store_true", help="Enable GUI")
    parser.add_argument("--debug", action="store_true", help="Print debug information")
    parser.add_argument("--debug-dir", type=str, help="Path to the debug directory")
    args = parser.parse_args()

    if args.debug:
        print("args:", args, file=sys.stderr)

    try:
        if args.gui:
            gui(args.debug)
        elif args.input:
            cli(args.input, args.output, args.debug, args.debug_dir, args.max_iter)
        else:
            raise Exception("no input file")
    except Exception as e:
        parser.error(str(e))
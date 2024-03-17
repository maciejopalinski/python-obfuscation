#!/usr/bin/env python3

import argparse
import sys
import os
import time
import ast
import zlib
import base64
import marshal

def decode_mzb(x: str) -> str:
    eval_str: str = ast.parse(x).body[1].value.args[0].value # type: ignore

    bytes_payload: str = ast.parse(eval_str).body[0].value.args[0].args[0].value # type: ignore

    output = bytes_payload[::-1] # type: ignore
    output = base64.b85decode(output) # type: ignore
    output = zlib.decompress(output)
    output = marshal.loads(output)

    return output.decode()

def decode_zb(x: str) -> str:
    eval_str: str = ast.parse(x).body[1].value.args[0].args[0].value # type: ignore

    output = eval_str[::-1] # type: ignore
    output = base64.b64decode(output) # type: ignore
    output = zlib.decompress(output)

    return output.decode()

def decode_exec(x: str) -> str:
    eval_str: str = ast.parse(x).body[0].value.args[0].args[0].value # type: ignore

    output = eval_str[::-1] # type: ignore
    output = base64.b64decode(output) # type: ignore
    output = zlib.decompress(output)

    return output.decode()

def iteration(x: str, current_iter: int, debug: bool, debug_dir: str | None, max_iter: int | None) -> str:
    if max_iter and current_iter > max_iter:
        return x

    if "_1nf3r10r_ = lambda __1nf3r10r__" in x:
        f = decode_mzb
    elif "_ = lambda __" in x:
        f = decode_zb
    elif "exec((_)" in x:
        f = decode_exec
    else:
        return x

    time_start = time.time_ns()
    decoded = f(x)
    time_stop = time.time_ns()

    elapsed_ms = (time_stop - time_start) // 1_000_000
    if debug:
        sys.stderr.write("Iteration {}: {}, took {} ms\n".format(current_iter, f.__name__, elapsed_ms))

        if debug_dir:
            debug_file = open(os.path.join(debug_dir, str(current_iter) + ".py"), "w")
            debug_file.write(decoded)
            debug_file.close()

    return iteration(decoded, current_iter + 1, debug, debug_dir, max_iter)

def remove_comments(x: str) -> str:
    comment_b64 = "JycnCgogICAgaGVhZGVycyA9IHsKICAgICAgICAnYXV0aG9yaXR5JzogJ3d3dy5zaG9ydHVybC5hdCcsCiAgICAgICAgJ2FjY2VwdCc6ICd0ZXh0L2h0bWwsYXBwbGljYXRpb24veGh0bWwreG1sLGFwcGxpY2F0aW9uL3htbDtxPTAuOSxpbWFnZS9hdmlmLGltYWdlL3dlYnAsaW1hZ2UvYXBuZywqLyo7cT0wLjgsYXBwbGljYXRpb24vc2lnbmVkLWV4Y2hhbmdlO3Y9YjM7cT0wLjknLAogICAgICAgICdhY2NlcHQtbGFuZ3VhZ2UnOiAnZW4tSU4sZW47cT0wLjknLAogICAgICAgICdjYWNoZS1jb250cm9sJzogJ21heC1hZ2U9MCcsCiAgICAgICAgIyBSZXF1ZXN0cyBzb3J0cyBjb29raWVzPSBhbHBoYWJldGljYWxseQogICAgICAgICMgJ2Nvb2tpZSc6ICdfZ2E9R0ExLjIuMTg0MTE1NzczNS4xNjYwNTQ2NDM1OyBfZ2lkPUdBMS4yLjE5MjY5NDA5MTUuMTY2MDU0NjQzNTsgX2dhdF9ndGFnX1VBXzMxMzkxMjEwXzQ0PTEnLAogICAgICAgICdkbnQnOiAnMScsCiAgICAgICAgJ29yaWdpbic6ICdodHRwczovL3d3dy5zaG9ydHVybC5hdCcsCiAgICAgICAgJ3JlZmVyZXInOiAnaHR0cHM6Ly93d3cuc2hvcnR1cmwuYXQvJywKICAgICAgICAnc2VjLWZldGNoLWRlc3QnOiAnZG9jdW1lbnQnLAogICAgICAgICdzZWMtZmV0Y2gtbW9kZSc6ICduYXZpZ2F0ZScsCiAgICAgICAgJ3NlYy1mZXRjaC1zaXRlJzogJ3NhbWUtb3JpZ2luJywKICAgICAgICAnc2VjLWZldGNoLXVzZXInOiAnPzEnLAogICAgICAgICd1cGdyYWRlLWluc2VjdXJlLXJlcXVlc3RzJzogJzEnLAogICAgICAgICd1c2VyLWFnZW50JzogJ01vemlsbGEvNS4wIChYMTE7IExpbnV4IGFhcmNoNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS84OC4wLjQzMjQuMTg4IFNhZmFyaS81MzcuMzYgQ3JLZXkvMS41NC4yNTAzMjAnLAogICAgfQoKICAgIGRhdGEgPSB7CiAgICAgICAgJ3UnOiBmJ3tsaW5rfScsCiAgICB9CiAgICAKCiAgICByZXNwb25zZSA9IHJlcXVlc3RzLnBvc3QoJ2h0dHBzOi8vd3d3LnNob3J0dXJsLmF0L3Nob3J0ZW5lci5waHAnLCBjb29raWVzPWNvb2tpZXMsIGhlYWRlcnM9aGVhZGVycywgZGF0YT1kYXRhKQogICAgY2RzID0gcmVzcG9uc2UuY29udGVudAoKICAgICN3aXRoIG9wZW4oJ2luZGV4Lmh0bWwnLCd3JykgYXMgZmlsZXM6CiAgICAjICAgZmlsZXMud3JpdGUoc3RyKGNkcykpCgogICAgc291cCA9IEJlYXV0aWZ1bFNvdXAoY2RzLCdodG1sLnBhcnNlcicpCgogICAgdHJ5OgogICAgICAgIHZhbHVlID0gc291cC5maW5kKCdpbnB1dCcsIHsnaWQnOiAnc2hvcnRlbnVybCd9KS5nZXQoJ3ZhbHVlJykKICAgICAgICByZXR1cm4gdmFsdWUKICAgICAgIAogICAgICAgIAogICAgICAKICAgICAgICAjb3MucmVtb3ZlKCd0aW55dXJscy50eHQnKQogICAgICAgICNvcy5yZW1vdmUoJ2xpbmtzdGlueS50eHQnKQogICAgCiAgICAgICAgCiAgICBleGNlcHQgRXhjZXB0aW9uIGFzIGU6CiAgICAgICAgcHJpbnQoJ1xuJykKICAgICAgICBGcm9udGVudFR5cGluZ0Z1bmN0aW9uKCdVcmwgaXMgaW52YWxpZCAhJykKICAgICAgICBwcmludCgnXG4nKQoKCmRlZiBzaG9ydHVybHNuZXcobGluayk6CiAgICBjb29raWVzID0gewogICAgJ19nYSc6ICdHQTEuMi4xODQxMTU3NzM1LjE2NjA1NDY0MzUnLAogICAgJ19naWQnOiAnR0ExLjIuMTkyNjk0MDkxNS4xNjYwNTQ2NDM1JywKICAgICdfZ2F0X2d0YWdfVUFfMzEzOTEyMTBfNDQnOiAnMScsCiAgICB9CgogICAgaGVhZGVycyA9IHsKICAgICAgICAnYXV0aG9yaXR5JzogJ3d3dy5zaG9ydHVybC5hdCcsCiAgICAgICAgJ2FjY2VwdCc6ICd0ZXh0L2h0bWwsYXBwbGljYXRpb24veGh0bWwreG1sLGFwcGxpY2F0aW9uL3htbDtxPTAuOSxpbWFnZS9hdmlmLGltYWdlL3dlYnAsaW1hZ2UvYXBuZywqLyo7cT0wLjgsYXBwbGljYXRpb24vc2lnbmVkLWV4Y2hhbmdlO3Y9YjM7cT0wLjknLAogICAgICAgICdhY2NlcHQtbGFuZ3VhZ2UnOiAnZW4tSU4sZW47cT0wLjknLAogICAgICAgICdjYWNoZS1jb250cm9sJzogJ21heC1hZ2U9MCcsCiAgICAgICAgIyBSZXF1ZXN0cyBzb3J0cyBjb29raWVzPSBhbHBoYWJldGljYWxseQogICAgICAgICMgJ2Nvb2tpZSc6ICdfZ2E9R0ExLjIuMTg0MTE1NzczNS4xNjYwNTQ2NDM1OyBfZ2lkPUdBMS4yLjE5MjY5NDA5MTUuMTY2MDU0NjQzNTsgX2dhdF9ndGFnX1VBXzMxMzkxMjEwXzQ0PTEnLAogICAgICAgICdkbnQnOiAnMScsCiAgICAgICAgJ29yaWdpbic6ICdodHRwczovL3d3dy5zaG9ydHVybC5hdCcsCiAgICAgICAgJ3JlZmVyZXInOiAnaHR0cHM6Ly93d3cuc2hvcnR1cmwuYXQvJywKICAgICAgICAnc2VjLWZldGNoLWRlc3QnOiAnZG9jdW1lbnQnLAogICAgICAgICdzZWMtZmV0Y2gtbW9kZSc6ICduYXZpZ2F0ZScsCiAgICAgICAgJ3NlYy1mZXRjaC1zaXRlJzogJ3NhbWUtb3JpZ2luJywKICAgICAgICAnc2VjLWZldGNoLXVzZXInOiAnPzEnLAogICAgICAgICd1cGdyYWRlLWluc2VjdXJlLXJlcXVlc3RzJzogJzEnLAogICAgICAgICd1c2VyLWFnZW50JzogJ01vemlsbGEvNS4wIChYMTE7IExpbnV4IGFhcmNoNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS84OC4wLjQzMjQuMTg4IFNhZmFyaS81MzcuMzYgQ3JLZXkvMS41NC4yNTAzMjAnLAogICAgfQoKICAgIGRhdGEgPSB7CiAgICAgICAgJ3UnOiBmJ3tsaW5rfScsCiAgICB9CiAgICAKCiAgICByZXNwb25zZSA9IHJlcXVlc3RzLnBvc3QoJ2h0dHBzOi8vd3d3LnNob3J0dXJsLmF0L3Nob3J0ZW5lci5waHAnLCBjb29raWVzPWNvb2tpZXMsIGhlYWRlcnM9aGVhZGVycywgZGF0YT1kYXRhKQogICAgY2RzID0gcmVzcG9uc2UuY29udGVudAoKICAgICN3aXRoIG9wZW4oJ2luZGV4Lmh0bWwnLCd3JykgYXMgZmlsZXM6CiAgICAjICAgZmlsZXMud3JpdGUoc3RyKGNkcykpCgogICAgc291cCA9IEJlYXV0aWZ1bFNvdXAoY2RzLCdodG1sLnBhcnNlcicpCgogICAgdHJ5OgogICAgICAgIHZhbHVlID0gc291cC5maW5kKCdpbnB1dCcsIHsnaWQnOiAnc2hvcnRlbnVybCd9KS5nZXQoJ3ZhbHVlJykKICAgICAgICBwcmludCgnXG4nKQogICAgICAgIEZyb250ZW50VHlwaW5nRnVuY3Rpb24oJ+KUlOKUgFsg4pyUIF0gU3VjY2VzcycpCiAgICAgICAgRnJvbnRlbnRUeXBpbmdGdW5jdGlvbihmIuKUlOKUgFsg4pyUIF0gTGluayA6ICIrRm9yZS5HUkVFTitmInt2YWx1ZX0iKQogICAgICAgIAogICAgICAKICAgICAgICAjb3MucmVtb3ZlKCd0aW55dXJscy50eHQnKQogICAgICAgICNvcy5yZW1vdmUoJ2xpbmtzdGlueS50eHQnKQogICAgCiAgICAgICAgCiAgICBleGNlcHQgRXhjZXB0aW9uIGFzIGU6CiAgICAgICAgcHJpbnQoJ1xuJykKICAgICAgICBGcm9udGVudFR5cGluZ0Z1bmN0aW9uKCdVcmwgaXMgaW52YWxpZCAhJykKICAgICAgICBwcmludCgnXG4nKQoKZGVmIHVwbG9hZF9maWxlX3RvX2dpdGh1YihhY2Nlc3NfdG9rZW4sIHJlcG9fb3duZXIsIHJlcG9fbmFtZSwgbG9jYWxfZmlsZV9wYXRoLCBicmFuY2hfbmFtZSwgY29tbWl0X21lc3NhZ2UpOgogICAgIyBCYXNlIFVSTCBmb3IgdGhlIEdpdEh1YiBBUEkKICAgIGJhc2VfdXJsID0gImh0dHBzOi8vYXBpLmdpdGh1Yi5jb20iCgogICAgIyBTZXQgdXAgaGVhZGVycyB3aXRoIGF1dGhlbnRpY2F0aW9uCiAgICBoZWFkZXJzID0gewogICAgICAgICJBdXRob3JpemF0aW9uIjogZiJ0b2tlbiB7YWNjZXNzX3Rva2VufSIKICAgIH0KCiAgICAjIFJlYWQgdGhlIGZpbGUgY29udGVudCBhbmQgZW5jb2RlIGl0IHRvIEJhc2U2NAogICAgd2l0aCBvcGVuKGxvY2FsX2ZpbGVfcGF0aCwgInJiIikgYXMgZmlsZToKICAgICAgICBjb250ZW50ID0gZmlsZS5yZWFkKCkKICAgICAgICBlbmNvZGVkX2NvbnRlbnQgPSBiYXNlNjQuYjY0ZW5jb2RlKGNvbnRlbnQpLmRlY29kZSgpCgogICAgIyBBUEkgZW5kcG9pbnQgdG8gY3JlYXRlIG9yIHVwZGF0ZSBhIGZpbGUKICAgIGZpbGVfdXJsID0gZiJ7YmFzZV91cmx9L3JlcG9zL3tyZXBvX293bmVyfS97cmVwb19uYW1lfS9jb250ZW50cy97bG9jYWxfZmlsZV9wYXRofSIKCiAgICAjIFByZXBhcmUgdGhlIHBheWxvYWQKICAgIHBheWxvYWQgPSB7CiAgICAgICAgIm1lc3NhZ2UiOiBjb21taXRfbWVzc2FnZSwKICAgICAgICAiY29udGVudCI6IGVuY29kZWRfY29udGVudCwKICAgICAgICAiYnJhbmNoIjogYnJhbmNoX25hbWUsCiAgICB9CgogICAgIyBTZW5kIHRoZSByZXF1ZXN0IHRvIGNyZWF0ZS91cGRhdGUgdGhlIGZpbGUKICAgIHJlc3BvbnNlID0gcmVxdWVzdHMucHV0KGZpbGVfdXJsLCBoZWFkZXJzPWhlYWRlcnMsIGpzb249cGF5bG9hZCkKCiAgICAKICAgCgogICAgaWYgcmVzcG9uc2Uuc3RhdHVzX2NvZGUgPT0gMjAxOgogICAgICAgIHBhc3MKICAgICAgICAjcHJpbnQoZiJVcGxvYWRlZCA6IHtyZXNwb25zZS5zdGF0dXNfY29kZX0iKQogICAgICAgICNwcmludChyZXNwb25zZS5qc29uKCkpCiAgICBlbHNlOgogICAgICAgIHByaW50KCdGYWlsZWQgISEnKQoKZGVmIHVwbG9hZF9maWxlc190b19naXRodWIodXNlcm5hbWUsIHJlcG9zaXRvcnksIGZpbGVfbGlzdCwgdG9rZW4pOgogICAgYmFzZV91cmwgPSBmImh0dHBzOi8vYXBpLmdpdGh1Yi5jb20vcmVwb3Mve3VzZXJuYW1lfS97cmVwb3NpdG9yeX0vY29udGVudHMvIgogICAgCiAgICBoZWFkZXJzID0gewogICAgICAgICJBdXRob3JpemF0aW9uIjogZiJ0b2tlbiB7dG9rZW59IiwKICAgICAgICAiQWNjZXB0IjogImFwcGxpY2F0aW9uL3ZuZC5naXRodWIudjMranNvbiIKICAgIH0KICAgIAogICAgZm9yIGZpbGVfaW5mbyBpbiBmaWxlX2xpc3Q6CiAgICAgICAgZmlsZV9wYXRoID0gZmlsZV9pbmZvWyJmaWxlX3BhdGgiXQogICAgICAgIGZpbGVfY29udGVudCA9IGZpbGVfaW5mb1siZmlsZV9jb250ZW50Il0KICAgICAgICBjb21taXRfbWVzc2FnZSA9IGYiVXBsb2FkIHtmaWxlX3BhdGh9IgogICAgICAgIGJyYW5jaF9uYW1lID0gIm1haW4iICAjIFJlcGxhY2Ugd2l0aCB0aGUgZGVzaXJlZCBicmFuY2ggbmFtZSBpZiBub3QgdXNpbmcgJ21haW4nCiAgICAgICAgCiAgICAgICAgdXJsID0gZiJ7YmFzZV91cmx9e2ZpbGVfcGF0aH0iCiAgICAgICAgCiAgICAgICAgIyBFbmNvZGUgdGhlIGZpbGUgY29udGVudCBpbiBCYXNlNjQKICAgICAgICBmaWxlX2NvbnRlbnRfYmFzZTY0ID0gYmFzZTY0LmI2NGVuY29kZShmaWxlX2NvbnRlbnQuZW5jb2RlKCkpLmRlY29kZSgpCiAgICAgICAgCiAgICAgICAgcGF5bG9hZCA9IHsKICAgICAgICAgICAgIm1lc3NhZ2UiOiBjb21taXRfbWVzc2FnZSwKICAgICAgICAgICAgImNvbnRlbnQiOiBmaWxlX2NvbnRlbnRfYmFzZTY0LAogICAgICAgICAgICAiYnJhbmNoIjogYnJhbmNoX25hbWUKICAgICAgICB9CiAgICAgICAgCiAgICAgICAgcmVzcG9uc2UgPSByZXF1ZXN0cy5wdXQodXJsLCBoZWFkZXJzPWhlYWRlcnMsIGpzb249cGF5bG9hZCkKCiAgICAgICAgCiAgICAgICAgCiAgICAgICAgCiAgICAgICAgaWYgcmVzcG9uc2Uuc3RhdHVzX2NvZGUgPT0gMjAxIG9yIHJlc3BvbnNlLnN0YXR1c19jb2RlID09IDIwMDoKICAgICAgICAgICAgRnJvbnRlbnRUeXBpbmdJbnB1dENvZGUoZiJGaWxlICd7ZmlsZV9wYXRofScgdXBsb2FkZWQgc3VjY2Vzc2Z1bGx5LiIgLCAneCcpCiAgICAgICAgZWxzZToKICAgICAgICAgICAgcHJpbnQoZiJGYWlsZWQgdG8gdXBsb2FkIGZpbGUgJ3tmaWxlX3BhdGh9Jy4gU3RhdHVzIENvZGU6IHtyZXNwb25zZS5zdGF0dXNfY29kZX0iKQogICAgICAgICAgICBiYWNraWUoKQogICAgICAgIAogICAgICAgIAoKZGVmIGJoYWljaGFuZ2UoYW5zd2VyKToKICAgIGlmIGFuc3dlciA9PSAneScgb3IgYW5zd2VyPT0nWSc6CiAgICAgICAgd2l0aCBvcGVuKCcuZ2l0aHViYXBpLnR4dCcsJ3InKSBhcyBnaXRodWJmb2xkZXJ3YWxhOgogICAgICAgICAgICBkYXRhZm9sZGVyd2FsYSA9IGdpdGh1YmZvbGRlcndhbGEucmVhZCgpLnN0cmlwKCkKICAgICAgICB3aXRoIG9wZW4oJy5naXRodWJhcGkyLnR4dCcsJ3InKSBhcyBnaXRodWIyd2FsYToKICAgICAgICAgICAgZGF0YTJ3YWxhID0gZ2l0aHViMndhbGEucmVhZCgpLnN0cmlwKCkKICAgICAgICBnaXRodWJfdXNlcm5hbWUgPSBmIntkYXRhMndhbGF9Ii5zdHJpcCgpCiAgICAgICAgZ2l0aHViaW5mb3dhbGEgPSBpbnB1dChyKyJbICIrYisieCIrcisiIF0iK3crIlwwMzNbMTszN20gRW50ZXIgUmVwb3NpdG9yeSBOYW1lIDogICIrcikuc3RyaXAoKQogICAgICAgIHJlcG9zaXRvcnlfbmFtZSA9IGYie2dpdGh1YmluZm93YWxhfSIuc3RyaXAoKQogICAgICAgIGdpdGh1Yl90b2tlbiA9IGYie2RhdGFmb2xkZXJ3YWxhfSIuc3RyaXAoKQogICAgICAgIG1laXNhaGFiID0gaW5wdXQocisiWyAiK2IrIngiK3IrIiBdIit3KyJcMDMzWzE7MzdtIEVudGVyIEZvbGRlciBuYW1lIDogICIrcikuc3RyaXAoKQogICAgICAgIG9zLmNoZGlyKG1laXNhaGFiKQogICAgICAgIHRpbWUuc2xlZXAoMS4wKQogICAgICAgIHNoYWthciA9IE1haW5fU2V0dXAoKQogICAgICAgIHNoYWthci5vbmVzaG90a2lsbCgpCiAgICAgICAgRnJvbnRlbnRUeXBpbmdGdW5jdGlvbignVXBsb2FkaW5nIGZpbGVzIGZyb20gZm9sZGVyIHt9Jy5mb3JtYXQobWVpc2FoYWIpKQogICAgICAgIHByaW50KCdcbicpCiAgICAgICAgZm9yIGsgaW4gb3MubGlzdGRpcigpOgogICAgICAgICAgICBpZiBQYXRoKGYne2t9JykuaXNfZGlyKCk6CiAgICAgICAgICAgICAgICBjb250aW51ZQogICAgICAgICAgICB3aXRoIG9wZW4oZid7a30nLCdyJykgYXMgbmljZXR4dDoKICAgICAgICAgICAgICAgIGFsbGRhdGEgPSBuaWNldHh0LnJlYWQoKQogICAgICAgICAgICBmaWxlX2xpc3QgPSBbCiAgICAgICAgICAgICAgICAgICAgewogICAgICAgICAgICAgICAgICAgICAgICAiZmlsZV9wYXRoIjogZiJ7a30iLAogICAgICAgICAgICAgICAgICAgICAgICAiZmlsZV9jb250ZW50IjogZiJ7YWxsZGF0YX0iCiAgICAgICAgICAgICAgICAgICAgfSwKICAgICAgICAgICAgICAgIF0KCiAgICAgICAgICAgIHVwbG9hZF9maWxlc190b19naXRodWIoZ2l0aHViX3VzZXJuYW1lLCByZXBvc2l0b3J5X25hbWUsIGZpbGVfbGlzdCwgZ2l0aHViX3Rva2VuKQogICAgICAgIHByaW50KCdcbicpCiAgICAgICAgRnJvbnRlbnRUeXBpbmdJbnB1dENvZGUoJ0FsbCBGaWxlcyBVcGxvYWRlZCBTdWNjZXNzZnVsbHkgRnJvbSBmb2xkZXIge30nLmZvcm1hdChtZWlzYWhhYiksJ3gnKQogICAgICAgIHByaW50KCdcbicpCiAgICAgICAgYmFja2llKCkKCmRlZiBkZWxldGVfZ2l0aHViX3JlcG9zaXRvcnkodXNlcm5hbWUsIHJlcG9zaXRvcnksIHRva2VuKToKICAgIGJhc2VfdXJsID0gZiJodHRwczovL2FwaS5naXRodWIuY29tL3JlcG9zL3t1c2VybmFtZX0ve3JlcG9zaXRvcnl9IgogICAgCiAgICBoZWFkZXJzID0gewogICAgICAgICJBdXRob3JpemF0aW9uIjogZiJ0b2tlbiB7dG9rZW59IiwKICAgICAgICAiQWNjZXB0IjogImFwcGxpY2F0aW9uL3ZuZC5naXRodWIudjMranNvbiIKICAgIH0KICAgIAogICAgcmVzcG9uc2UgPSByZXF1ZXN0cy5kZWxldGUoYmFzZV91cmwsIGhlYWRlcnM9aGVhZGVycykKICAgIAogICAgaWYgcmVzcG9uc2Uuc3RhdHVzX2NvZGUgPT0gMjA0OgogICAgICAgIHByaW50KCdcbicpCiAgICAgICAgRnJvbnRlbnRUeXBpbmdGdW5jdGlvbihmIlJlcG9zaXRvcnkgJ3tyZXBvc2l0b3J5fScgZGVsZXRlZCBzdWNjZXNzZnVsbHkuIikKICAgIGVsaWYgcmVzcG9uc2Uuc3RhdHVzX2NvZGUgPT0gNDA0OgogICAgICAgIHByaW50KGYiUmVwb3NpdG9yeSAne3JlcG9zaXRvcnl9JyBub3QgZm91bmQuIikKICAgIGVsc2U6CiAgICAgICAgcHJpbnQoZiJGYWlsZWQgdG8gZGVsZXRlIHJlcG9zaXRvcnkuIFN0YXR1cyBDb2RlOiB7cmVzcG9uc2Uuc3RhdHVzX2NvZGV9IikKICAgICAgICBwcmludChyZXNwb25zZS5qc29uKCkpCiAgICAgICAgZXhpdCgpCgpkZWYgbWFrZV9yZXBvc2l0b3J5X3ByaXZhdGUodXNlcm5hbWUsIHJlcG9zaXRvcnksIHRva2VuKToKICAgIGJhc2VfdXJsID0gZiJodHRwczovL2FwaS5naXRodWIuY29tL3JlcG9zL3t1c2VybmFtZX0ve3JlcG9zaXRvcnl9IgogICAgCiAgICBoZWFkZXJzID0gewogICAgICAgICJBdXRob3JpemF0aW9uIjogZiJ0b2tlbiB7dG9rZW59IiwKICAgICAgICAiQWNjZXB0IjogImFwcGxpY2F0aW9uL3ZuZC5naXRodWIudjMranNvbiIKICAgIH0KICAgIAogICAgcGF5bG9hZCA9IHsKICAgICAgICAicHJpdmF0ZSI6IFRydWUKICAgIH0KICAgIAogICAgcmVzcG9uc2UgPSByZXF1ZXN0cy5wYXRjaChiYXNlX3VybCwgaGVhZGVycz1oZWFkZXJzLCBqc29uPXBheWxvYWQpCiAgICAKICAgIGlmIHJlc3BvbnNlLnN0YXR1c19jb2RlID09IDIwMDoKICAgICAgICBwcmludCgnXG4nKQogICAgICAgIEZyb250ZW50VHlwaW5nRnVuY3Rpb24oZiJSZXBvc2l0b3J5ICd7cmVwb3NpdG9yeX0nIHNldCB0byBwcml2YXRlLiIpCiAgICBlbGlmIHJlc3BvbnNlLnN0YXR1c19jb2RlID09IDQwNDoKICAgICAgICBwcmludChmIlJlcG9zaXRvcnkgJ3tyZXBvc2l0b3J5fScgbm90IGZvdW5kLiIpCiAgICBlbHNlOgogICAgICAgIHByaW50KGYiRmFpbGVkIHRvIHNldCByZXBvc2l0b3J5IHRvIHByaXZhdGUuIFN0YXR1cyBDb2RlOiB7cmVzcG9uc2Uuc3RhdHVzX2NvZGV9IikKICAgICAgICBwcmludChyZXNwb25zZS5qc29uKCkpCiAgICAgICAgZXhpdCgpCgpkZWYgdXBkYXRlX3JlcG9zaXRvcnlfZGVzY3JpcHRpb24odXNlcm5hbWUsIHJlcG9zaXRvcnksIGRlc2NyaXB0aW9uLCB0b2tlbik6CiAgICBiYXNlX3VybCA9IGYiaHR0cHM6Ly9hcGkuZ2l0aHViLmNvbS9yZXBvcy97dXNlcm5hbWV9L3tyZXBvc2l0b3J5fSIKICAgIAogICAgaGVhZGVycyA9IHsKICAgICAgICAiQXV0aG9yaXphdGlvbiI6IGYidG9rZW4ge3Rva2VufSIsCiAgICAgICAgIkFjY2VwdCI6ICJhcHBsaWNhdGlvbi92bmQuZ2l0aHViLnYzK2pzb24iCiAgICB9CiAgICAKICAgIHBheWxvYWQgPSB7CiAgICAgICAgImRlc2NyaXB0aW9uIjogZGVzY3JpcHRpb24KICAgIH0KICAgIAogICAgcmVzcG9uc2UgPSByZXF1ZXN0cy5wYXRjaChiYXNlX3VybCwgaGVhZGVycz1oZWFkZXJzLCBqc29uPXBheWxvYWQpCiAgICAKICAgIGlmIHJlc3BvbnNlLnN0YXR1c19jb2RlID09IDIwMDoKICAgICAgICBwcmludCgnXG4nKQogICAgICAgIEZyb250ZW50VHlwaW5nRnVuY3Rpb24oZiJSZXBvc2l0b3J5IGRlc2NyaXB0aW9uIHVwZGF0ZWQgc3VjY2Vzc2Z1bGx5LiIpCiAgICBlbGlmIHJlc3BvbnNlLnN0YXR1c19jb2RlID09IDQwNDoKICAgICAgICBwcmludChmIlJlcG9zaXRvcnkgbm90IGZvdW5kLiIpCiAgICBlbHNlOgogICAgICAgIHByaW50KGYiRmFpbGVkIHRvIHVwZGF0ZSByZXBvc2l0b3J5IGRlc2NyaXB0aW9uLiBTdGF0dXMgQ29kZToge3Jlc3BvbnNlLnN0YXR1c19jb2RlfSIpCiAgICAgICAgcHJpbnQocmVzcG9uc2UuanNvbigpKQogICAgICAgIGV4aXQoKQoKZGVmIHVwZGF0ZV9yZWFkbWVfaW5fcmVwb3NpdG9yeSh1c2VybmFtZSwgcmVwb3NpdG9yeSwgbmV3X3JlYWRtZV9jb250ZW50LCBjb21taXRfbWVzc2FnZSwgdG9rZW4pOgogICAgYmFzZV91cmwgPSBmImh0dHBzOi8vYXBpLmdpdGh1Yi5jb20vcmVwb3Mve3VzZXJuYW1lfS97cmVwb3NpdG9yeX0vY29udGVudHMvUkVBRE1FLm1kIgogICAgCiAgICBoZWFkZXJzID0gewogICAgICAgICJBdXRob3JpemF0aW9uIjogZiJ0b2tlbiB7dG9rZW59IiwKICAgICAgICAiQWNjZXB0IjogImFwcGxpY2F0aW9uL3ZuZC5naXRodWIudjMranNvbiIKICAgIH0KICAgIAogICAgIyBHZXQgdGhlIGN1cnJlbnQgUkVBRE1FIGNvbnRlbnQKICAgIHJlc3BvbnNlID0gcmVxdWVzdHMuZ2V0KGJhc2VfdXJsLCBoZWFkZXJzPWhlYWRlcnMpCiAgICByZXNwb25zZV9qc29uID0gcmVzcG9uc2UuanNvbigpCiAgICBjdXJyZW50X3JlYWRtZV9jb250ZW50ID0gYjY0ZW5jb2RlKHJlc3BvbnNlX2pzb25bJ2NvbnRlbnQnXS5lbmNvZGUoKSkuZGVjb2RlKCkKICAgIAogICAgIyBVcGRhdGUgdGhlIGNvbnRlbnQgaWYgaXQncyBkaWZmZXJlbnQKICAgIGlmIGN1cnJlbnRfcmVhZG1lX2NvbnRlbnQgIT0gYjY0ZW5jb2RlKG5ld19yZWFkbWVfY29udGVudC5lbmNvZGUoKSkuZGVjb2RlKCk6CiAgICAgICAgcGF5bG9hZCA9IHsKICAgICAgICAgICAgIm1lc3NhZ2UiOiBjb21taXRfbWVzc2FnZSwKICAgICAgICAgICAgImNvbnRlbnQiOiBiNjRlbmNvZGUobmV3X3JlYWRtZV9jb250ZW50LmVuY29kZSgpKS5kZWNvZGUoKSwKICAgICAgICAgICAgInNoYSI6IHJlc3BvbnNlX2pzb25bJ3NoYSddCiAgICAgICAgfQogICAgICAgIHVwZGF0ZV9yZXNwb25zZSA9IHJlcXVlc3RzLnB1dChiYXNlX3VybCwgaGVhZGVycz1oZWFkZXJzLCBqc29uPXBheWxvYWQpCiAgICAgICAgaWYgdXBkYXRlX3Jlc3BvbnNlLnN0YXR1c19jb2RlID09IDIwMDoKICAgICAgICAgICAgcHJpbnQoJ1xuJykKICAgICAgICAgICAgRnJvbnRlbnRUeXBpbmdGdW5jdGlvbigiUkVBRE1FIHVwZGF0ZWQgc3VjY2Vzc2Z1bGx5LiIpCiAgICAgICAgZWxzZToKICAgICAgICAgICAgcHJpbnQoZiJGYWlsZWQgdG8gdXBkYXRlIFJFQURNRS4gU3RhdHVzIENvZGU6IHt1cGRhdGVfcmVzcG9uc2Uuc3RhdHVzX2NvZGV9IikKICAgICAgICAgICAgcHJpbnQodXBkYXRlX3Jlc3BvbnNlLmpzb24oKSkKICAgICAgICAgICAgZXhpdCgpCiAgICBlbHNlOgogICAgICAgIHByaW50KCJObyBjaGFuZ2VzIGRldGVjdGVkIGluIFJFQURNRS4iKQogICAgICAgIHByaW50KCdcbicpCiAgICAgICAgYmFja2llKCkKCmRlZiBzaG9ydHVybGxvcChsaW5rKToKICAgICMKCiAgICB1cmwgPSAnaHR0cHM6Ly9jdXR0Lmx5JwoKICAgIHIgPSByZXF1ZXN0cy5nZXQodXJsKS5jb29raWVzCgogICAgd2l0aCBvcGVuKCdzYW1heWJoYWkudHh0JywndycpIGFzIGZpbGU6CiAgICAgICAgZmlsZS53cml0ZShzdHIocikpCgogICAgd2l0aCBvcGVuKCdzYW1heWJoYWkudHh0JywncicpIGFzIG9wczoKICAgICAgICBkYXRhID0gc3RyKG9wcy5yZWFkKCkpCgogICAgb3BlbnMgPSBkYXRhLnNwbGl0KClbMV0KICAgIGRhdGEyID0gb3BlbnMuc3BsaXQoJz0nKVsxXSAjIFBTU0lEID0gCgoKICAgIGNvb2tpZXMgPSB7CiAgICAgICAgJ1BIUFNFU1NJRCc6IGYne2RhdGEyfScsCiAgICB9CgogICAgaGVhZGVycyA9IHsKICAgICAgICAnVXNlci1BZ2VudCc6ICdNb3ppbGxhLzUuMCAoV2luZG93cyBOVCAxMC4wOyBydjo5MS4wKSBHZWNrby8yMDEwMDEwMSBGaXJlZm94LzkxLjAnLAogICAgICAgICdBY2NlcHQnOiAnKi8qJywKICAgICAgICAnQWNjZXB0LUxhbmd1YWdlJzogJ2VuLVVTLGVuO3E9MC41JywKICAgICAgICAnQ29udGVudC1UeXBlJzogJ211bHRpcGFydC9mb3JtLWRhdGE7IGJvdW5kYXJ5PS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLTI0MzYxOTI4MTExNTU2ODU5MDk0ODU4MDY0NzYnLAogICAgICAgICdPcmlnaW4nOiAnaHR0cHM6Ly9jdXR0Lmx5JywKICAgICAgICAnRE5UJzogJzEnLAogICAgICAgICdBbHQtVXNlZCc6ICdjdXR0Lmx5JywKICAgICAgICAnQ29ubmVjdGlvbic6ICdrZWVwLWFsaXZlJywKICAgICAgICAnUmVmZXJlcic6ICdodHRwczovL2N1dHQubHkvJywKICAgICAgICAjICdDb29raWUnOiAnUEhQU0VTU0lEPWNzOGk4bTBpb3MwbGQ5cmVkdmE0MG0xcWRtJywKICAgICAgICAnU2VjLUZldGNoLURlc3QnOiAnZW1wdHknLAogICAgICAgICdTZWMtRmV0Y2gtTW9kZSc6ICdjb3JzJywKICAgICAgICAnU2VjLUZldGNoLVNpdGUnOiAnc2FtZS1vcmlnaW4nLAogICAgICAgICMgUmVxdWVzdHMgZG9lc24ndCBzdXBwb3J0IHRyYWlsZXJzCiAgICAgICAgIyAnVEUnOiAndHJhaWxlcnMnLAogICAgfQoKICAgIGRhdGEgPSAnLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0yNDM2MTkyODExMTU1Njg1OTA5NDg1ODA2NDc2XHJcbkNvbnRlbnQtRGlzcG9zaXRpb246IGZvcm0tZGF0YTsgbmFtZT0idXJsIlxyXG5cclxuPHVybD5cclxuLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0yNDM2MTkyODExMTU1Njg1OTA5NDg1ODA2NDc2XHJcbkNvbnRlbnQtRGlzcG9zaXRpb246IGZvcm0tZGF0YTsgbmFtZT0iZG9tYWluIlxyXG5cclxuMFxyXG4tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLTI0MzYxOTI4MTExNTU2ODU5MDk0ODU4MDY0NzYtLVxyXG4nCiAgICAKCiAgICBkYXRhID0gZGF0YS5yZXBsYWNlKCc8dXJsPicsbGluaykKCiAgICByZXNwb25zZSA9IHJlcXVlc3RzLnBvc3QoJ2h0dHBzOi8vY3V0dC5seS9zY3JpcHRzL3Nob3J0ZW5VcmwucGhwJywgY29va2llcz1jb29raWVzLCBoZWFkZXJzPWhlYWRlcnMsIGRhdGE9ZGF0YSkKCiAgICBjb250ZW50ID0gcmVzcG9uc2UuY29udGVudAoKICAgIHdpdGggb3BlbignbGFzdC50eHQnLCd3JykgYXMgb2k6CiAgICAgICAgb2kud3JpdGUoc3RyKGNvbnRlbnQpKQoKICAgIHdpdGggb3BlbignbGFzdC50eHQnLCdyJykgYXMgbGo6CiAgICAgICAgZGF0YTUgPSBsai5yZWFkKCkKCiAgICB5eSA9IGRhdGE1LnNwbGl0KCInIikKICAgIHJldHVybiB5eVsxXQogICAgCiAgICBvcy5yZW1vdmUoJ2xhc3QudHh0JykKICAgIG9zLnJlbW92ZSgnc2FtYXliaGFpLnR4dCcpCgpkZWYgdXBsb2FkX211bHRpcGxlX3RvX21lZ2EoZW1haWwsIHBhc3N3b3JkLCBmaWxlcyk6CiAgICBtZWdhID0gTWVnYSgpCiAgICBtID0gbWVnYS5sb2dpbihlbWFpbCwgcGFzc3dvcmQpCiAgICAKICAgIGZvciBmaWxlX3BhdGggaW4gZmlsZXM6CiAgICAgICAgbS51cGxvYWQoZmlsZV9wYXRoKQogICAgICAgIEZyb250ZW50VHlwaW5nRnVuY3Rpb24oZiJVcGxvYWRlZDoge2ZpbGVfcGF0aH0iKQoKZGVmIG1haW5zeXN0ZW1saW5rKCk6CiAgICBtb25leSA9IE1haW5fU2V0dXAoKQogICAgbW9uZXkub25lc2hvdGtpbGwoKQogICAgd2l0aCBvcGVuKCcubWVnYS50eHQnLCdyJykgYXMgbWVnYXJlYWQ6CiAgICAgICAgbWVnYXJlYWRzID0gbWVnYXJlYWQucmVhZGxpbmVzKCkKCiAgICBlbXB0eWJoYWkgPSB7fQoKICAgIGZvciBpIGluIG1lZ2FyZWFkczoKICAgICAgICBqc3BsaXQgPSBpLnNwbGl0KCdcdCcpCiAgICAgICAgZW1wdHliaGFpW2pzcGxpdFswXV0gPSBqc3BsaXRbMV0KCiAgICBlbXB0eWJoYWkgPSB7IHgudHJhbnNsYXRlKHszMjpOb25lfSkgOiB5CiAgICAgICAgZm9yIHgsIHkgaW4gZW1wdHliaGFpLml0ZW1zKCl9CgoKICAgIG1lZ2FfZW1haWwgPSBmIntlbXB0eWJoYWkuZ2V0KCdVc2VybmFtZScpfSIuc3RyaXAoKQogICAgbWVnYV9wYXNzd29yZCA9IGYie2VtcHR5YmhhaS5nZXQoJ1Bhc3N3b3JkJyl9Ii5zdHJpcCgpCgogICAgd2l0aCBvcGVuKCcuc2F2ZW5hbWVkLnR4dCcsJ3InKSBhcyBmaWxlczoKICAgICAgICBva3NkYXRhID0gZmlsZXMucmVhZGxpbmVzKCkKCiAgICAjIExvZyBpbiB0byBNRUdBCiAgICBtZWdhID0gTWVnYSgpCiAgICBtID0gbWVnYS5sb2dpbihtZWdhX2VtYWlsLCBtZWdhX3Bhc3N3b3JkKQogIAoKICAgIG9wID0gMAogICAgc2FtYXkgPSBbXQoKICAgIGZvciBsaW5lIGluIG9rc2RhdGE6CiAgICAgICAgc2FtYXkuYXBwZW5kKGxpbmUuc3RyaXAoKSkKCiAgICBmaWxlc2Rpcm5ldyA9IG9zLnBhdGguZXhwYW5kdXNlcignficpICsgJy8nCgogICAgbmV3ZmlsZW5hbWVzID0gW10KICAgIG9zcCA9IDEKICAgIGZvciBrIGluIHNhbWF5OgogICAgICAgIEtsb3BzID0gaW5wdXQocisiWyAiK2IrIngiK3IrIiBdIit3K2YiXDAzM1sxOzM3bSBFbnRlciB0aGUgUmVsYXRlZCBuYW1lIGZpbGUge29zcH0gOiAiK3IpLnN0cmlwKCkKICAgICAgICBuZXdmaWxlbmFtZXMuYXBwZW5kKEtsb3BzKQogICAgICAgIG9zcCA9IG9zcCArIDEKCgogICAgbW9uZXkub25lc2hvdGtpbGwoKQoKCiAgICAjIFVwbG9hZCB0aGUgZmlsZSBhbmQgZ2V0IGl0cyBoYW5kbGUKCiAgICBmb3IgaSBpbiBzYW1heToKICAgICAgICBmaWxlX2hhbmRsZSA9IG0udXBsb2FkKHNhbWF5W29wXSkKICAgICAgICAKICAgICAgICAKCiAgICAgICAgIyBHZXQgdGhlIHB1YmxpYyBkb3dubG9hZCBsaW5rCiAgICAgICAgZG93bmxvYWRfbGluayA9IG0uZ2V0X3VwbG9hZF9saW5rKGZpbGVfaGFuZGxlKQoKICAgICAgICB3aXRoIG9wZW4oZid7ZmlsZXNkaXJuZXd9LmJhc2hfbWVnYS50eHQnLCdhJykgYXMgZmlsZXNuZXdjb250ZW50OgogICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICBmaWxlc25ld2NvbnRlbnQud3JpdGUoZid7bmV3ZmlsZW5hbWVzW29wXX0gCSB7ZG93bmxvYWRfbGlua31cbicpCiAgICAgICAgCgogICAgICAgIHByaW50KHIrIlsgIitiKyJ4IityKyIgXSIrdytmIlwwMzNbMTszN20gbGluayAtPiAiK0ZvcmUuUkVEK2Yie3NhbWF5W29wXX06ICIrRm9yZS5HUkVFTitzdHIoc2hvcnR1cmxsb3AoZG93bmxvYWRfbGluaykpKQoKICAgICAgICBvcCA9IG9wICsgMQogICAgICAgIAogICAgCiAgICAgCiAgICBvcy5yZW1vdmUoJy5zYXZlbmFtZWQudHh0JykKICAgIHByaW50KCdcbicpCiAgICBiYWNraWUoKQogICAgCgoKZGVmIHNob3J0dXJsKGxpbmspOgogICAgIwoKICAgIHVybCA9ICdodHRwczovL2N1dHQubHknCgogICAgciA9IHJlcXVlc3RzLmdldCh1cmwpLmNvb2tpZXMKCiAgICB3aXRoIG9wZW4oJ3NhbWF5YmhhaS50eHQnLCd3JykgYXMgZmlsZToKICAgICAgICBmaWxlLndyaXRlKHN0cihyKSkKCiAgICB3aXRoIG9wZW4oJ3NhbWF5YmhhaS50eHQnLCdyJykgYXMgb3BzOgogICAgICAgIGRhdGEgPSBzdHIob3BzLnJlYWQoKSkKCiAgICBvcGVucyA9IGRhdGEuc3BsaXQoKVsxXQogICAgZGF0YTIgPSBvcGVucy5zcGxpdCgnPScpWzFdICMgUFNTSUQgPSAKCgogICAgY29va2llcyA9IHsKICAgICAgICAnUEhQU0VTU0lEJzogZid7ZGF0YTJ9JywKICAgIH0KCiAgICBoZWFkZXJzID0gewogICAgICAgICdVc2VyLUFnZW50JzogJ01vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjA7IHJ2OjkxLjApIEdlY2tvLzIwMTAwMTAxIEZpcmVmb3gvOTEuMCcsCiAgICAgICAgJ0FjY2VwdCc6ICcqLyonLAogICAgICAgICdBY2NlcHQtTGFuZ3VhZ2UnOiAnZW4tVVMsZW47cT0wLjUnLAogICAgICAgICdDb250ZW50LVR5cGUnOiAnbXVsdGlwYXJ0L2Zvcm0tZGF0YTsgYm91bmRhcnk9LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tMjQzNjE5MjgxMTE1NTY4NTkwOTQ4NTgwNjQ3NicsCiAgICAgICAgJ09yaWdpbic6ICdodHRwczovL2N1dHQubHknLAogICAgICAgICdETlQnOiAnMScsCiAgICAgICAgJ0FsdC1Vc2VkJzogJ2N1dHQubHknLAogICAgICAgICdDb25uZWN0aW9uJzogJ2tlZXAtYWxpdmUnLAogICAgICAgICdSZWZlcmVyJzogJ2h0dHBzOi8vY3V0dC5seS8nLAogICAgICAgICMgJ0Nvb2tpZSc6ICdQSFBTRVNTSUQ9Y3M4aThtMGlvczBsZDlyZWR2YTQwbTFxZG0nLAogICAgICAgICdTZWMtRmV0Y2gtRGVzdCc6ICdlbXB0eScsCiAgICAgICAgJ1NlYy1GZXRjaC1Nb2RlJzogJ2NvcnMnLAogICAgICAgICdTZWMtRmV0Y2gtU2l0ZSc6ICdzYW1lLW9yaWdpbicsCiAgICAgICAgIyBSZXF1ZXN0cyBkb2Vzbid0IHN1cHBvcnQgdHJhaWxlcnMKICAgICAgICAjICdURSc6ICd0cmFpbGVycycsCiAgICB9CgogICAgZGF0YSA9ICctLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLTI0MzYxOTI4MTExNTU2ODU5MDk0ODU4MDY0NzZcclxuQ29udGVudC1EaXNwb3NpdGlvbjogZm9ybS1kYXRhOyBuYW1lPSJ1cmwiXHJcblxyXG48dXJsPlxyXG4tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLTI0MzYxOTI4MTExNTU2ODU5MDk0ODU4MDY0NzZcclxuQ29udGVudC1EaXNwb3NpdGlvbjogZm9ybS1kYXRhOyBuYW1lPSJkb21haW4iXHJcblxyXG4wXHJcbi0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tMjQzNjE5MjgxMTE1NTY4NTkwOTQ4NTgwNjQ3Ni0tXHJcbicKICAgIAoKICAgIGRhdGEgPSBkYXRhLnJlcGxhY2UoJzx1cmw+JyxsaW5rKQoKCicnJw=="
    comment = base64.b64decode(comment_b64).decode()

    return x.replace(comment, "")

def cli(input_filename: str, output_filename: str, debug: bool, debug_dir: str | None, max_iter: int | None):
    input_file = sys.stdin
    if input_filename not in ["-", "stdin"]:
        input_file = open(input_filename, "r")

    input_source = input_file.read()

    if input_filename not in ["-", "stdin"]:
        input_file.close()

    ds = iteration(input_source, 1, debug, debug_dir, max_iter)
    ds = remove_comments(ds)

    output_file = sys.stdout
    if output_filename != "stdout":
        output_file = open(output_filename, "w")

    output_file.write(ds)

    if output_filename != "stdout":
        output_file.close()

def gui(debug: bool):
    raise Exception("work in progress!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A script to deobfuscate Python scripts")
    parser.add_argument("input", type=str, nargs="?", default="stdin", help="Input filename")
    parser.add_argument("-o", "--output", type=str, default="stdout", help="Output filename (if not existent, will create)")
    parser.add_argument("-i", "--max-iter", type=int, help="Max iterations")
    parser.add_argument("--gui", action="store_true", help="Enable GUI")
    parser.add_argument("--debug", action="store_true", help="Print debug information")
    parser.add_argument("--debug-dir", type=str, help="Path to the debug directory")
    args = parser.parse_args()

    if args.debug:
        sys.stderr.write("args: {}\n".format(args))

    try:
        if args.gui:
            gui(args.debug)
        elif args.input:
            cli(args.input, args.output, args.debug, args.debug_dir, args.max_iter)
        else:
            raise Exception("no input file")
    except Exception as e:
        parser.error(str(e))
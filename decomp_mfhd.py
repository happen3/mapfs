import zlib
import sys
import lzma

if len(sys.argv) != 3:
	print(f"Usage: {sys.argv[0]} mfhd_image target")
	exit(1)

with open(sys.argv[1], 'rb') as f:
	data = lzma.decompress(zlib.decompress(f.read()))

with open(sys.argv[2], 'wb') as f:
	f.write(data)

# mapfs

This is a mapping file system for Linux, using Python as its base.

**Image specification:**
```
image {
    image.mfhd
    image.chain
    journal+image
  }
```
\
**MFHD specification:**
```
Encoding: data (bytearray) -> lzma -> zlib
Decoding: zlib -> lzma -> data (bytes-string) -> data (bytearray)
```
\
**Chain specification:**
```python
[
  ("file_name", 0, 2) # (file_name, start_off, end_off)
  ...
]
```
\
file_name: **The file name you refer**\
0: **Start offset**\
2: **End offset**

## Why linux only?

Mainly personal preferences.
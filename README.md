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

## Future roadmap

| Feature             | mfs             | mfs2                               | mfs2.1                   | mfs2.2/mfs2.3         | mfs2.4                   | mfs3 (planned)                    |
|---------------------|-----------------|------------------------------------|--------------------------|-----------------------|--------------------------|-----------------------------------|
| Journaling          |                 | X                                  | X                        | X (compressed)        | X                        | X                                 |
| Compression         | zlib            | lzma                               | lzma                     | lzma+zlib             | lzma+zlib                | lzma2 (?)                         |
| Files               | X               | X                                  | X                        | X                     | X                        | X                                 |
| Folders             |                 | X                                  | + (empty folder support) | +                     | +                        | +                                 |
| Error Checking      | zlib exceptions | checkJournal                       | checkJournal             | checkJournal (v2)     | checkJournal (v2)        | checkJournal (v2)                 |
| Mounting            | extract-only    | X                                  | X                        | X                     | X                        | X                                 |
| Cross-Compatibility | Windows, Linux  | Linux                              | Linux                    | Linux                 | Linux                    | Linux                             |
| Metadata            |                 |                                    |                          |                       | ~ (file size)            | X                                 |
| API                 |                 |                                    |                          |                       |                          | X                                 |
| Files Spec          | .chain, .mfhd   | block/fs (eg. block/example_drive) | block/fs                 | block/fs              | block/fs                 | block/fs                          |
| Encryption          |                 |                                    |                          | (preliminary for 2.4) | experimental (file only) | mfs3 w/ EFSM (encrypting FS mode) |

## Why linux only?

Mainly personal preferences.
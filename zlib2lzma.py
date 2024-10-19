import zlib
import lzma
import sys

def zlib_to_lzma(input_file, output_file):
    try:
        # Step 1: Read zlib-compressed data from the input file
        with open(input_file, 'rb') as infile:
            zlib_data = infile.read()

        # Step 2: Decompress the zlib-compressed data
        original_data = zlib.decompress(zlib_data)

        # Step 3: Compress the original data using LZMA
        lzma_compressed_data = lzma.compress(original_data)

        # Step 4: Write the LZMA-compressed data to the output file
        with open(output_file, 'wb') as outfile:
            outfile.write(lzma_compressed_data)

        print(f"Successfully converted {input_file} (zlib) to {output_file} (LZMA).")
    except zlib.error as e:
        print("Error decompressing zlib data:", e)
    except lzma.LZMAError as e:
        print("Error compressing data with LZMA:", e)
    except FileNotFoundError as e:
        print("File not found:", e)
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python zlib_to_lzma.py <input_zlib_file> <output_lzma_file>")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        zlib_to_lzma(input_file, output_file)

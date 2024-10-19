import itertools
import pickle
import subprocess
import ast
import os
import struct
import shutil
import lzma
import zlib

def extend_dict(dict1, dict2, fill_value=None):
    """
    Extend dict1 until its length matches dict2 by adding new key-value pairs.

    Args:
    - dict1: The dictionary to be extended.
    - dict2: The dictionary whose length will be matched.
    - fill_value: The value to use for new keys in dict1.

    Returns:
    - dict1: The extended dictionary.
    """
    # Determine the length of dict2
    target_length = len(dict2)
    current_length = len(dict1)

    # If dict1 is shorter than dict2, extend it
    if current_length < target_length:
        # Generate new keys based on the length of dict2
        new_keys = range(current_length, target_length)
        for new_key in new_keys:
            dict1[new_key] = fill_value  # Assign fill_value to new keys

    return dict1

def pmo(file_list, output_file):
    with open(output_file, 'wb') as outfile:
        for file in file_list:
            with open(file, 'rb') as infile:
                # Read file content
                content = infile.read()
                
                # Get the file name without path
                file_name = os.path.basename(file)
                
                # Get the file size
                file_size = len(content)
                
                # Pack the file name length, file size, and content
                # Using struct: < indicates little-endian, H for length, I for size
                packed_data = struct.pack('<H I', len(file_name), file_size) + file_name.encode() + content
                
                # Write packed data to the output file
                outfile.write(packed_data)

def upmo(input_file):
    with open(input_file, 'rb') as infile:
        while True:
            # Read the length of the file name
            header = infile.read(6)
            if not header:
                break  # End of file
            
            # Unpack the header
            name_length, file_size = struct.unpack('<H I', header)
            
            # Read the file name
            file_name = infile.read(name_length).decode()
            
            # Read the file content
            content = infile.read(file_size)
            
            # Write to individual files
            with open(file_name, 'wb') as outfile:
                outfile.write(content)

def recursive_listdir(path, current_path=""):
    # List to store file and directory paths
    files_list = []
    
    # Get the full path by combining the base path and the current subdirectory
    full_path = os.path.join(path, current_path)
    
    # Loop through each entry in the directory
    for entry in os.listdir(full_path):
        entry_path = os.path.join(current_path, entry)  # Track the current relative path
        full_entry_path = os.path.join(full_path, entry)  # Full path to the current entry

        if os.path.isdir(full_entry_path):
            # Recurse into the directory to check its contents
            sub_dir_list = recursive_listdir(path, entry_path)
            
            # If the subdirectory contains no files, add the directory reference
            if not sub_dir_list:
                files_list.append(f"{entry_path}/")  # Add directory with a trailing slash
            else:
                # Otherwise, extend the current list with its content
                files_list.extend(sub_dir_list)
        else:
            # If it's a file, add its full relative path to the list
            files_list.append(f"{entry_path}")
    
    return files_list

def Mount(source, target):
    # Ensure the mount point exists
    if not os.path.exists(target):
        subprocess.run(['sudo', 'mkdir', '-p', target])

    # Construct the mount command
    command = ['sudo', 'mount', '--bind', source, target]

    try:
        # Execute the mount command
        subprocess.run(command, check=True)
        print(f"Mounted {source} at {target}")
    except subprocess.CalledProcessError as e:
        print(f"Error mounting {source}: {e}")

def UMount(target):
    command = ['sudo', 'umount', target]
    try:
        subprocess.run(command, check=True)
        print(f"Unmounted {target}")
    except subprocess.CalledProcessError as e:
        print(f"Error unmounting {target}: {e}")

class MapFS:
    def __init__(self, files, at):
        self.files = files
        self.jfiles = []
        self.journal = {}
        self.at = at
        self.filesaved = at
        self.__version__ = "MapFS 2.3a2"

    def __repr__(self) -> str:
        return f"<filesystem MapFS>"
    
    def version(self):
        return self.__version__

    def checkJournal(self, journal1, journal2): 
        print("fsck: replaying journal")
        
        # Iterate over items in journal2 and compare with journal1
        for k in journal2.keys():
            # Check if the current key exists in journal1
            if k in journal1:
                # Compare the values of journal2 and journal1 for the same key
                #print(journal2[k], journal1[k])
                if journal2[k] == journal1[k]:
                    print(f"fsck: file {k} matches with journal2")
                else:
                    print(f"fsck: file {k} does not match with journal1")
                    print("fsck: replaying entry")
                    # Append the key and its value from journal2 to jfiles
                    self.jfiles.append((k, journal2.get(k, b"\x00")))
            else:
                print(f"fsck: file {k} not found in journal1, replaying entry")
                self.jfiles.append((k, journal2.get(k, b"\x00")))

        # Check for entries in journal1 that are not in journal2
        for k in journal1.keys():
            if k not in journal2:
                print(f"fsck: file {k} found in journal1 but not in journal2, potentially missing")
                self.jfiles.append((k, journal1[k]))

    def WriteToJournalA(self, journal, data):
        j_ = data
        with open(journal, "wb") as j:
            j.write(zlib.compress(lzma.compress(pickle.dumps(j_))))

    def ReadFile(self, uid, packed):
        upmo(packed)
        with open(f"{uid}.chain", "r") as f:
            files = ast.literal_eval(f.read())

        with open(f"{uid}.mfhd", "rb") as f:
            compressed_data = f.read()
            decompressed_data = bytearray(lzma.decompress(zlib.decompress(compressed_data)))
            u = decompressed_data

        return files, u

    def Map(self, where, position=".", files=None):
        rData = bytearray(b"\x00")  # Use bytearray for efficient appending
        fMap = []
        if files is None:
            files = self.files
        else:
            self.files = files
        prev_off = 1
        prev_pos = os.getcwd()
        os.chdir(position)
        for file in self.files:
            if file.endswith("/"):
                fMap.append([file + ".fsNONE-00000", 0, 1])
                continue
            with open(file, 'rb') as f:
                d = f.read()
                start_offset = prev_off
                end_offset = prev_off + len(d)
                fMap.append((file, start_offset, end_offset))
                rData.extend(d)
                prev_off += len(d)
        os.chdir(prev_pos)
        for file in self.jfiles:
            d = file[1]
            start_offset = prev_off
            end_offset = prev_off + len(d)
            fMap.append((file[0], start_offset, end_offset))
            rData.extend(d)
            prev_off += len(d)


        self.filesaved = where
        with open(where + '.chain', 'w') as f:
            f.write(str(fMap))

        # Compress and save rData
        compressed_data = lzma.compress(rData, check=lzma.CHECK_NONE)
        compressed_data = zlib.compress(compressed_data, level=7)
        with open(where + '.mfhd', 'wb') as f:
            f.write(compressed_data)

        if not os.path.exists('journal+' + where):
            self.WriteToJournalA(f"journal+{self.filesaved}", [])
        if not os.path.exists('./block/'):
            os.makedirs('./block', exist_ok=True)
        pmo([where + '.mfhd', where + '.chain', f'journal+{where}'], 'block/' + where)

        return fMap, rData

    def Unmap(self, mapFsData, echo=False):
        rData = mapFsData[1]
        fMap = mapFsData[0]
        a = []
        for o in fMap:
            start, end = o[1], o[2]
            file_data = rData[start:end]  # Correctly slice rData based on offsets
            if echo:
                print(f"File: {o[0]}")
                print(f"Data: {''.join([chr(c) for c in file_data])}")  # Decode to string, handling errors
            else:
                a.append(''.join([chr(c) for c in file_data]))
        if not echo:
            return [f[0] for f in fMap], a
    
    def Open(self):
        self.journal = {}
        prev_pos = os.getcwd()
        os.chdir(self.filesaved)
        for entry in recursive_listdir("."):
            if entry.endswith("/"):
                continue
            with open(entry, 'rb') as f:
                self.journal[entry] = f.read()
                print(self.journal)
        os.chdir(prev_pos)
        with open(f'journal+{self.filesaved}', 'rb') as journal:
            try:
                journal2 = pickle.loads(lzma.decompress(zlib.decompress(journal.read())))
            except zlib.error as e:
                journal2 = self.journal
                print("fsck: skipping verification for this time; unsupported compression")
                print(f"fsck: the error at the moment of the exception was triggered is:\n{e}")
        if type(journal2) == list:
            print("fsck: skipping verification for this time; outdated format")
        journal2 = self.journal
        #print(custom_journal, journal2)
        self.checkJournal(journal2, self.journal)
        self.state_OPEN = True

    def Close(self, mounted=False):
        prev_pos = os.getcwd()
        os.chdir(self.filesaved)
        for entry in recursive_listdir("."):
            if entry.endswith("/"):
                continue
            with open(entry, 'rb') as f:
                self.journal[entry] = f.read()
        if mounted:
            files = recursive_listdir(".")
        else:
            files = self.files
        os.chdir(prev_pos)
        self.WriteToJournalA(f'journal+{self.filesaved}', self.journal)
        self.state_OPEN = False
        self.Map(self.at, self.at, files)
        shutil.rmtree(self.filesaved)

class MapFSInterface:
    @staticmethod
    def extract(data: tuple, mfs: MapFS, of: str):
        os.makedirs(of, exist_ok=True)
        files = [f for f in data[0]]
        od = mfs.Unmap(data)[1]
        prev_pos = os.getcwd()
        os.chdir(of)
        for fi, fo in enumerate(files):
            #print(fo[0])
            if os.path.dirname(fo[0]) != '': os.makedirs(os.path.dirname(fo[0]), exist_ok=True)
            with open(f"{fo[0]}", "w") as f:
                f.write(od[fi])
        os.chdir(prev_pos) 

    def MountVD(mfs: MapFS, target, of, open=False):
        if open:
            mfs.Open()
        Mount(of, target)

    def UnmountVD(mfs: MapFS, target):
        mfs.Close(True)
        UMount(target)
        subprocess.run(['sudo', 'rmdir', target])
        os.remove(mfs.filesaved + '.chain')
        os.remove(mfs.filesaved + '.mfhd')
        os.remove('journal+' + mfs.filesaved)

    def SwitchToTargetCmd(target):
        subprocess.call(['bash', '-c', f'cd {target} && clear && exec bash'])

mfs = MapFS([], "fs")
print(mfs.version())
data = mfs.ReadFile("fs", "block/fs")
MapFSInterface.extract(data, mfs, "fs")
input("press enter")
mfs.Open()
MapFSInterface.MountVD(mfs, '/media/nah/MAPFS', 'fs')
#MapFSInterface.SwitchToTargetCmd('/media/nah/MAPFS')
MapFSInterface.UnmountVD(mfs, '/media/nah/MAPFS')
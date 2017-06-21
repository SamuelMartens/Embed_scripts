BIN_FILE_DESTINATION = r""
COMPILE_TARGET = "lpc1768"
COMPILE_TOOLCHAIN = "GCC_ARM"

import os
from subprocess import call
from shutil import copy
from os.path import join

def Get_bin_file_path():
    search_path = join("..", "BUILD", COMPILE_TARGET, COMPILE_TOOLCHAIN)
    for item in os.listdir(search_path):
        if item.endswith(".bin"):
            return join(search_path, item)
    return ""

def main():
    print "Compilation started"
    
    # Compile project
    compilation_res = call(["mbed", "compile", "-t", COMPILE_TOOLCHAIN, "-m", COMPILE_TARGET])
    if compilation_res != 0:
        print "Compilation error"
        return
    print "Comilation success"
    
    # Copy .bin file to destination
    bin_file_path = Get_bin_file_path()
    if not bin_file_path:
        print "Bin file is not found"

    if not BIN_FILE_DESTINATION:
        print "Binary file destination is empty. Bin file location is: " + bin_file_path
        return

    copy(bin_file_path, BIN_FILE_DESTINATION)
    print "Bin file copied from" + bin_file_path + " to " + BIN_FILE_DESTINATION
    

if __name__ == "__main__":
    main()

COMPILE_TARGET = "lpc1768"
COMPILE_TOOLCHAIN = "GCC_ARM"

from subprocess import call
from shutil import copyfile

def main():
    # Compile project
    call(["mbed", "compile", "-t", COMPILE_TOOLCHAIN, "-m", COMPILE_TARGET])
    

if __name__ == "__main__":
    main()

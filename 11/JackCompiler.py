import os
import sys
from CompilationEngine import CompilationEngine
NUMBER_OF_ARGUMENTS = 1
PATH_SOURCE = 1
JACK_SUFFIX = '.jack'
XML_SUFFIX = '.vm'
NO_BACK_SLASH = -1

def main():
    if os.path.isdir(path):
        new_path = path
        if path.endswith("/"):
            new_path = path[:-1]
        for filename in os.listdir(new_path):
            if filename.endswith(JACK_SUFFIX):
                CompilationEngine(new_path + '/' + filename, new_path + '/' + filename[:-5] + XML_SUFFIX)
    else:
        CompilationEngine(path, path[:-5] + XML_SUFFIX)


if __name__ == "__main__":
    # if the user inserted the right amount of values.
    if len(sys.argv) == NUMBER_OF_ARGUMENTS + 1:
        path = sys.argv[PATH_SOURCE]
        main()
import os

import sys

import re

# Constants
ARITHMETIC_OPERATIONS = ('add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not')
memory_table = {'local': 'LCL', 'argument': 'ARG','this': 'THIS', 'that':'THAT', 'static':'16', 'temp':'5'}
C_PUSH = 'push'
C_POP = 'pop'
C_ARITHMETIC = 'arithmetic'
VM_SUFFIX = ".vm"
NO_BACK_SLASH = -1
NUMBER_OF_ARGUMENTS = 1
PATH_SOURCE = 1
NO_PATH = ""
EMPTY_LINE = ""
FIRST_CHAR = 0
FIRST_ARG_INDEX = 1
SECOND_ARG_INDEX = 2
TRUE_JUMP = 9
CONTINUE_JUMP = 7

# generic asm operation
CONST_PUSH = 'D=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
POINTER_POP = '@SP\nA=M\nA=A-1\nD=M\n@SP\nM=M-1\n'
POINTER_PUSH = 'D=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
GENERIC_PUSH = 'D=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
START_POP = '@SP\nD=M\nM=M-1\nA=D-1\nD=M\n'

# asm arithmetic operations
ADD='@SP\nA=M\nA=A-1\nD=M\nA=A-1\nD=D+M\nM=D\n@SP\nM=M-1\n'
SUB= '@SP\nA=M\nA=A-1\nA=A-1\nD=M\nA=A+1\nD=D-M\nA=A-1\nM=D\n@SP\nM=M-1\n'
NEGATIVE = '@SP\nA=M\nA=A-1\nM=-M\n'
EQ_1 = '@SP\nA=M\nA=A-1\nD=M\nA=A-1\nD=D-M\n'
EQ_2 = 'D;JEQ\n@SP\nA=M\nA=A-1\nA=A-1\nM=0\n'
EQ_3 = '0;JMP\n@SP\nA=M\nA=A-1\nA=A-1\nM=-1\n@SP\nM=M-1\n'


GT = '@SP\nA=M\nA=A-1\nD=M\n@YBigger$$\nD;JGT\n@SP\nA=M\nA=A-1\nA=A-1\nD=M\n@Check$$\nD;JLT\n(TRUE$$)\n' \
     '@SP\nA=M\nA=A-1\nA=A-1\nM=-1\n@END$$\n0;JMP\n(YBigger$$)\n@SP\nA=M\nA=A-1\nA=A-1\nD=M\n@Check$$\n' \
     'D;JGT\n(False$$)\n@SP\nA=M\nA=A-1\nA=A-1\nM=0\n@END$$\n0;JMP\n(Check$$)\n@SP\nA=M\nA=A-1\nD=M\n' \
     'A=A-1\nD=D-M\n@False$$\nD;JGE\n@TRUE$$\n0;JMP\n(END$$)\n@SP\nM=M-1\n'

LT = '@SP\nA=M\nA=A-1\nD=M\n@YBigger$$\nD;JGT\n@SP\nA=M\nA=A-1\nA=A-1\nD=M\n@Check$$\nD;JLT\n(False$$)\n' \
     '@SP\nA=M\nA=A-1\nA=A-1\nM=0\n@END$$\n0;JMP\n(YBigger$$)\n@SP\nA=M\nA=A-1\nA=A-1\nD=M\n@Check$$\n' \
     'D;JGT\n(TRUE$$)\n@SP\nA=M\nA=A-1\nA=A-1\nM=-1\n@END$$\n0;JMP\n(Check$$)\n@SP\nA=M\nA=A-1\nD=M\n' \
     'A=A-1\nD=D-M\n@False$$\nD;JLE\n@TRUE$$\n0;JMP\n(END$$)\n@SP\nM=M-1\n'

AND = '@SP\nA=M\nA=A-1\nD=M\nA=A-1\nM=D&M\n@SP\nM=M-1\n'
OR = '@SP\nA=M\nA=A-1\nD=M\nA=A-1\nM=D|M\n@SP\nM=M-1\n'
NOT = '@SP\nA=M\nA=A-1\nM=!M\n'

# Regexes
ONE_SPACE=' '
COMMENT_REG = '//'
LEGAL_CHAR_REG = '[a-zA-Z0-9]'

# Data
vm_lines = []
asm_line = ''
tag_counter = 0


def execute_vm_file(path, filename, isdir, is_first_file):
    vm_file = open(path, 'r')
    for line in vm_file:
        to_add, line_to_add = legal_line(line)
        if to_add:
            vm_lines.append(line_to_add)
    for command in vm_lines:
        if command_type(command) == C_ARITHMETIC:
            writeArithmetic(command)
        else:
            writePushPop(command_type(command), command)
    if isdir:
        create_file_for_directory(path, filename, is_first_file)
    else:
        create_file(path, filename)


def legal_line(line):
    empty_line = line.isspace()  # the line is empty
    if empty_line:
        return False, EMPTY_LINE
    search_comment_line = re.search(COMMENT_REG, line)
    if search_comment_line:
        if search_comment_line.start() == FIRST_CHAR:  # all the line is a comment line
            return False, EMPTY_LINE
        else:  # part of the line is comment
            line = line[FIRST_CHAR:search_comment_line.start()]
            match_empty_line = line.isspace()
            if match_empty_line:
                return False, EMPTY_LINE
    line = re.sub('\s+', ' ', line).strip()
    return True, line


def command_type(command):
    if command.startswith(ARITHMETIC_OPERATIONS):
        return C_ARITHMETIC
    elif command.startswith(C_PUSH):
        return C_PUSH
    else:
        return C_POP


def get_arg1(command, type):
    if type == C_ARITHMETIC:
        return command
    # the type is pop or push
    else:
        return command.split(ONE_SPACE)[FIRST_ARG_INDEX]


def get_arg2(command, type):
    if type == C_PUSH or type == C_POP:
        return command.split(ONE_SPACE)[SECOND_ARG_INDEX]

def writePushPop(type, command):
    global asm_line
    arg1 = get_arg1(command, type)
    arg2 = get_arg2(command, type)
    if type == C_PUSH: # push command
        if arg1 == 'constant':  # constant command
            asm_line += '@'+arg2+'\n'
            asm_line += CONST_PUSH
        elif arg1 == 'pointer':
            if int(arg2) == 0:
                asm_line += '@THIS\n'+POINTER_PUSH
            else:
                asm_line += '@THAT\n' + POINTER_PUSH
        else:  # LCL,THAT,THIS,ARG,STATIC, temp commands
            if arg1 != 'temp':
                asm_line += '@'+memory_table[arg1]+'\nA=M\n'
            else:
                asm_line += '@'+memory_table[arg1]+'\n'
            asm_line += 'A=A+1\n'*int(arg2)
            asm_line += GENERIC_PUSH
    if type == C_POP:
        if arg1 == 'pointer':
            if int(arg2) == 0:
                asm_line += POINTER_POP + '@THIS\nM=D\n'
            else:
                asm_line += POINTER_POP + '@THAT\nM=D\n'
            return
        if arg1 == 'temp':
            asm_line += START_POP
            asm_line += '@'+memory_table[arg1]+'\n'
            asm_line += 'A=A+1\n' * int(arg2)
            asm_line += 'M=D\n'
            return
        asm_line += START_POP
        asm_line += '@'+memory_table[arg1]+'\nA=M\n'
        asm_line += 'A=A+1\n'*int(arg2)
        asm_line += 'M=D\n'


def writeArithmetic(type):
    global asm_line
    global tag_counter
    if type == 'add':
        asm_line += ADD
    elif type == 'sub':
        asm_line += SUB
    elif type == 'neg':
        asm_line += NEGATIVE
    elif type == 'eq':
        asm_line += EQ_1
        line_count = asm_line.count('\n')
        asm_line += '@'+str(line_count+TRUE_JUMP)+'\n'
        asm_line += EQ_2
        line_count = asm_line.count('\n')
        asm_line += '@'+str(line_count+CONTINUE_JUMP)+'\n'
        asm_line += EQ_3
    elif type == 'gt':
        tag_counter += 1
        asm_line += GT.replace('$$', str(tag_counter))

    elif type == 'lt':
        tag_counter += 1
        asm_line += LT.replace('$$', str(tag_counter))


    elif type == 'and':
        asm_line += AND
    elif type == 'or':
        asm_line += OR
    elif type == 'not':
        asm_line += NOT

def clear_data():
    global vm_lines
    global asm_line
    vm_lines=[]
    asm_line=''

def create_file(name, file_path):
    if file_path.rfind("/") == NO_BACK_SLASH:
        file = open(name[:-2] + 'asm', 'w')
    else:
        file = open(file_path + '/' + name[:-2] + 'asm', 'w')
    file.write(asm_line)
    file.close()

def create_file_for_directory(file_path, name, first_file):
    if file_path.endswith("/"):
        file_path = file_path[:-1]
    if first_file:
        file = open(file_path[:file_path.rfind("/") + 1] + name + '.asm', 'w')
    else:
        file = open(file_path[:file_path.rfind("/")+1] + name + '.asm', 'a')
    file.write(asm_line)
    file.close()


def main():
    if os.path.isdir(path):
        directory_name = os.path.relpath(path)
        is_first_file = True
        for filename in os.listdir(path):
            if filename.endswith(VM_SUFFIX):
                execute_vm_file(path + '/' + filename, directory_name, True, is_first_file)
                is_first_file = False
                clear_data()
    else:
        if path.rfind("/") == NO_BACK_SLASH:
            execute_vm_file(path, path, False, True)
        else:
            execute_vm_file(path, path[path.rfind("/") + 1:], False, True)


if __name__ == "__main__":
    # if the user inserted the right amount of values.
    if len(sys.argv) == NUMBER_OF_ARGUMENTS + 1:
        path = sys.argv[PATH_SOURCE]
        main()


import os

import sys

import re

# Constants
ARITHMETIC_OPERATIONS = ('add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not')
memory_table = {'local': 'LCL', 'argument': 'ARG', 'this': 'THIS', 'that': 'THAT', 'static': '16',
                'temp': '5'}
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
ADD = '@SP\nA=M\nA=A-1\nD=M\nA=A-1\nD=D+M\nM=D\n@SP\nM=M-1\n'
SUB = '@SP\nA=M\nA=A-1\nA=A-1\nD=M\nA=A+1\nD=D-M\nA=A-1\nM=D\n@SP\nM=M-1\n'
NEGATIVE = '@SP\nA=M\nA=A-1\nM=-M\n'
EQ = '@SP\nA=M-1\nD=M\nA=A-1\nD=D-M\n@TRUE$$\nD;JEQ\n@SP\nM=M-1\nA=M-1\nM=0\n@END$$\n0;JMP\n(TRUE$$)\n' \
     '@SP\nM=M-1\nA=M-1\nM=-1\n(END$$)\n'


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
ONE_SPACE = ' '
COMMENT_REG = '//'
LEGAL_CHAR_REG = '[a-zA-Z0-9]'

# Data
vm_lines = []
# asm_line = ''
asm_line = '@256\nD=A\n@SP\nM=D\n'

tag_counter = 0
static_counter = 0

### project 8 ###
REPLACE_SIGN = '$$'
GLOBAL = ''
W_LABEL = '($$)\n'
W_GOTO = '@$$\n0;JMP\n'
W_IF = '@SP\nD=M-1\nM=M-1\nA=D\nD=M\n@$$\nD;JNE\n'
W_CALL = '@ret.label$$\nD=A\n@SP\nM=M+1\nA=M-1\nM=D\n@LCL\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n@ARG\nD=M\n@SP\nM=M+1\n' \
         'A=M-1\nM=D\n@THIS\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n@THAT\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n@SP\nD=M\n@5\nD=D-A\n' \
         '@&&\nD=D-A\n@ARG\nM=D\n@SP\nD=M\n@LCL\nM=D\n@##\n0;JMP\n(ret.label$$)\n'
W_FUNCTION = 'D=A\n@SP\nM=M+D\nA=M\n'
W_RETURN = '@LCL\nD=M\n@R13\nM=D\n@5\nA=D-A\nD=M\n@R14\nM=D\n@SP\nA=M-1\nD=M\n@ARG\nA=M\nM=D\nD=A+1\n@SP\nM=D\n' \
           '@R13\nA=M-1\nD=M\n@THAT\nM=D\n@2\nD=A\n@R13\nA=M-D\nD=M\n@THIS\nM=D\n@3\nD=A\n@R13\nA=M-D\n' \
           'D=M\n@ARG\nM=D\n@4\nD=A\n@R13\nA=M-D\nD=M\n@LCL\nM=D\n@R14\nA=M\n0;JMP\n'

C_LABEL = 'label'
C_GOTO = 'goto'
C_IF_GOTO = 'if-goto'
C_FUNCTION = 'function'
C_CALL = 'call'
C_RETURN = 'return'

scopes = []
call_counter = 0
RET_LABEL = 'ret.label$$'


def write_label(command, parent):
    global asm_line
    label_name = get_arg1(command,C_LABEL)
    if parent == GLOBAL:
        asm_line += W_LABEL.replace(REPLACE_SIGN, label_name)
    else:
        asm_line += W_LABEL.replace(REPLACE_SIGN, parent + label_name)


def write_goto(command, parent):
    global asm_line
    label_name = get_arg1(command, C_GOTO)
    asm_line += W_GOTO.replace(REPLACE_SIGN, parent + label_name)


def write_if(command, parent):
    global asm_line
    label_name = get_arg1(command, C_IF_GOTO)
    asm_line += W_IF.replace(REPLACE_SIGN, parent + label_name)

# def write_call(function_name, num_args):


def write_function(command):
    global asm_line
    global scopes
    if scopes:
        scopes.pop()
    function_name = get_arg1(command, C_FUNCTION)
    scopes.append(function_name)
    n_var = get_arg2(command, C_FUNCTION)
    asm_line += W_LABEL.replace(REPLACE_SIGN, function_name)+'@'+str(n_var)+'\n'
    asm_line += W_FUNCTION
    asm_line += 'A=A-1\nM=0\n'*int(n_var)


def write_return():
    global asm_line
    global scopes
    asm_line += W_RETURN


def write_call(command):
    global asm_line
    global scopes
    global call_counter
    function_name = get_arg1(command, C_FUNCTION)
    scopes.append(function_name)
    num_args = get_arg2(command, C_CALL)
    # Replace 3 signs of counter labels and number of args
    asm_line += W_CALL.replace(REPLACE_SIGN, str(call_counter)).replace('&&', str(num_args))\
        .replace('##', function_name)
    call_counter += 1
    scopes.pop()


def execute_vm_file(path, filename, isdir, is_first_file):
    global scopes
    vm_file = open(path, 'r')
    for line in vm_file:
        to_add, line_to_add = legal_line(line)
        if to_add:
            vm_lines.append(line_to_add)
    for command in vm_lines:
        if command_type(command) == C_ARITHMETIC:
            writeArithmetic(command)
        elif command_type(command) == C_PUSH or command_type(command) == C_POP:
            writePushPop(command_type(command), command)
        elif command_type(command) == C_LABEL:
            if not scopes:
                # the scope is global
                write_label(command, GLOBAL)
            else :
                write_label(command, scopes[-1] + '$')
        elif command_type(command) == C_GOTO:
            if not scopes:
                # the scope is global
                write_goto(command, GLOBAL)
            else:
                write_goto(command, scopes[-1] + '$')
        elif command_type(command) == C_IF_GOTO:
            if not scopes:
                # the scope is global
                write_if(command, GLOBAL)
            else:
                write_if(command, scopes[-1] + '$')
        elif command_type(command) == C_FUNCTION:
            write_function(command)
        elif command_type(command) == C_RETURN:
            write_return()
        elif command_type(command) == C_CALL:
            write_call(command)

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
    elif command.startswith(C_POP):
        return C_POP
    elif command.startswith(C_LABEL):
        return C_LABEL
    elif command.startswith(C_GOTO):
        return C_GOTO
    elif command.startswith(C_IF_GOTO):
        return C_IF_GOTO
    elif command.startswith(C_FUNCTION):
        return C_FUNCTION
    elif command.startswith(C_CALL):
        return C_CALL
    elif command.startswith(C_RETURN):
        return C_RETURN


def get_arg1(command, type):
    if type == C_ARITHMETIC:
        return command
    # the type is pop or push
    else:
        return command.split(ONE_SPACE)[FIRST_ARG_INDEX]


def get_arg2(command, type):
    if type != C_ARITHMETIC:
        return command.split(ONE_SPACE)[SECOND_ARG_INDEX]


def writePushPop(type, command):
    global asm_line
    arg1 = get_arg1(command, type)
    arg2 = get_arg2(command, type)
    if type == C_PUSH:  # push command
        if arg1 == 'constant':  # constant command
            asm_line += '@' + arg2 + '\n'
            asm_line += CONST_PUSH
        elif arg1 == 'pointer':
            if int(arg2) == 0:
                asm_line += '@THIS\n' + POINTER_PUSH
            else:
                asm_line += '@THAT\n' + POINTER_PUSH
        elif arg1 == 'static':
            if not scopes:
                # the scope is global
                asm_line += '@Global$STATIC' + arg2 + '\n'
            else:
                class_name = scopes[-1][:scopes[-1].find('.')]
                asm_line += '@' + class_name + '$STATIC' + arg2 + '\n'
            asm_line += 'D=M\n@SP\nM=M+1\nA=M-1\nM=D\n'
        else:  # LCL, THAT, THIS, ARG, temp commands
            if arg1 != 'temp':
                asm_line += '@' + memory_table[arg1] + '\nA=M\n'
            else:
                asm_line += '@' + memory_table[arg1] + '\n'
            asm_line += 'A=A+1\n' * int(arg2)
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
            asm_line += '@' + memory_table[arg1] + '\n'
            asm_line += 'A=A+1\n' * int(arg2)
            asm_line += 'M=D\n'
            return
        if arg1 == 'static':
            asm_line += START_POP
            if not scopes:
                # the scope is global
                asm_line += '@Global$STATIC' + arg2 + '\n'
            else:
                class_name = scopes[-1][:scopes[-1].find('.')]
                asm_line += '@' + class_name + '$STATIC' + arg2 + '\n'
            asm_line += 'M=D\n'
            return
        asm_line += START_POP
        asm_line += '@' + memory_table[arg1] + '\nA=M\n'
        asm_line += 'A=A+1\n' * int(arg2)
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
        tag_counter += 1
        asm_line += EQ.replace('$$', str(tag_counter))
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
    vm_lines = []
    asm_line = ''


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
        file = open(file_path[:file_path.rfind("/") + 1] + name + '.asm', 'a')
    file.write(asm_line)
    file.close()


def main():
    write_call('call Sys.init 0')
    if os.path.isdir(path):
        new_path = path
        if path.endswith("/"):
            new_path = path[:-1]
        directory_name = os.path.basename(new_path)
        is_first_file = True
        for filename in os.listdir(new_path):
            if filename.endswith(VM_SUFFIX):
                execute_vm_file(new_path + '/' + filename, directory_name, True, is_first_file)
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

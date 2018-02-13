import os
import re
import math
import sys

# MAGIC_NUMBERS

FIRST_CHAR = 0
FIRST_RAM_INDEX = 16
BINARY_BASE = 2
REGISTER_SIZE = 15
A_INTSRUCTION_SIGN = "@"
DEST_SIGN = '='
JMP_SIGN = ';'
MEMORY_SIGN = 'M'
ADDRESS_SIGN = 'A'
NUMBER_OF_ARGUMENTS = 1
PATH_SOURCE = 1
NO_BACK_SLASH = -1

# regexes

EMPTY_LINE = '\s'
COMMENT = '//'
BRACKETS = '\(.*\)'
NUMBER = '\d+'

# Constants
PATH = "/cs/usr/roi1255/Desktop/Fill.asm"

# Data bases
symbolTableFirst = {'R0': 0, 'R1': 1, 'R2': 2, 'R3': 3, 'R4': 4, 'R5': 5, 'R6': 6, 'R7': 7,
                    'R8': 8, 'R9': 9, 'R10': 10, 'R11': 11, 'R12': 12, 'R13': 13, 'R14': 14,
                    'R15': 15, 'SCREEN': 16384, 'KBD': 24576, 'SP': 0, 'LCL': 1, 'ARG': 2,
                    'THIS': 3, 'THAT': 4}

symbolTable = {}

compTable = {'0': '101010', '1': '111111', '-1': '111010', 'D': '001100',
             'A': '110000', '!D': '001101', '!A': '110001', '-D': '001111',
             '-A': '110011', 'D+1': '011111', 'A+1': '110111', 'D-1': '001110',
             'A-1': '110010', 'D+A': '000010', 'D-A': '010011', 'A-D': '000111',
             'D&A': '000000', 'D|A': '010101', 'D>>': '010000', 'D<<': '110000', 'A>>': '000000',
             'A<<': '100000'}

shiftSymbols = ['D>>', 'D<<', 'A>>', 'A<<', 'M<<', 'M>>']

destTable = {'': '000', 'M': '001', 'D': '010', 'MD': '011', 'A': '100', 'AM': '101', 'AD': '110',
             'AMD': '111'}
jumpTable = {'': '000', 'JGT': '001', 'JEQ': '010', 'JGE': '011', 'JLT': '100', 'JNE': '101', 'JLE': '110',
             'JMP': '111'}
lines = []
assembly_lines = []


# Functions


def clear_array():
    """
    clear the globals arrays of the lines and the assembly lines
    :return:
    """
    while len(lines) != 0:
        lines.pop()
    while len(assembly_lines) != 0:
        assembly_lines.pop()


def legal_line(line, counter_line):
    """
    :param line: the line that should check it legality
    :param counter_line: number of line that inserted
    :return: True and the legal part of the line if it legal, otherwise False
    """
    empty_line = line.isspace()  # the line is empty
    if empty_line:
        return False, ""
    search_comment_line = re.search(COMMENT, line)
    if search_comment_line:
        if search_comment_line.start() == FIRST_CHAR:  # all the line is a comment line
            return False, ""
        else:  # part of the line is comment
            line = line[FIRST_CHAR:search_comment_line.start() - 1]
            match_empty_line = line.isspace()
            if match_empty_line:
                return False, ""
    brackets = re.search(BRACKETS, line)
    if brackets:  # if there is a (XXX) in the file
        symbolTable.update({line[brackets.start() + 1:brackets.end() - 1]: counter_line})
        return False, ""
    return True, line


def first_pass(path):
    """
    Make first pass over the file and add the lines that relevant to the assembly to the lines array
    :param path: the path of the file
    """
    symbolTable = symbolTableFirst.copy()
    assembly_file = open(path, 'r')
    counter_line = 0
    for line in assembly_file:
        add_or_not, line_to_add = legal_line(line, counter_line)
        if add_or_not:
            counter_line += 1
            # re.sub(EMPTY_LINE,"",line_to_add)
            lines.append(re.sub(EMPTY_LINE, "", line_to_add))


def decimal_to_binary(num):
    """
    convert decimal base number to binary base number
    :param num: decimal number
    :return: binary number
    """
    binary_res = ""
    while num >= 1:
        binary_char = num % BINARY_BASE
        num = math.floor(num / BINARY_BASE)
        binary_res += str(binary_char)
    if len(binary_res) < REGISTER_SIZE:
        binary_res += "0" * (REGISTER_SIZE - len(binary_res))
    return binary_res[::-1]


def second_pass():
    """
    After the first pass occur the second pass work on pure assembly line that converted to binary lines
    """
    curr_ram_index = FIRST_RAM_INDEX
    for line in lines:
        if line.startswith(A_INTSRUCTION_SIGN):
            symbol = line[1:]
            match_symbol_number = re.match(NUMBER, symbol)
            if match_symbol_number:
                assembly_line = decimal_to_binary(int(symbol))
                assembly_lines.append("0" + assembly_line)
                symbolTable.update({symbol: assembly_line})
                continue
            if symbol in symbolTable:
                assembly_line = decimal_to_binary(symbolTable[symbol])
                assembly_lines.append("0" + assembly_line)
            elif symbol in symbolTableFirst:
                assembly_line = decimal_to_binary(symbolTableFirst[symbol])
                assembly_lines.append("0" + assembly_line)
            else:
                symbolTable.update({symbol: curr_ram_index})
                assembly_line = decimal_to_binary(curr_ram_index)
                assembly_lines.append("0" + assembly_line)
                curr_ram_index += 1
        # C- Instruction
        else:
            assembly_lines.append(c_instruction_parser(line))


def c_instruction_parser(c_instruction):
    """
    Parse a assembly c- instruction
    :param c_instruction:  assembly c-inctruction line
    :return: 16-bit number that represent c-instruction
    """
    binary_res = '111'
    dest, comp, jmp = '', '', ''
    # split the c-instruction into 3 parts - dest, comp, jmp.
    if DEST_SIGN in c_instruction:
        dest, comp = c_instruction.split(DEST_SIGN)
    else:
        comp = c_instruction
    if JMP_SIGN in comp:
        comp, jmp = comp.split(JMP_SIGN)
    if comp in shiftSymbols:
        binary_res = '101'
    # change the M chars in comp to A (to make the comp table smaller)
    if MEMORY_SIGN in comp:
        binary_res += '1'
        comp = comp.replace(MEMORY_SIGN, ADDRESS_SIGN)
    else:
        binary_res += '0'
    binary_res += compTable[comp]
    binary_res += destTable[dest]
    binary_res += jumpTable[jmp]
    return binary_res


def execute_asm_file(file_path, file_name):
    """
    full iteration and convertion on a single .asm file
    :param file_path: path of the file
    :param file_name: name of the file
    """
    first_pass(file_path)
    second_pass()
    if file_path.rfind("/") == NO_BACK_SLASH:
        create_file(file_name, file_path)
    else:
        create_file(file_name, file_path[:file_path.rfind("/")])


def create_file(name, file_path):
    if file_path.rfind("/") == NO_BACK_SLASH:
        file = open(name[:-3] + 'hack', 'w')
    else:
        file = open(file_path + '/' + name[:-3] + 'hack', 'w')
    for line in assembly_lines:
        file.write(line + '\n')
    file.close()
    clear_array()


def main():
    """
    execute the Assembler program
    """
    if os.path.isdir(path):
        for filename in os.listdir(path):
            if filename.endswith('.asm'):
                execute_asm_file(path + '/' + filename, filename)
    else:
        execute_asm_file(path, path[path.rfind("/") + 1:])


if __name__ == "__main__":
    # if the user inserted the right amount of values.
    if len(sys.argv) == NUMBER_OF_ARGUMENTS + 1:
        path = sys.argv[PATH_SOURCE]
        main()

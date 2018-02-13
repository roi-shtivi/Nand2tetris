import re

# MAGIC_NUMBERS
FIRST_CHAR = 0

# Grammar
KEYWORD = {'class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void',
           'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return'}
SYMBOLS = {'(', ')', '[', ']', '{', '}', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'}

# Constants
TYPE_KEYWORD = 'keyword'
TYPE_SYMBOL = 'symbol'
TYPE_IDENTIFIER = 'identifier'
TYPE_INT_CONST = 'integerConstant'
TYPE_STRING_CONST = 'stringConstant'

KEYWORD_CLASS = 'class'
KEYWORD_METHOD = 'method'
KEYWORD_FUNCTION = 'function'
KEYWORD_CONSTRUCTOR = 'constructor'
KEYWORD_INT = 'int'
KEYWORD_BOOLEAN = 'boolean'
KEYWORD_CHAR = 'char'
KEYWORD_VOID = 'void'
KEYWORD_VAR = 'var'
KEYWORD_STATIC = 'static'
KEYWORD_FIELD = 'field'
KEYWORD_LET = 'let'
KEYWORD_DO = 'do'
KEYWORD_IF = 'if'
KEYWORD_ELSE = 'else'
KEYWORD_WHILE = 'while'
KEYWORD_RETURN = 'return'
KEYWORD_TRUE = 'true'
KEYWORD_FALSE = 'false'
KEYWORD_NULL = 'null'
KEYWORD_THIS = 'this'

#REGEX
COMMENT1_REG = '//'
COMMENT2_REG = '/\\*\\*'
COMMENT3_REG = '/\\*'

END_COMMENT_1 = '\n'
END_COMMENT2_3 = '\\*/'

STRING_REG = '"(.*?)"'
INPUT_TEST_PATH = '/cs/usr/roi1255/Desktop/nand2tetris/projects/10/ArrayTest/danitest.jack'
OUTPUT_TEST_PATH = '/cs/usr/roi1255/Desktop/nand2tetris/projects/10/ArrayTest/danitest.blha'


class JackTokenizer:
    """
    Get a full path to the jack file
    """

    def __init__(self, path):
        self.jack_file = open(path, 'r')
        self.jack_string = ''
        self.clean_string = ''
        self.all_tokens = []
        self.token_index = -1
        self.curr_token = ''

        self.clean_empty_line()
        self.clean_comments()
        self.create_tokens()

    def clean_empty_line(self):
        for line in self.jack_file:
            if not line.isspace():
                self.jack_string += line

    def clean_comments(self):
        self.jack_string +='\n'
        max_index = len(self.jack_string)+1
        comment1,comment2,comment3= [COMMENT1_REG,END_COMMENT_1,max_index, -1, 0],\
                                    [COMMENT2_REG, END_COMMENT2_3, max_index, -1, 2],\
                                    [COMMENT3_REG, END_COMMENT2_3, max_index, -1, 2]
        search_comment1 = re.search(COMMENT1_REG, self.jack_string)
        search_comment2 = re.search(COMMENT2_REG, self.jack_string)
        search_comment3 = re.search(COMMENT3_REG, self.jack_string)

        while search_comment1 or search_comment2 or search_comment3:
            if search_comment1:  # comment // was found
                comment1[2] = search_comment1.start()

            if search_comment2:  # comment /** was found
                comment2[2] = search_comment2.start()

            if search_comment3:  # comment /* was found
                comment3[2] = search_comment3.start()
            current_comment = []
            # Finds min
            if comment1[2] < comment2[2] and comment1[2] < comment3[2]:
                current_comment = comment1
            elif comment2[2] <= comment3[2] and comment2[2] < comment1[2]:
                current_comment = comment2
            else:
                current_comment = comment3
            search_quote = re.search(STRING_REG, self.jack_string)
            if search_quote and (search_quote.start() < current_comment[2]):  #qoute was found before any comment
                self.clean_string += self.jack_string[:search_quote.end()]
                self.jack_string = self.jack_string[search_quote.end():]
            else:
                suffix = self.jack_string[current_comment[2]:]
                current_comment[3] = re.search(current_comment[1], suffix).start()
                self.clean_string += self.jack_string[:current_comment[2]]+' '
                if current_comment[3] != len(self.jack_string)-1:
                    self.jack_string = self.jack_string[current_comment[2] + current_comment[3] + current_comment[4]:]
                else:
                    break
            comment1, comment2, comment3 = [COMMENT1_REG, END_COMMENT_1, max_index, -1, 0], \
                                           [COMMENT2_REG, END_COMMENT2_3, max_index, -1, 2], \
                                           [COMMENT3_REG, END_COMMENT2_3, max_index, -1, 2]
            search_comment1 = re.search(COMMENT1_REG, self.jack_string)
            search_comment2 = re.search(COMMENT2_REG, self.jack_string)
            search_comment3 = re.search(COMMENT3_REG, self.jack_string)
        self.clean_string += self.jack_string
        self.clean_string = self.clean_string.replace('\n+', '\n').strip()  # replace multi empty lines with one empty line

    def create_tokens(self):
        temp_string = ''
        is_string = False

        for char in self.clean_string:
            if char == '"':
                is_string = not is_string
            if not is_string:
                if char in SYMBOLS:
                    # if char == '<':
                    #     temp_string += '\n&lt;\n'
                    # elif char == '>':
                    #     temp_string += '\n&gt;\n'
                    # elif char == '&':
                    #     temp_string += '\n&amp;\n'
                    # else:
                        temp_string += '\n' + char + '\n'
                elif char.isspace():
                    temp_string += '\n'
                elif char == '"':
                    temp_string += '&quot'
                else:
                        temp_string += char
            else:
                if char == '"':
                    temp_string += '&quot'
                else:
                    temp_string += char
        temp_tokens = temp_string.split('\n')
        for token in temp_tokens:
            if not token.isspace() and token != '':
                self.all_tokens.append(token)

    def has_more_tokens(self):
        if self.token_index > (len(self.all_tokens) - 1):
            return False
        return True

    def advance(self):
        self.token_index += 1
        self.curr_token = self.all_tokens[self.token_index]
        return self.all_tokens[self.token_index]

    def token_type(self):
        current_token = self.all_tokens[self.token_index]
        if current_token in KEYWORD:
            return TYPE_KEYWORD
        elif current_token in SYMBOLS:
            return TYPE_SYMBOL
        elif current_token.isdigit():
            return TYPE_INT_CONST
        elif current_token.startswith('&quot'):
            return TYPE_STRING_CONST
        else:
            return TYPE_IDENTIFIER

    def key_word(self):
        current_token = self.all_tokens[self.token_index]
        if current_token == KEYWORD_CLASS:
            return KEYWORD_CLASS
        elif current_token == KEYWORD_METHOD:
            return KEYWORD_METHOD
        elif current_token == KEYWORD_FUNCTION:
            return KEYWORD_FUNCTION
        elif current_token == KEYWORD_CONSTRUCTOR:
            return KEYWORD_CONSTRUCTOR
        elif current_token == KEYWORD_INT:
            return KEYWORD_CONSTRUCTOR
        elif current_token == KEYWORD_BOOLEAN:
            return KEYWORD_BOOLEAN
        elif current_token == KEYWORD_CHAR:
            return KEYWORD_CHAR
        elif current_token == KEYWORD_VOID:
            return KEYWORD_VOID
        elif current_token == KEYWORD_VAR:
            return KEYWORD_VAR
        elif current_token == KEYWORD_STATIC:
            return KEYWORD_STATIC
        elif current_token == KEYWORD_FIELD:
            return KEYWORD_FIELD
        elif current_token == KEYWORD_LET:
            return KEYWORD_LET
        elif current_token == KEYWORD_DO:
            return KEYWORD_DO
        elif current_token == KEYWORD_IF:
            return KEYWORD_IF
        elif current_token == KEYWORD_ELSE:
            return KEYWORD_ELSE
        elif current_token == KEYWORD_WHILE:
            return KEYWORD_WHILE
        elif current_token == KEYWORD_RETURN:
            return KEYWORD_RETURN
        elif current_token == KEYWORD_TRUE:
            return KEYWORD_TRUE
        elif current_token == KEYWORD_FALSE:
            return KEYWORD_FALSE
        elif current_token == KEYWORD_NULL:
            return KEYWORD_NULL
        elif current_token == KEYWORD_THIS:
            return KEYWORD_THIS

    def current_token(self):
        return self.all_tokens[self.token_index]

    def get_next_token(self):
        return self.all_tokens[self.token_index+1]

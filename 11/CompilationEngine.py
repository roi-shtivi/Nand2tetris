import xml.etree.cElementTree as ET
from xml.dom import minidom
from JackTokenizer import JackTokenizer
from symbolTable import symbolTable
from VMWriter import VMWriter


# Constants
TERM_KEYWORD = 'keyword'
TERM_SYMBOL = 'symbol'
TERM_IDENTIFIER = 'identifier'
TERM_INT_CONST = 'integerConstant'
TERM_STRING_CONST = 'stringConstant'

TYPES = {'int', 'char', 'boolean', 'void'}
VAR_TYPES = {'int', 'char', 'boolean', 'void'}
OP = {'+', '-', '*', '/', '&', '|', '<', '>', '='}
OP_TRANSLATOR = {'+': 'add', '-': 'sub', '*': 'call Math.multiply 2', '/': 'call Math.divide 2', '&': 'and',
                 '|': 'or', '<': 'lt', '>': 'gt', '=': 'eq'}
UNARY_OP_TRANSLATOR = {'-': 'neg', '~': 'not'}
KEYWORD = 'keyword'
SYMBOL = 'symbol'
IDENTIFIER = 'identifier'
TEMP = 'temp'
POINTER = 'pointer'
THAT = 'that'
THIS = 'this'
CONSTANT = 'constant'
FIELD = 'this'
ARGUMENT = 'argument'
IF_TRUE = 'IF_TRUE'
IF_FALSE = 'IF_FALSE'
IF_END = 'IF_END'
WHILE_LABEL = 'WHILE_EXP'
END_WHILE = 'WHILE_END'
LOCAL = 'local'

class CompilationEngine:

    def __init__(self, input_path, output_path):
        self.class_name = ''
        self.subroutine_name = ''
        self.if_counter = -1
        self.while_counter = -1
        self.subroutine_num_arg = 0
        self.tkx = JackTokenizer(input_path)
        self.class_table = symbolTable()
        self.subroutine_table = symbolTable()
        self.vm_writer = VMWriter(output_path)
        self.compile_class(output_path)

    def compile_class(self, output_path):
        """
        complete class
        """
        #Class
        self.tkx.advance()

        #className
        self.subroutine_table.class_name = self.tkx.advance()
        self.class_name = self.tkx.current_token()

        #{
        self.tkx.advance()

        self.tkx.advance()
        while self.tkx.current_token() == 'static' or self.tkx.current_token() == 'field':
            self.compile_class_var_dec()
            self.tkx.advance()

        while self.tkx.current_token() == 'constructor' or self.tkx.current_token() == 'function' or self.tkx.current_token() == 'method':
            self.compile_subroutine_dec()
            self.tkx.advance()

        # tree = ET.ElementTree(root)
        # rough_string = ET.tostring(root, 'utf-8')
        # reparsed = minidom.parseString(rough_string)
        # out_file = open(output_path, 'w')
        # out_file.write(reparsed.toprettyxml(indent="\t")[reparsed.toprettyxml(indent="\t").find('\n')+1:])

    def compile_subroutine_dec(self):
        """
        static declaration or field declaration
        """
        self.if_counter = -1
        self.while_counter = -1
        was_constructor = False
        was_method = False
        is_type = True
        # constructor or function or method

        subroutine = self.tkx.current_token()

        # void or type
        self.tkx.advance()  # todo check if we need 2 advances

        self.subroutine_table.start_subroutine()

        if subroutine == 'constructor':
            was_constructor = True

        else:
            if subroutine == 'method':
                was_method = True
                self.subroutine_table.define(THIS, self.class_name, 'argument')
                self.subroutine_num_arg = 1
        self.subroutine_name = self.class_name + '.'

        # subroutine name
        self.tkx.advance()
        self.subroutine_name += self.tkx.current_token()

        #todo: check is_type

        # (
        self.tkx.advance()

        self.compile_parameter_list()

        self.compile_subroutine_body(was_constructor, was_method)

    def compile_parameter_list(self):
        """
        parameter list
        """

        if self.tkx.advance() != ')':
            # type
            type = self.tkx.current_token()

            # var name
            name = self.tkx.advance()

            self.subroutine_table.define(name, type, 'argument')
        else:
            return

        self.tkx.advance()
        while self.tkx.current_token() != ')':

            # type
            type = self.tkx.advance()

            # var name
            name = self.tkx.advance()
            self.subroutine_table.define(name, type, 'argument')
            self.tkx.advance()

    def compile_subroutine_body(self, was_constructor, was_method):
        """
        subroutine body
        Inside declaration
        """
        # self.subroutine_num_arg = 0
        # {
        self.tkx.advance()

        # var declaration
        while self.tkx.get_next_token() == 'var':
            self.compile_var_dec()

        self.vm_writer.write_function(self.subroutine_name, self.subroutine_table.var_count(LOCAL))
        if was_constructor:
            self.vm_writer.write_push(CONSTANT, self.class_table.var_count(FIELD))
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop(POINTER, 0)
        elif was_method:
            self.vm_writer.write_push(ARGUMENT, 0)
            self.vm_writer.write_pop(POINTER, 0)
        self.compile_statements()

    def compile_class_var_dec(self):
        """
        class variable declaration
        """
        self.subroutine_num_arg = 0
        # static or field
        kind = self.tkx.current_token()

        # type
        type = self.tkx.advance()

        # var name
        name = self.tkx.advance()

        self.class_table.define(name, type, kind)

        self.tkx.advance()
        while self.tkx.current_token() != ';':
            # var name
            name = self.tkx.advance()
            self.class_table.define(name, type, kind)
            self.tkx.advance()

    def compile_var_dec(self):
        """
        variable declaration
        """
        # var
        self.tkx.advance()

        # type
        type = self.tkx.advance()

        # var name
        name = self.tkx.advance()

        self.subroutine_table.define(name, type, LOCAL)

        self.tkx.advance()
        while self.tkx.current_token() != ';':
            # var name
            name = self.tkx.advance()
            self.subroutine_table.define(name, type, LOCAL)
            self.tkx.advance()


    def compile_statements(self):
        """
        statements
        """
        # for each statement in statements
        self.tkx.advance()

        while self.tkx.current_token() != '}':
            self.compile_statement()
            self.tkx.advance()

    def compile_statement(self):
        if self.tkx.current_token() == 'let':
            self.compile_let()
        elif self.tkx.current_token() == 'if':
            self.compile_if()
        elif self.tkx.current_token() == 'do':
            self.compile_do()
        elif self.tkx.current_token() == 'while':
            self.compile_while()
        elif self.tkx.current_token() == 'return':
            self.compile_return()


    def compile_let(self):
        """
        let statement
        After that this is a var declaration
        'let' varName ('['expression']')? '=' expression ';'
        """
        was_array = False
        name = self.tkx.advance()  # identifier
        if self.tkx.advance() == '[':
            self.compile_expression()
            kind = self.get_kind(name)
            index = self.get_index(name)

            self.vm_writer.write_push(kind, index)
            self.vm_writer.write_arithmetic('add')

            was_array = True
            # ']'
            self.tkx.advance()

        self.compile_expression()  # =
        if not was_array:
            kind = self.get_kind(name)
            index = self.get_index(name)

            self.vm_writer.write_pop(kind, index)
        else:
            self.vm_writer.write_pop(TEMP, 0)
            self.vm_writer.write_pop(POINTER, 1)
            self.vm_writer.write_push(TEMP, 0)
            self.vm_writer.write_pop(THAT, 0)


    def compile_if(self):
        """
        if statement
        'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        """
        isElse = False
        self.if_counter += 1
        label_if = self.if_counter
        self.tkx.advance()  # '(' symbol
        self.compile_expression()
        self.vm_writer.write_if_goto(IF_TRUE + str(label_if))
        self.vm_writer.write_goto(IF_FALSE + str(label_if))
        self.vm_writer.write_label(IF_TRUE + str(label_if))
        # ')' symbol
        self.tkx.advance()  # '{' symbol
        self.compile_statements()

        # self.vm_writer.write_label(IF_FALSE + str(self.if_counter))
        # '}' symbol
        if self.tkx.get_next_token() == 'else':
            isElse = True
            self.vm_writer.write_goto(IF_END + str(label_if))
            self.vm_writer.write_label(IF_FALSE + str(label_if))

            self.tkx.advance()  # else
            self.tkx.advance()  # '{' symbol
            self.compile_statements()

            # '}' symbol

        if isElse:
            self.vm_writer.write_label(IF_END + str(label_if))
        else:
            self.vm_writer.write_label(IF_FALSE + str(label_if))


    def compile_do(self):
        """
        do statement
        """
        # do

        # name
        name = self.tkx.advance()

        self.tkx.advance()

        self.compile_subroutine_call(name, True)

        # ;
        self.tkx.advance()

    def compile_while(self):
        """
        while statement
        """
        self.while_counter += 1
        while_label = self.while_counter
        self.vm_writer.write_label(WHILE_LABEL + str(while_label))

        self.tkx.advance()  # '(' symbol
        self.compile_expression()
        self.vm_writer.write_arithmetic('not')
        self.vm_writer.write_if_goto(END_WHILE + str(while_label))
        # ')' symbol
        self.tkx.advance()  # '{' symbol
        self.compile_statements()
        # '}' symbol
        self.vm_writer.write_goto(WHILE_LABEL + str(while_label))
        self.vm_writer.write_label(END_WHILE + str(while_label))

    def compile_return(self):
        """
        return statement
        """
        # return
        if self.tkx.get_next_token() != ';':
            self.compile_expression()
            self.vm_writer.write_return()
            # ;
            return
        self.vm_writer.write_push(CONSTANT, 0)
        # ;
        self.tkx.advance()
        self.vm_writer.write_return()


    def compile_expression(self):
        """
        expression
        Maybe after all "()"
        """
        self.tkx.advance()
        self.compile_term()

        while self.tkx.current_token() in OP:
            op = self.tkx.current_token()
            self.tkx.advance()
            self.compile_term()
            self.vm_writer.write_arithmetic(OP_TRANSLATOR[op])

    def compile_expression_list(self):
        """
        expression list
        Maybe after all "()" that in call to function
        """
        self.subroutine_num_arg = 0
        if self.tkx.get_next_token() != ')':
            self.compile_expression()
            self.subroutine_num_arg += 1

        else:
            self.tkx.advance()
            return

        while self.tkx.current_token() != ')':
            self.compile_expression()
            self.subroutine_num_arg += 1

    def compile_term(self):
        """
        term
        Distinguish between the kinds by "(", "." and "["
        (See the explanation in the book)
        """
        if self.tkx.token_type() == TERM_INT_CONST:
            self.vm_writer.write_push(CONSTANT, str(self.tkx.current_token()))
            self.tkx.advance()
        elif self.tkx.token_type() == TERM_STRING_CONST:
            self.write_string_const(self.tkx.current_token())
            self.tkx.advance()
        elif self.tkx.token_type() == TERM_KEYWORD:
            if self.tkx.current_token() in {'true', 'false', 'null'}:
                self.vm_writer.write_push(CONSTANT, 0)
                if self.tkx.current_token() == 'true':
                    self.vm_writer.write_arithmetic('not')
            else:  # this
                self.vm_writer.write_push(POINTER, 0)
            self.tkx.advance()
        elif self.tkx.token_type() == TERM_SYMBOL:
            if self.tkx.current_token() == '(':
                self.compile_expression()
                self.tkx.advance()
            else:
                unary_op = self.tkx.current_token()
                self.tkx.advance()
                self.compile_term()
                self.vm_writer.write_arithmetic(UNARY_OP_TRANSLATOR[unary_op])
        elif self.tkx.token_type() == TERM_IDENTIFIER:
            name = self.tkx.current_token()
            kind = self.get_kind(name)
            index = self.get_index(name)
            self.tkx.advance()
            if self.tkx.current_token() == '[':
                self.compile_expression()
                self.vm_writer.write_push(kind, index)
                self.vm_writer.write_arithmetic('add')
                self.vm_writer.write_pop(POINTER, 1)
                self.vm_writer.write_push(THAT, 0)
                # ]
                self.tkx.advance()
            elif self.tkx.current_token() == '(' or self.tkx.current_token() == '.':
                self.compile_subroutine_call(name, False)
                self.tkx.advance()
            else:
                self.vm_writer.write_push(kind, index)

    def compile_subroutine_call(self, name, isDo):
        """
        subroutine call
        """
        was_method = False
        if self.tkx.current_token() == '.':

            kind = self.get_kind(name)
            if kind:
                index = self.get_index(name)
                self.vm_writer.write_push(kind, index)
                was_method = True
                name = self.get_type(name) + '.' + self.tkx.advance()
            # subroutine name
            else:
                name += '.' + self.tkx.advance()

            # (
            self.tkx.advance()

        elif '.' not in name:
            name = self.class_name + '.' + name
            was_method = True
            self.vm_writer.write_push(POINTER, 0)
        self.compile_expression_list()
        if was_method:
            self.subroutine_num_arg += 1

        self.vm_writer.write_call(name, self.subroutine_num_arg)
        self.subroutine_num_arg = 0
        if isDo:
            self.vm_writer.write_pop(TEMP, 0)

        # )


    def get_kind(self, name):
        if  self.subroutine_table.kind_of(name) is not None:
            return self.subroutine_table.kind_of(name)
        return self.class_table.kind_of(name)


    def get_type(self, name):
        if self.subroutine_table.type_of(name) is not None:
            return self.subroutine_table.type_of(name)
        return self.class_table.type_of(name)

    def get_index(self, name):
        if self.subroutine_table.index_of(name) is not None:
            return self.subroutine_table.index_of(name)
        return self.class_table.index_of(name)

    def write_string_const(self, str):
        re_str = str.replace('&quot', '')
        self.vm_writer.write_push(CONSTANT, len(re_str))
        self.vm_writer.write_call('String.new', 1)
        for char in re_str:
            self.vm_writer.write_push(CONSTANT, ord(char))
            self.vm_writer.write_call("String.appendChar", 2)


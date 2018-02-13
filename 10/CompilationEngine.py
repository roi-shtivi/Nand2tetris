import xml.etree.cElementTree as ET
from xml.dom import minidom
from JackTokenizer import JackTokenizer


# Constants
TERM_KEYWORD = 'keyword'
TERM_SYMBOL = 'symbol'
TERM_IDENTIFIER = 'identifier'
TERM_INT_CONST = 'integerConstant'
TERM_STRING_CONST = 'stringConstant'

TYPES = {'int', 'char', 'boolean', 'void'}
VAR_TYPES = {'int', 'char', 'boolean', 'void'}
OP = {'+', '-', '*', '/', '&', '|', '<', '>', '='}
KEYWORD = 'keyword'
SYMBOL = 'symbol'
IDENTIFIER = 'identifier'

class CompilationEngine:

    def __init__(self, input_path, output_path):
        self.tkx = JackTokenizer(input_path)
        self.compile_class(output_path)

    def compile_class(self, output_path):
        """
        complete class
        """
        root = ET.Element("class")
        #Class
        current_token = self.tkx.advance()
        ET.SubElement(root, KEYWORD).text = current_token

        #className
        current_token = self.tkx.advance()
        ET.SubElement(root, IDENTIFIER).text = current_token
        TYPES.add(current_token)

        #{
        current_token = self.tkx.advance()
        ET.SubElement(root, SYMBOL).text = current_token

        self.tkx.advance()
        while self.tkx.current_token() == 'static' or self.tkx.current_token() == 'field':
            self.compile_class_var_dec(root)
            self.tkx.advance()

        while self.tkx.current_token() == 'constructor' or self.tkx.current_token() == 'function' or self.tkx.current_token() == 'method':
            self.compile_subroutine_dec(root)
            self.tkx.advance()

        # }
        ET.SubElement(root, SYMBOL).text = self.tkx.current_token()

        tree = ET.ElementTree(root)
        rough_string = ET.tostring(root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        out_file = open(output_path, 'w')
        out_file.write(reparsed.toprettyxml(indent="\t")[reparsed.toprettyxml(indent="\t").find('\n')+1:])

    def compile_subroutine_dec(self, root):
        """
        static declaration or field declaration
        """
        subroutine_dec_root = ET.SubElement(root, "subroutineDec")

        # constructor or function or method
        ET.SubElement(subroutine_dec_root, KEYWORD).text = \
            self.tkx.current_token()

        # void or type

        if self.tkx.advance() in VAR_TYPES:
            ET.SubElement(subroutine_dec_root, KEYWORD).text = self.tkx.current_token()
        else:
            ET.SubElement(subroutine_dec_root, IDENTIFIER).text = self.tkx.current_token()

        # subroutine name
        ET.SubElement(subroutine_dec_root, IDENTIFIER).text = \
            self.tkx.advance()

        # (
        ET.SubElement(subroutine_dec_root, SYMBOL).text = self.tkx.advance()

        self.compile_parameter_list(subroutine_dec_root)

        # )
        ET.SubElement(subroutine_dec_root, SYMBOL).text = \
            self.tkx.current_token()

        self.compile_subroutine_body(subroutine_dec_root)

    def compile_parameter_list(self, root):
        """
        parameter list
        """
        parameter_list_root = ET.SubElement(root, "parameterList")

        if self.tkx.advance() != ')':
            # type
            if self.tkx.current_token() in VAR_TYPES:
                ET.SubElement(parameter_list_root, KEYWORD).text = self.tkx.current_token()
            else:
                ET.SubElement(parameter_list_root, IDENTIFIER).text = self.tkx.current_token()
            # var name
            ET.SubElement(parameter_list_root, IDENTIFIER).text = \
                self.tkx.advance()
        else:
            parameter_list_root.text = '\n'
            return

        self.tkx.advance()
        while self.tkx.current_token() != ')':
            # ,
            ET.SubElement(parameter_list_root, SYMBOL).text = \
                self.tkx.current_token()

            # type
            if self.tkx.advance() in VAR_TYPES:
                ET.SubElement(parameter_list_root, KEYWORD).text = self.tkx.current_token()
            else:
                ET.SubElement(parameter_list_root, IDENTIFIER).text = self.tkx.current_token()
            # var name
            ET.SubElement(parameter_list_root, IDENTIFIER).text = \
                self.tkx.advance()

            self.tkx.advance()

    def compile_subroutine_body(self, root):
        """
        subroutine body
        Inside declaration
        """
        subroutine_body_root = ET.SubElement(root, "subroutineBody")

        # {
        ET.SubElement(subroutine_body_root, SYMBOL).text = \
            self.tkx.advance()

        # var declaration
        while self.tkx.get_next_token() == 'var':
            self.compile_var_dec(subroutine_body_root)

        self.compile_statements(subroutine_body_root)

        # }
        ET.SubElement(subroutine_body_root, SYMBOL).text = \
            self.tkx.current_token()

    def compile_class_var_dec(self, root):
        """
        class variable declaration
        """
        var_dec_root = ET.SubElement(root, "classVarDec")
        # static or field
        ET.SubElement(var_dec_root, KEYWORD).text = self.tkx.current_token()
        # type
        if self.tkx.advance() in VAR_TYPES:
            ET.SubElement(var_dec_root, KEYWORD).text = self.tkx.current_token()
        else:
            ET.SubElement(var_dec_root, IDENTIFIER).text = self.tkx.current_token()

        # var name
        ET.SubElement(var_dec_root, IDENTIFIER).text = self.tkx.advance()

        self.tkx.advance()
        while self.tkx.current_token() != ';':
            # ,
            ET.SubElement(var_dec_root, SYMBOL).text = \
                self.tkx.current_token()
            # var name
            ET.SubElement(var_dec_root, IDENTIFIER).text = self.tkx.advance()
            self.tkx.advance()

        # ;
        ET.SubElement(var_dec_root, SYMBOL).text = self.tkx.current_token()


    def compile_var_dec(self, root):
        """
        variable declaration
        """
        var_dec_root = ET.SubElement(root, "varDec")
        self.tkx.advance()
        # var
        ET.SubElement(var_dec_root, KEYWORD).text = self.tkx.current_token()
        # type
        if self.tkx.advance() in VAR_TYPES:
            ET.SubElement(var_dec_root, KEYWORD).text = self.tkx.current_token()
        else:
            ET.SubElement(var_dec_root, IDENTIFIER).text = self.tkx.current_token()
        # var name
        ET.SubElement(var_dec_root, IDENTIFIER).text = self.tkx.advance()

        self.tkx.advance()
        while self.tkx.current_token() != ';':
            # ,
            ET.SubElement(var_dec_root, SYMBOL).text = \
                self.tkx.current_token()
            # var name
            ET.SubElement(var_dec_root, IDENTIFIER).text = self.tkx.advance()
            self.tkx.advance()

        # ;
        ET.SubElement(var_dec_root, SYMBOL).text = self.tkx.current_token()


    def compile_statements(self, root):
        """
        statements
        """
        statements_root = ET.SubElement(root, "statements")

        # for each statement in statements
        self.tkx.advance()
        if self.tkx.current_token() == '}':
            statements_root.text = '\n'
        while self.tkx.current_token() != '}':
            self.compile_statement(statements_root)
            self.tkx.advance()

    def compile_statement(self, root):
        if self.tkx.current_token() == 'let':
            self.compile_let(root)
        elif self.tkx.current_token() == 'if':
            self.compile_if(root)
        elif self.tkx.current_token() == 'do':
            self.compile_do(root)
        elif self.tkx.current_token() == 'while':
            self.compile_while(root)
        elif self.tkx.current_token() == 'return':
            self.compile_return(root)


    def compile_let(self, root):
        """
        let statement
        After that this is a var declaration
        'let' varName ('['expression']')? '=' expression ';'
        """
        let_root = ET.SubElement(root, "letStatement")
        ET.SubElement(let_root, KEYWORD).text = self.tkx.current_token()  # let
        ET.SubElement(let_root, IDENTIFIER).text = self.tkx.advance()  # identifier
        if self.tkx.advance() == '[':
            ET.SubElement(let_root, SYMBOL).text = self.tkx.current_token()
            self.compile_expression(let_root)
            ET.SubElement(let_root, SYMBOL).text = self.tkx.current_token() #']'
            self.tkx.advance()

        ET.SubElement(let_root,SYMBOL).text = self.tkx.current_token()  # '=' symbol
        self.compile_expression(let_root)
        ET.SubElement(let_root,SYMBOL).text = self.tkx.current_token()  # ';' symbol

    def compile_if(self, root):
        """
        if statement
        'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        """
        if_root = ET.SubElement(root, "ifStatement")
        ET.SubElement(if_root, KEYWORD).text = self.tkx.current_token()
        ET.SubElement(if_root, SYMBOL).text = self.tkx.advance()  # '(' symbol
        self.compile_expression(if_root)
        ET.SubElement(if_root, SYMBOL).text = self.tkx.current_token()  # ')' symbol
        ET.SubElement(if_root, SYMBOL).text = self.tkx.advance()  # '{' symbol
        self.compile_statements(if_root)
        ET.SubElement(if_root, SYMBOL).text = self.tkx.current_token()  # '}' symbol
        if self.tkx.get_next_token() == 'else':
            ET.SubElement(if_root, KEYWORD).text = self.tkx.advance() # else
            ET.SubElement(if_root, SYMBOL).text = self.tkx.advance()  # '{' symbol
            self.compile_statements(if_root)
            ET.SubElement(if_root, SYMBOL).text = self.tkx.current_token()  # '}' symbol


    def compile_do(self, root):
        """
        do statement
        """
        do_root = ET.SubElement(root, "doStatement")
        # do
        ET.SubElement(do_root, KEYWORD).text = self.tkx.current_token()

        # name
        ET.SubElement(do_root, IDENTIFIER).text = self.tkx.advance()
        self.tkx.advance()

        self.compile_subroutine_call(do_root)

        # ;
        ET.SubElement(do_root, SYMBOL).text = self.tkx.advance()

    def compile_while(self, root):
        """
        while statement
        """
        while_root = ET.SubElement(root, "whileStatement")
        ET.SubElement(while_root, KEYWORD).text = self.tkx.current_token()
        ET.SubElement(while_root, SYMBOL).text = self.tkx.advance()  # '(' symbol
        self.compile_expression(while_root)
        ET.SubElement(while_root, SYMBOL).text = self.tkx.current_token()  # ')' symbol
        ET.SubElement(while_root, SYMBOL).text = self.tkx.advance()  # '{' symbol
        self.compile_statements(while_root)
        ET.SubElement(while_root, SYMBOL).text = self.tkx.current_token()  # '}' symbol

    def compile_return(self, root):
        """
        return statement
        """
        return_root = ET.SubElement(root, "returnStatement")
        # return
        ET.SubElement(return_root, KEYWORD).text = self.tkx.current_token()

        if self.tkx.get_next_token() != ';':
            self.compile_expression(return_root)
            # ;
            ET.SubElement(return_root, SYMBOL).text = self.tkx.current_token()
            return

        # ;
        ET.SubElement(return_root, SYMBOL).text = self.tkx.advance()

    def compile_expression(self, root):
        """
        expression
        Maybe after all "()"
        """
        expression_root = ET.SubElement(root, "expression")

        self.tkx.advance()

        self.compile_term(expression_root)

        while self.tkx.current_token() in OP:
            ET.SubElement(expression_root, TERM_SYMBOL).text = \
                self.tkx.current_token()

            self.tkx.advance()

            self.compile_term(expression_root)


    def compile_expression_list(self, root):
        """
        expression list
        Maybe after all "()" that in call to function
        """
        expression_list_root = ET.SubElement(root, "expressionList")
        """
        Check if in the end of expression there is "advance" or "current"
        """
        if self.tkx.get_next_token() != ')':
            self.compile_expression(expression_list_root)
        else:
            self.tkx.advance()
            expression_list_root.text = '\n'
            return

        while self.tkx.current_token() != ')':
            # ,
            ET.SubElement(expression_list_root, SYMBOL).text = \
                self.tkx.current_token()

            self.compile_expression(expression_list_root)

    def compile_term(self, root):
        """
        term
        Distinguish between the kinds by "(", "." and "["
        (See the explanation in the book)
        """
        term_root = ET.SubElement(root, "term")
        type = self.tkx.token_type()
        if self.tkx.token_type() == TERM_INT_CONST:
            ET.SubElement(term_root, TERM_INT_CONST).text = self.tkx.current_token()
            self.tkx.advance()
        elif self.tkx.token_type() == TERM_STRING_CONST:
            ET.SubElement(term_root, TERM_STRING_CONST).text = self.tkx.current_token().replace('&quot', '')
            self.tkx.advance()
        elif self.tkx.token_type() == TERM_KEYWORD:
            ET.SubElement(term_root, TERM_KEYWORD).text = self.tkx.current_token()
            self.tkx.advance()
        elif self.tkx.token_type() == TERM_SYMBOL:
            ET.SubElement(term_root, TERM_SYMBOL).text = self.tkx.current_token()
            if self.tkx.current_token() == '(':
                self.compile_expression(term_root)
                # )
                ET.SubElement(term_root, TERM_SYMBOL).text = self.tkx.current_token()
                self.tkx.advance()
            else:
                self.tkx.advance()
                self.compile_term(term_root)
        elif self.tkx.token_type() == TERM_IDENTIFIER:
            ET.SubElement(term_root, TERM_IDENTIFIER).text = self.tkx.current_token()
            self.tkx.advance()
            if self.tkx.current_token() == '[':
                ET.SubElement(term_root, TERM_SYMBOL).text = self.tkx.current_token()
                self.compile_expression(term_root)
                # ]
                ET.SubElement(term_root, TERM_SYMBOL).text = self.tkx.current_token()
                self.tkx.advance()
            if self.tkx.current_token() == '(' or self.tkx.current_token() == '.':
                self.compile_subroutine_call(term_root)
                self.tkx.advance()

    def compile_subroutine_call(self, root):
        """
        subroutine call
        """

        if self.tkx.current_token() == '.':
            # .
            ET.SubElement(root, SYMBOL).text = \
                self.tkx.current_token()

            # subroutine name
            ET.SubElement(root, IDENTIFIER).text = \
                self.tkx.advance()

            self.tkx.advance()

        # (
        ET.SubElement(root, SYMBOL).text = \
            self.tkx.current_token()

        self.compile_expression_list(root)

        # )
        ET.SubElement(root, SYMBOL).text = \
            self.tkx.current_token()
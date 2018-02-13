
STATIC = 'static'
FIELD = 'field'
THIS = 'this'
ARG = 'argument'
LOCAL = 'local'

class symbolTable:

    def __init__(self):
        self.subroutineTable = {}
        self.class_name = ''
        self.argument_counter = -1
        self.var_counter = -1
        self.field_counter = -1
        self.static_counter = -1

    def start_subroutine(self):
        self.subroutineTable = {}
        self.argument_counter = -1
        self.var_counter = -1

    def define(self, name, type, kind):
        if kind == STATIC:
            self.static_counter += 1
            self.subroutineTable[name] = [type, kind, self.static_counter]
        elif kind == FIELD:
            self.field_counter += 1
            self.subroutineTable[name] = [type, THIS, self.field_counter]
        elif kind == LOCAL:
            self.var_counter += 1
            self.subroutineTable[name] = [type, kind, self.var_counter]
        elif kind == ARG:
            self.argument_counter += 1
            self.subroutineTable[name] = [type, kind, self.argument_counter]

    def var_count(self, kind):
        kind_counter = 0
        for val in self.subroutineTable.values():
            if val[1] == kind:
                kind_counter += 1
        return kind_counter

    def kind_of(self, name):
        for key in self.subroutineTable:
            if key == name:
                return self.subroutineTable[key][1]
        return None

    def type_of(self, name):
        for key in self.subroutineTable:
            if key == name:
                return self.subroutineTable[key][0]
        return None

    def index_of(self, name):
        for key in self.subroutineTable:
            if key == name:
                return self.subroutineTable[key][2]
        return None
#
# st = symbolTable()
# st.start_subroutine('Point')
# print(st.subroutineTable)
# st.define('bla', 'int', 'static')
# st.define('x', 'int', 'static')
# st.define('b', 'int', 'static')
# print(st.subroutineTable)
# print(st.var_count('static'))
# print(st.kind_of('t'))
# print(st.type_of('x'))
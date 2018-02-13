
class VMWriter:

    def __init__(self, path):
        # Check to which path to write
        self.jack_file = open(path, 'w')

    def write_push(self, segment, index):
        if segment is None:
            self.jack_file.write('push ' + str(index) + '\n')
        elif index is None:
            self.jack_file.write('push ' + segment + '\n')
        else:
            self.jack_file.write('push ' + segment + ' ' + str(index) + '\n')

    def write_pop(self, segment, index):
        if segment is None:
            self.jack_file.write('pop ' + str(index) + '\n')
        elif index is None:
            self.jack_file.write('pop ' + segment + '\n')
        else:
            self.jack_file.write('pop ' + segment + ' ' + str(index) + '\n')

    def write_arithmetic(self, command):
        self.jack_file.write(command + '\n')

    def write_label(self, name):
        self.jack_file.write('label ' + name + '\n')

    def write_goto(self, name):
        self.jack_file.write('goto ' + name + '\n')

    def write_if_goto(self, name):
        self.jack_file.write('if-goto ' + name + '\n')

    def write_call(self, name_func, nArgs):
        self.jack_file.write('call ' + name_func + ' ' + str(nArgs) + '\n')

    def write_function(self, name_func, nArgs):
        self.jack_file.write('function ' + name_func + ' ' + str(nArgs) + '\n')

    def write_return(self):
        self.jack_file.write('return\n')

    def close(self):
        # Maybe before close we need to delete the last newline
        self.jack_file.close()
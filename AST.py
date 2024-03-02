# Abstract Syntax Tree
class AST(object):
    pass

# Concatenation and Sum Node
class Op(AST):
    def __init__(self, op, children):
        self.token = op
        self.children = children

# Number Node 
class Num(AST):
    def __init__(self, token):
        self.token = token[0]
        self.value = token[1]

# List Node
class List(AST):
    def __init__(self, token, children):
        self.token = token[0]
        self.value = token[1]
        self.children = children

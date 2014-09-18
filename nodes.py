import random
import datetime
import ast

def NoneNode():
    return None

class Needs(object):
    def __init__(self, *node_types):
        self.node_type = random.choice(node_types)

class Node(object):
    def __str__(self):
        if not hasattr(self, "dependencies"):
            self.dependencies = {}
        try:
            result = self.explication.format(**self.dependencies)
            return result
        except AttributeError, e:
            return self.generate()

    def generate(self):
        return ""

class Statement(Node):
    def __init__(self):
        # Get all 'needs' nodes off the class
        cls = self.__class__

        if not hasattr(self, "explication"):
            self.explication = random.choice(self.explications)

        self.dependencies = { k:v.node_type() for k, v in cls.__dict__.items() if isinstance(v, Needs) }
        for k,v in self.dependencies.items():
            setattr(self, k, v)

    def sentence(self):
        phrase = str(self)
        return phrase[0].upper() + phrase[1:] + "."

"""

class ForStatement(Statement):
    pass

class WhileStatement(Statement):
    pass
    """

class Expression(Node):
    def __init__(self):
        cls = self.__class__
        self.dependencies = { k:v.node_type() for k, v in cls.__dict__.items() if isinstance(v, Needs) }
        for k,v in self.dependencies.items():
            setattr(self, k, v)

    def code(self, tabs=0):
        return "THIS ISN'T DONE YET" + self.__class__.__name__

class IntExpression(Expression):
    def __init__(self):
        Expression.__init__(self)
 
        self.number = random.randint(0, 100)
        self.dependencies["number"] = self.number

    explication = "the integer {number}"

    def code(self):
        return "%d"%self.number

class FloatExpression(Expression):
    def __init__(self):
        Expression.__init__(self)
        self.number = random.random() * 85
        self.dependencies = {"number": self.number}

    explication = "the number {number:.1f}"

    def code(self):
        return "%0.1f"%self.number


class StringExpression(Expression):
    STRINGS = [
            "hello world",
            "the cow jumped over the moon",
            "a b c d",
            "1 2 3",
            "pascal's triangle",
            '"This is a test"',
            "dumbledore's army",
            "the golden snitch",
            "potent potables",
            "fish fingers",
            "it's bigger on the inside"
            ]

    def __init__(self):
        Expression.__init__(self)
        self.str = random.choice(self.STRINGS)
        self.dependencies["str"] = self.str

    explication = "the string '{str}'"

    def code(self):
        return "%r"%self.str


class EmptyListExpression(Expression):
    explication = "an empty list"

    def code(self):
        return "[]"

def english_join(sequence):
    if len(sequence) == 1:
        return sequence[0]

    start = sequence[:-1]
    end = sequence[-1]
    return ", ".join(start) + " and " + end

class IntListExpression(Expression):
    def __init__(self):
        self.numbers = [ IntExpression() for i in range(random.randint(2,3)) ]
        self.dependencies = {"numberlist": english_join([str(num) for num in self.numbers])}

    explication = "a list containing {numberlist}"

    def code(self):
        return "[" + ", ".join(str(n.code()) for n in self.numbers) + "]"

class IDExpression(Expression):
    NAMES = ["i", "j", "y", "k", "x", "var",
             "foo", "bar", "baz",
             "my_var", "MyVar",
             "input",
             "my_input",
             "the_input",
             "the_greatest_variable_name_ever"]

    def __init__(self):
        self.name = random.choice(self.__class__.NAMES)
        self.dependencies = {"name": self.name}

    def code(self):
        return self.name

    explication = "the variable named '{name}'"

class ListIDExpression(Expression):
    NAMES = ["l", "my_list", "the_list", "seq", "sequence"]
    def __init__(self):
        self.name = random.choice(self.__class__.NAMES)
        self.dependencies = {"name": self.name}

    def code(self):
        return self.name

    explication = "a list named '{name}'"

class ListAccessExpression(Expression):
    lname = Needs(ListIDExpression)

    ordinals = ["first", "second", "third", "fourth", "fifth"]

    def __init__(self):
        Expression.__init__(self)
        self.index = random.randint(0, 4)
        self.dependencies["ordinal"] = self.ordinals[self.index]

    explication = "the {ordinal} element of {lname}"

    def code(self, tabs=0):
        return self.lname.code() + "[%d]"%self.index


class SimpleArithmeticExpression(Expression):
    lval = Needs(IntExpression, FloatExpression)
    rval = Needs(IntExpression, FloatExpression)

    ENGLISH = {
            "+": "{lval} added to {rval}",
            "-": "{rval} subtracted from {lval}",
            "/": "{lval} divided by {rval}",
            "*": "{lval} multiplied by {rval}"
            }

    def __init__(self):
        Expression.__init__(self)
        self.operator = random.choice(["+", "-", "*", "/"])
        self.explication = self.ENGLISH[self.operator]
        #print self.dependencies


    def code(self):
        return "%s %s %s"%(self.dependencies['lval'].code(),
                           self.operator,
                           self.dependencies['rval'].code())

class BooleanExpression(Expression):
    def __init__(self):
        Expression.__init__(self)
        self.bool = bool(random.randint(0, 1))
        self.dependencies['bool'] = self.bool

    explication = "the value {bool}"

    def code(self):
        return self.bool

class EqualityExpression(Expression):
    lval = Needs(IDExpression, ListAccessExpression)
    rval = Needs(BooleanExpression,
                 IntExpression,
                 FloatExpression)

    explication = "{lval} is equal to {rval}"

    def code(self):
        return "%s == %s"%(
                self.dependencies['lval'].code(),
                self.dependencies['rval'].code())

def clause(statement):
    return statement[0].lower() + statement[1:]

class AssignmentStatement(Statement):
    lval = Needs(IDExpression, ListAccessExpression)
    rval = Needs(IntExpression, FloatExpression, EmptyListExpression, IntListExpression, BooleanExpression,
                 SimpleArithmeticExpression,
                 StringExpression,
                 ListAccessExpression)
    explication = "assign {rval} to {lval}"

    def code(self, tabs = 0):
        if tabs:
            prefix = "    "
        else:
            prefix = ""
        return prefix + "%s = %s"%(self.lval.code(), 
                                   self.rval.code())

class PrintStatement(Statement):
    to_print = Needs(IDExpression, IntExpression, FloatExpression, IntListExpression, SimpleArithmeticExpression, StringExpression,
                     ListAccessExpression)
    explication = "print {to_print}"
    def code(self, tabs = 0):
        if tabs:
            prefix = "    "
        else:
            prefix = ""
        out = prefix + "print " + self.to_print.code()

        return out

class IfStatement(Statement):
    cond = Needs(EqualityExpression)
    truth = Needs(AssignmentStatement, PrintStatement)
    alt = Needs(AssignmentStatement, PrintStatement, NoneNode)

    expl_if = "if {cond}, then {truth}"
    expl_ifelse = "if {cond}, then {truth}. Otherwise, {alt}"

    explication = "if {cond}, then {truth}"

    def __init__(self):
        Statement.__init__(self)
        if self.alt:
            self.explication = self.expl_ifelse
        else:
            self.explication = self.expl_if

    def code(self, tabs=0):
        prefix = "    "*tabs
        lines = []
        lines.append("if " + self.cond.code() +":")
        lines.append(self.truth.code(tabs+1))
        if self.alt:
            lines.append("else:")
            lines.append(self.alt.code(tabs+1))
        return "\n".join([ prefix + l for l in lines ])

class ForStatement(Statement):
    var = Needs(IDExpression)
    iterable = Needs(ListIDExpression, IntListExpression)
    action = Needs(PrintStatement, AssignmentStatement, IfStatement)

    explications = ["Loop over {iterable} with the {var}. Each time, {action}",
                    "Iterate over {iterable} with the {var}. Each time, {action}"]

    def code(self, tabs=0):
        prefix = "    "*tabs
        lines = []
        lines.append("for " + self.var.code() + " in " + self.iterable.code() + ":")
        lines.append(self.action.code(tabs+1))

        return "\n".join([ prefix + l for l in lines ])


def sentence(statement):
    return statement[0].upper() + statement[1:] + "."

def generate(seed = None):
    if seed:
        random.seed(seed)
    
    # Choose a statement to generate
    subs = Statement.__subclasses__()
    stmt = random.choice(subs)()

    return stmt

if __name__ == "__main__":
    x = generate()
    print x.sentence()
    print ""
    print x.code()

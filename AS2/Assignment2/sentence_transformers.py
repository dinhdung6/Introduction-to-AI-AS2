import re
from lark import Lark, Transformer, v_args
from truthtable import *
from logic import *
from typing import List, Union
from lark.exceptions import ParseError

class Parser:
    def __init__(self, input):
        self.input = input
        self.position = 0

    def consume_whitespace(self):
        while self.position < len(self.input) and self.input[self.position].isspace():
            self.position += 1

    def match(self, string):
        self.consume_whitespace()
        if self.input.startswith(string, self.position):
            self.position += len(string)
            return True
        return False

    def parse_symbol(self):
        self.consume_whitespace()
        start_position = self.position
        while self.position < len(self.input) and self.input[self.position].isalnum():
            self.position += 1
        return Symbol(self.input[start_position:self.position])

    def parse_atom(self):
        if self.match("("):
            result = self.parse_biconditional()
            if not self.match(")"):
                raise Exception("Expected ')'")
            return result
        else:
            return self.parse_symbol()

    def parse_negation(self):
        if self.match("~"):
            return Negation(self.parse_atom())
        else:
            return self.parse_atom()

    def parse_conjunction(self):
        result = self.parse_disjunction()
        while self.match("&"):
            result = Conjunction(result, self.parse_disjunction())
        return result

    def parse_disjunction(self):
        result = self.parse_negation()
        while self.match("||"):
            result = Disjunction(result, self.parse_negation())
        return result

    def parse_implication(self):
        result = self.parse_conjunction()
        while self.match("=>"):
            result = Implication(result, self.parse_conjunction())
        return result

    def parse_biconditional(self):
        result = self.parse_implication()
        while self.match("<=>"):
            result = Biconditional(result, self.parse_implication())
        return result

    def parse(self):
        return self.parse_biconditional()

class SentenceTransformer(Transformer):
    def symbol(self, args):
        return Symbol(args[0].value)
    
    def atom(self, args):
        return args[0]

    def negation(self, args):
        return Negation(args[0])

    def conjunction(self, args):
        return Conjunction(*args)

    def disjunction(self, args):
        return Disjunction(*args)

    def implication(self, args):
        # For implications with conjunction in premise
        if isinstance(args[0], Conjunction):
            return Implication(args[0], args[1])
        return Implication(*args)

    def biconditional(self, args):
        return Biconditional(*args)

# Grammar definition
sentence_parser = Lark(r"""
    ?start: biconditional
    ?biconditional: implication
                  | biconditional "<=>" implication
    ?implication: conjunction
                | implication "=>" conjunction
    ?conjunction: disjunction
                | conjunction "&" disjunction
    ?disjunction: negation
                | disjunction "||" negation
    ?negation: "~" atom -> negation
            | atom
    atom: symbol
        | "(" biconditional ")"
    symbol: /[a-z0-9_]+/
    %import common.WS
    %ignore WS
""", start='start', parser='lalr', transformer=SentenceTransformer())
    
def parse(sentence):
    """Parse a logical sentence string into its corresponding logical structure"""
    try:
        return sentence_parser.parse(sentence)
    except Exception as e:
        print(f"Error parsing sentence: {sentence}")
        print(f"Error details: {e}")
        raise e


'''This parse method will be using Lark 
    which is the library of Python.
    If you want to use it, feel free change the name to 
    parse instead of parse1 and rename the above'''
def parse1(sentence):
    return sentence_parser.parse(sentence)


def create_knowledge_base(sentences):
    """Create a knowledge base from a list of sentence strings"""
    parsed_sentences = []
    for sentence in sentences:
        print(f"Before parsing: {sentence}")
        # Handle implications with conjunctions in premise
        if "=>" in sentence and "&" in sentence.split("=>")[0]:
            parts = sentence.split("=>")
            premise = parts[0].strip()
            conclusion = parts[1].strip()
            if "&" in premise:
                # Create conjunction object for premise
                premise_symbols = [Symbol(p.strip()) for p in premise.split("&")]
                parsed_sentence = Implication(Conjunction(*premise_symbols), Symbol(conclusion))
            else:
                parsed_sentence = parse(sentence)
        else:
            parsed_sentence = parse(sentence)
        print(f"After parsing: {parsed_sentence}")
        parsed_sentences.append(parsed_sentence)
    
    return Conjunction(*parsed_sentences)


# Debug Functions 
def parse_knowledge_base(kb_string):
    kb_list = []

    # Split the string into individual statements
    statements = re.split(r'\s*&\s*', kb_string)

    for statement in statements:
        # Implication
        if "=>" in statement:
            premise, conclusion = statement.strip("()").split(" => ")

            # Check if premise is a Conjunction
            if " & " in premise:
                conjuncts = [Symbol(s.strip()) for s in premise.split(" & ")]
                kb_list.append(Implication(Conjunction(*conjuncts), Symbol(conclusion)))
            else:
                kb_list.append(Implication(Symbol(premise), Symbol(conclusion)))

        # Symbol
        else:
            kb_list.append(Symbol(statement))

    return kb_list


def knowledge_base_to_string(kb_list):
    kb_string = ""

    for element in kb_list.args:
        # Implication
        if isinstance(element, Implication):
            premise = element.args[0]
            conclusion = element.args[1]

            # Check if the premise is a Conjunction
            if isinstance(premise, Conjunction):
                conjuncts = " & ".join(str(arg) for arg in premise.args)
                kb_string += f"({conjuncts} => {conclusion})"
            else:
                kb_string += f"({premise} => {conclusion})"

        # Symbol
        else:
            kb_string += str(element)

        kb_string += " & "

    # Remove the trailing " & " and return the string
    return kb_string[:-3]




# sentences = ['p2=>p3', 'p3=>p1', 'c=>e', 'b&e=>f', 'f&g=>h', 'p1=>d', 'p1&p3=>c', 'a', 'b', 'p2']
# knowledge_base = create_knowledge_base(sentences)
# print(knowledge_base)

# kb_string = knowledge_base_to_string(knowledge_base)
# print(kb_string)

# knowledge = parse_knowledge_base(kb_string)
# print(knowledge)
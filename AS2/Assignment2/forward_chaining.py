from sentence_transformers import *

class ForwardChaining:
    def __init__(self, KB, query):
        self.KB = KB
        self.query = str(query)

    def get_premises(self, conjunct):
        """Get premises from an implication"""
        if isinstance(conjunct, Implication):
            if isinstance(conjunct.args[0], Conjunction):
                return [str(arg) for arg in conjunct.args[0].args]
            return [str(conjunct.args[0])]
        return []

    def get_conclusion(self, conjunct):
        """Get conclusion from an implication"""
        if isinstance(conjunct, Implication):
            return str(conjunct.args[1])
        return None

    def fc_entails(self):
        # Initialize chain with facts from KB
        chain = []
        count = {}
        agenda = []

        # Initialize count and agenda with facts
        for conjunct in self.KB.conjuncts():
            if isinstance(conjunct, Symbol):
                agenda.append(str(conjunct))
                chain.append(str(conjunct))
            elif isinstance(conjunct, Implication):
                premises = self.get_premises(conjunct)
                count[conjunct] = len(premises)

        # Track which symbols have been processed
        inferred = {str(symbol): False for symbol in self.KB.symbols()}

        while agenda:
            p = agenda.pop(0)
            
            if p == self.query:
                return True, chain
                
            if not inferred[p]:
                inferred[p] = True
                
                for conjunct in self.KB.conjuncts():
                    if isinstance(conjunct, Implication):
                        premises = self.get_premises(conjunct)
                        if p in premises:
                            count[conjunct] -= 1
                            if count[conjunct] == 0:
                                conclusion = self.get_conclusion(conjunct)
                                if conclusion not in chain:
                                    agenda.append(conclusion)
                                    chain.append(conclusion)

        return self.query in chain, chain

    def solve(self):
        solution_found, chain = self.fc_entails()
        return "YES: " + ', '.join(chain) if solution_found else "NO"
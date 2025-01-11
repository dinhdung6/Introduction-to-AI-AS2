from sentence_transformers import *


class BackwardChaining:
    def __init__(self, KB, goal):
        self.KB = KB
        self.goal = str(goal)  # Convert goal to string for comparison
        
    def prove(self, removed, chain):
        # If goal is a fact in KB, return True
        for conjunct in self.KB.conjuncts():
            if isinstance(conjunct, Symbol) and str(conjunct) == self.goal:
                if self.goal not in chain:
                    chain.append(self.goal)
                return True, chain
        
        if self.goal in removed:
            return False, chain
            
        removed.append(self.goal)
        
        # Look for rules that conclude the goal
        for conjunct in self.KB.conjuncts():
            if isinstance(conjunct, Implication):
                conclusion = str(conjunct.args[1])
                if conclusion == self.goal:
                    premises = []
                    if isinstance(conjunct.args[0], Conjunction):
                        premises.extend(conjunct.args[0].args)
                    else:
                        premises.append(conjunct.args[0])
                    
                    # Try to prove all premises
                    all_proven = True
                    for premise in premises:
                        if str(premise) in chain:
                            continue
                            
                        bc = BackwardChaining(self.KB, str(premise))
                        premise_proven, updated_chain = bc.prove(removed.copy(), chain)
                        
                        if premise_proven:
                            chain = updated_chain
                        else:
                            all_proven = False
                            break
                    
                    if all_proven:
                        if self.goal not in chain:
                            chain.append(self.goal)
                        return True, chain
                        
        return False, chain
        
    def solve(self):
        solution_found, chain = self.prove([], [])
        return "YES: " + ', '.join(chain) if solution_found else "NO"

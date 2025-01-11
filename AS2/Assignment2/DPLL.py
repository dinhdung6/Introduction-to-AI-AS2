from typing import Dict, Set, Optional, List, Tuple
from logic import *

class DPLL:
    def __init__(self, knowledge_base: Sentence, query: Sentence):
        self.knowledge_base = knowledge_base
        self.query = query
        self.symbols = set.union(knowledge_base.symbols(), query.symbols())
        
    def to_cnf(self, sentence: Sentence) -> List[Set[Tuple[str, bool]]]:
        """Convert sentence to Conjunctive Normal Form (CNF)"""
        if isinstance(sentence, Symbol):
            return [{(sentence.name, True)}]
        elif isinstance(sentence, Negation):
            if isinstance(sentence.args[0], Symbol):
                return [{(sentence.args[0].name, False)}]
            elif isinstance(sentence.args[0], Conjunction):
                # Convert ~(A & B) to ~A || ~B
                return self.to_cnf(Disjunction(
                    Negation(sentence.args[0].args[0]),
                    Negation(sentence.args[0].args[1])
                ))
        elif isinstance(sentence, Conjunction):
            result = []
            for arg in sentence.args:
                result.extend(self.to_cnf(arg))
            return result
        elif isinstance(sentence, Implication):
            # Convert P => Q to ~P || Q
            negated_premise = Negation(sentence.args[0])
            disjunction = Disjunction(negated_premise, sentence.args[1])
            return self.to_cnf(disjunction)
        elif isinstance(sentence, Disjunction):
            # Convert to CNF recursively
            left_cnf = self.to_cnf(sentence.args[0])
            right_cnf = self.to_cnf(sentence.args[1])
            # Combine all clauses
            result = []
            for left_clause in left_cnf:
                for right_clause in right_cnf:
                    result.append(left_clause.union(right_clause))
            return result
        return []

    def find_pure_symbol(self, clauses: List[Set[Tuple[str, bool]]], symbols: Set[str], 
                        assignment: Dict[str, bool]) -> Optional[Tuple[str, bool]]:
        """Find a pure symbol and its preferred value"""
        for symbol in symbols:
            if symbol in assignment:
                continue
            found_pos = found_neg = False
            for clause in clauses:
                for lit, val in clause:
                    if lit == symbol:
                        if val:
                            found_pos = True
                        else:
                            found_neg = True
            if found_pos != found_neg:
                return (symbol, found_pos)
        return None

    def find_unit_clause(self, clauses: List[Set[Tuple[str, bool]]], 
                        assignment: Dict[str, bool]) -> Optional[Tuple[str, bool]]:
        """Find a unit clause and its literal"""
        for clause in clauses:
            unassigned = set()
            for lit, val in clause:
                if lit not in assignment:
                    if len(unassigned) == 0 or (lit, val) in unassigned:
                        unassigned.add((lit, val))
            if len(unassigned) == 1:
                lit, val = unassigned.pop()
                return (lit, val)
        return None

    def dpll_satisfiable(self, clauses: List[Set[Tuple[str, bool]]], symbols: Set[str], 
                        assignment: Dict[str, bool]) -> Optional[Dict[str, bool]]:
        """DPLL algorithm implementation"""
        # All clauses are satisfied
        if not clauses:
            return assignment
        # Empty clause (unsatisfiable)
        if any(not clause for clause in clauses):
            return None

        # Unit propagation
        unit = self.find_unit_clause(clauses, assignment)
        if unit:
            symbol, value = unit
            new_assignment = assignment.copy()
            new_assignment[symbol] = value
            new_clauses = [c for c in clauses if (symbol, value) not in c]
            new_clauses = [c - {(symbol, not value)} for c in new_clauses]
            return self.dpll_satisfiable(new_clauses, symbols - {symbol}, new_assignment)

        # Pure symbol elimination
        pure = self.find_pure_symbol(clauses, symbols, assignment)
        if pure:
            symbol, value = pure
            new_assignment = assignment.copy()
            new_assignment[symbol] = value
            new_clauses = [c for c in clauses if (symbol, not value) not in c]
            return self.dpll_satisfiable(new_clauses, symbols - {symbol}, new_assignment)

        # Choose a symbol
        symbol = next(iter(symbols - set(assignment.keys())))
        # Try with True
        new_assignment = assignment.copy()
        new_assignment[symbol] = True
        result = self.dpll_satisfiable(
            [c for c in clauses if (symbol, True) not in c],
            symbols - {symbol},
            new_assignment
        )
        if result is not None:
            return result
        # Try with False
        new_assignment[symbol] = False
        return self.dpll_satisfiable(
            [c for c in clauses if (symbol, False) not in c],
            symbols - {symbol},
            new_assignment
        )

    def solve(self) -> str:
        """Solve the entailment problem using DPLL and return result string"""
        # Check if KB ∧ ¬query is unsatisfiable
        kb_and_not_query = Conjunction(self.knowledge_base, Negation(self.query))
        cnf_clauses = self.to_cnf(kb_and_not_query)
        
        # If DPLL returns None (unsatisfiable), then KB ⊨ query
        result = self.dpll_satisfiable(cnf_clauses, self.symbols, {}) is None
        return "YES" if result else "NO"